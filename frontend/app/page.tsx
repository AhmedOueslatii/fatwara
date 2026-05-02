import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center px-6 py-16">
      <h1 className="text-4xl font-bold tracking-tight">
        Fatwara
      </h1>
      <p className="mt-3 text-lg text-slate-600">
        Facturation electronique conforme TEIF pour les professionnels liberaux
        en Tunisie.
      </p>

      <ul className="mt-8 space-y-2 text-slate-700">
        <li>- Generation TEIF 1.8.7 validee XSD</li>
        <li>- Signature XAdES-B avec votre certificat ANCE</li>
        <li>- Soumission automatique a la TTN</li>
      </ul>

      <div className="mt-10 flex gap-3">
        <Link
          href="/auth/register"
          className="rounded-md bg-brand px-4 py-2 text-sm font-medium text-white hover:opacity-90"
        >
          Creer un compte
        </Link>
        <Link
          href="/auth/login"
          className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Se connecter
        </Link>
      </div>
    </main>
  );
}
