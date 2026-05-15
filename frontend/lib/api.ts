import type {
  CertUploadResponse,
  InvoiceCreate,
  InvoiceListItem,
  InvoiceResponse,
  InvoiceStatusResponse,
  OnboardingStatus,
  SystemHealth,
  UserResponse,
} from "./types";

const BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(public status: number, public body: unknown, message: string) {
    super(message);
  }
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    let body: unknown = null;
    try {
      body = await res.json();
    } catch {
      body = await res.text();
    }
    throw new ApiError(res.status, body, `API ${res.status} on ${path}`);
  }
  return res.json() as Promise<T>;
}

async function apiUpload<T>(path: string, form: FormData): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    credentials: "include",
    body: form,
  });
  if (!res.ok) {
    let body: unknown = null;
    try {
      body = await res.json();
    } catch {
      body = await res.text();
    }
    throw new ApiError(res.status, body, `Upload ${res.status} on ${path}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  system: {
    health: () => apiFetch<SystemHealth>("/api/v1/system/health"),
  },
  auth: {
    login: (email: string, password: string) =>
      apiFetch<UserResponse>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }),
    register: (email: string, password: string) =>
      apiFetch<UserResponse>("/api/v1/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }),
    logout: () =>
      fetch(`${BASE}/api/v1/auth/logout`, {
        method: "POST",
        credentials: "include",
      }),
    me: () => apiFetch<UserResponse>("/api/v1/auth/me"),
  },
  invoices: {
    create: (body: InvoiceCreate) =>
      apiFetch<InvoiceResponse>("/api/v1/invoices", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    list: () => apiFetch<InvoiceListItem[]>("/api/v1/invoices"),
    status: (id: string) =>
      apiFetch<InvoiceStatusResponse>(`/api/v1/invoices/${id}/status`),
  },
  onboarding: {
    status: () => apiFetch<OnboardingStatus>("/api/v1/onboarding/status"),
    uploadCert: (file: File, password: string) => {
      const form = new FormData();
      form.append("file", file);
      form.append("password", password);
      return apiUpload<CertUploadResponse>(
        "/api/v1/onboarding/cert/upload",
        form,
      );
    },
  },
};
