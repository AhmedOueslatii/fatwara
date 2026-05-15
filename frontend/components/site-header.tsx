import Link from "next/link";
import { Button } from "@/components/ui/button";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200/70 bg-white/80 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-gradient text-white shadow-soft">
            <span className="text-sm font-bold">F</span>
          </div>
          <span className="text-lg font-bold tracking-tight text-slate-900">
            Fatwara
          </span>
        </Link>

        <nav className="hidden items-center gap-7 text-sm font-medium text-slate-600 md:flex">
          <a href="#features" className="hover:text-slate-900">
            Fonctionnalites
          </a>
          <a href="#how" className="hover:text-slate-900">
            Comment ca marche
          </a>
          <a href="#pricing" className="hover:text-slate-900">
            Tarifs
          </a>
          <a href="#faq" className="hover:text-slate-900">
            FAQ
          </a>
        </nav>

        <div className="flex items-center gap-2">
          <Link href="/auth/login">
            <Button variant="ghost" size="sm">
              Connexion
            </Button>
          </Link>
          <Link href="/auth/register">
            <Button size="sm">Essai gratuit</Button>
          </Link>
        </div>
      </div>
    </header>
  );
}
