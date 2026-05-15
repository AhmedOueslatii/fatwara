import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="border-t border-slate-200 bg-slate-50">
      <div className="mx-auto max-w-6xl px-6 py-12">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          <div className="col-span-2">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-gradient text-white shadow-soft">
                <span className="text-sm font-bold">F</span>
              </div>
              <span className="text-lg font-bold tracking-tight text-slate-900">
                Fatwara
              </span>
            </div>
            <p className="mt-3 max-w-sm text-sm text-slate-600">
              Facturation electronique conforme TEIF pour les professionnels
              liberaux en Tunisie. Hebergement 100% tunisien.
            </p>
          </div>

          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Produit
            </h4>
            <ul className="mt-3 space-y-2 text-sm text-slate-600">
              <li>
                <a href="#features" className="hover:text-brand-700">
                  Fonctionnalites
                </a>
              </li>
              <li>
                <a href="#pricing" className="hover:text-brand-700">
                  Tarifs
                </a>
              </li>
              <li>
                <a href="#faq" className="hover:text-brand-700">
                  FAQ
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Compte
            </h4>
            <ul className="mt-3 space-y-2 text-sm text-slate-600">
              <li>
                <Link href="/auth/login" className="hover:text-brand-700">
                  Connexion
                </Link>
              </li>
              <li>
                <Link href="/auth/register" className="hover:text-brand-700">
                  Creer un compte
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-10 flex flex-col items-start justify-between gap-3 border-t border-slate-200 pt-6 text-xs text-slate-500 md:flex-row md:items-center">
          <p>(c) {new Date().getFullYear()} Fatwara. Tous droits reserves.</p>
          <p>Hebergement Tunisie - Donnees fiscales conservees 10 ans.</p>
        </div>
      </div>
    </footer>
  );
}
