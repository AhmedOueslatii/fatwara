"""Vision-LLM OCR for invoice photos.

Two providers, same interface (Gemini 2.0 Flash + Mistral Pixtral). The user
uploads a photo of a paper invoice; the LLM extracts structured fields.

Residency note: image bytes are sent to the provider for the duration of one
HTTP call and not persisted by us. Anthropic/Google/Mistral free tiers all do
not train on API data. Source images never enter Postgres or MinIO.
"""

import base64
import json
import logging
from typing import Protocol

import httpx

from app.core.config import settings
from app.models.ocr import ExtractedInvoice

log = logging.getLogger(__name__)


class OcrError(RuntimeError):
    pass


SYSTEM_PROMPT = (
    "You extract structured data from Tunisian paper or PDF invoices. "
    "Return ONLY valid JSON matching the schema. Do not invent data: if a "
    "field is missing, illegible, or uncertain, set it to null. Tunisian "
    "matricule fiscal format is 7 digits + letter + /letter/letter/3 digits "
    "(e.g. 1234567A/P/M/000). Currency defaults to TND. TVA rates in Tunisia "
    "are 0, 7, 13, or 19. Dates must be YYYY-MM-DD."
)

USER_PROMPT = (
    "Extract supplier, customer, invoice_date (YYYY-MM-DD), line items "
    "(description, quantity, unit_price, tva_rate), and currency from this "
    "invoice image. Return JSON ONLY, no prose, matching exactly:\n"
    "{\n"
    '  "supplier": {"name": str|null, "matricule": str|null, "address": '
    '{"street_name": str|null, "city_name": str|null, "postal_zone": '
    'str|null, "country_subentity": str|null}},\n'
    '  "customer": {... same shape ...},\n'
    '  "invoice_date": "YYYY-MM-DD"|null,\n'
    '  "items": [{"description": str|null, "quantity": number|null, '
    '"unit_price": number|null, "tva_rate": number|null}],\n'
    '  "currency": "TND",\n'
    '  "note": str|null\n'
    "}"
)


class OcrClient(Protocol):
    async def extract(self, image_bytes: bytes, mime: str) -> ExtractedInvoice: ...


def _parse_json_response(text: str) -> ExtractedInvoice:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        log.warning("OCR provider returned non-JSON: %s", text[:200])
        raise OcrError(f"Could not parse OCR response as JSON: {exc}") from exc
    try:
        return ExtractedInvoice.model_validate(data)
    except Exception as exc:
        raise OcrError(f"OCR response did not match schema: {exc}") from exc


# ---------- Gemini 2.0 Flash ----------


class GeminiOcrClient:
    """Gemini 2.0 Flash via the public generative-language REST API.

    Free tier: 1500 requests/day, no card required. Endpoint:
    https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent
    """

    BASE = "https://generativelanguage.googleapis.com/v1beta/models"
    MODEL = "gemini-2.0-flash"

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise OcrError("GEMINI_API_KEY is not set")
        self.api_key = api_key

    async def extract(self, image_bytes: bytes, mime: str) -> ExtractedInvoice:
        b64 = base64.b64encode(image_bytes).decode("ascii")
        body = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"inline_data": {"mime_type": mime, "data": b64}},
                        {"text": USER_PROMPT},
                    ],
                }
            ],
            "generationConfig": {
                "temperature": 0,
                "responseMimeType": "application/json",
            },
        }
        url = f"{self.BASE}/{self.MODEL}:generateContent?key={self.api_key}"
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json=body)
        if resp.status_code != 200:
            raise OcrError(f"Gemini error {resp.status_code}: {resp.text[:300]}")
        payload = resp.json()
        try:
            text = payload["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as exc:
            raise OcrError(f"Gemini response malformed: {payload}") from exc
        return _parse_json_response(text)


# ---------- Mistral Pixtral ----------


class MistralOcrClient:
    """Mistral Pixtral via console.mistral.ai. EU-hosted (better residency
    story for a Tunisian fiscal product than US providers).
    """

    URL = "https://api.mistral.ai/v1/chat/completions"
    MODEL = "pixtral-12b-2409"

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise OcrError("MISTRAL_API_KEY is not set")
        self.api_key = api_key

    async def extract(self, image_bytes: bytes, mime: str) -> ExtractedInvoice:
        b64 = base64.b64encode(image_bytes).decode("ascii")
        data_url = f"data:{mime};base64,{b64}"
        body = {
            "model": self.MODEL,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": USER_PROMPT},
                        {"type": "image_url", "image_url": data_url},
                    ],
                },
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(self.URL, json=body, headers=headers)
        if resp.status_code != 200:
            raise OcrError(f"Mistral error {resp.status_code}: {resp.text[:300]}")
        payload = resp.json()
        try:
            text = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise OcrError(f"Mistral response malformed: {payload}") from exc
        return _parse_json_response(text)


# ---------- Factory ----------


def get_ocr_client(provider: str | None = None) -> OcrClient:
    p = (provider or settings.OCR_PROVIDER).lower()
    if p == "gemini":
        return GeminiOcrClient(settings.GEMINI_API_KEY)
    if p == "mistral":
        return MistralOcrClient(settings.MISTRAL_API_KEY)
    raise OcrError(f"Unknown OCR provider: {p}")
