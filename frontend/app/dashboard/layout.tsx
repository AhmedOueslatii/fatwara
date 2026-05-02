import Link from "next/link";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase-server";
import SignOutButton from "@/components/sign-out-button";

const NAV = [
  { href: "/dashboard", label: "Accueil" },
  { href: "/dashboard/onboarding", label: "Onboarding" },
  { href: "/dashboard/invoices", label: "Factures" },
  { href: "/dashboard/invoices/new", label: "Nouvelle facture" },
];

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) redirect("/auth/login");

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
          <Link href="/dashboard" className="text-lg font-semibold">
            Fatwara
          </Link>
          <nav className="flex items-center gap-4 text-sm">
            {NAV.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="text-slate-600 hover:text-slate-900"
              >
                {item.label}
              </Link>
            ))}
            <span className="hidden text-slate-400 md:inline">
              {user.email}
            </span>
            <SignOutButton />
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
    </div>
  );
}
