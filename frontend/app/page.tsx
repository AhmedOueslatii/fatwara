import Link from "next/link";
import { Button } from "@/components/ui/button";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white text-slate-900">
      <SiteHeader />

      <Hero />
      <TrustBadges />
      <Features />
      <HowItWorks />
      <Pricing />
      <Faq />
      <CtaBanner />

      <SiteFooter />
    </div>
  );
}

/* ---------- Hero ---------- */

function Hero() {
  return (
    <section className="relative overflow-hidden">
      <div className="absolute inset-0 bg-hero-radial" aria-hidden />
      <div className="absolute inset-0 grid-pattern opacity-60" aria-hidden />

      <div className="relative mx-auto max-w-6xl px-6 py-24 md:py-32">
        <div className="mx-auto max-w-3xl text-center animate-fade-up">
          <span className="inline-flex items-center gap-2 rounded-full border border-brand-200 bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700">
            <span className="h-1.5 w-1.5 rounded-full bg-brand-500" />
            Conformite TEIF 1.8.7 - DGI Tunisie
          </span>

          <h1 className="mt-6 text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl md:text-6xl">
            Vos factures electroniques,{" "}
            <span className="text-gradient-brand">signees et soumises</span> en
            60 secondes.
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-600">
            Fatwara genere vos factures TEIF, les signe avec votre certificat
            ANCE et les transmet automatiquement a la TTN. Concu pour les
            medecins, avocats, comptables et consultants tunisiens.
          </p>

          <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link href="/auth/register">
              <Button size="lg">Commencer gratuitement</Button>
            </Link>
            <a href="#how">
              <Button variant="outline" size="lg">
                Voir comment ca marche
              </Button>
            </a>
          </div>

          <p className="mt-4 text-xs text-slate-500">
            Aucune carte bancaire requise - 30 jours d&apos;essai - Hebergement
            100% tunisien
          </p>
        </div>

        <HeroPreview />
      </div>
    </section>
  );
}

function HeroPreview() {
  return (
    <div className="mx-auto mt-16 max-w-4xl animate-fade-up">
      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-glow">
        <div className="flex items-center gap-2 border-b border-slate-200 bg-slate-50 px-4 py-3">
          <div className="flex gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-red-400" />
            <span className="h-2.5 w-2.5 rounded-full bg-amber-400" />
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" />
          </div>
          <span className="ml-3 text-xs font-mono text-slate-500">
            fatwara.tn / dashboard / invoices / FACT-2026-0042
          </span>
        </div>

        <div className="grid grid-cols-1 divide-slate-200 md:grid-cols-3 md:divide-x">
          <div className="p-5">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Statut
            </div>
            <div className="mt-2 inline-flex items-center gap-2 rounded-full bg-emerald-100 px-3 py-1 text-sm font-semibold text-emerald-800">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
              Acceptee TTN
            </div>
            <div className="mt-4 text-xs text-slate-500">Reference TTN</div>
            <div className="font-mono text-sm text-slate-800">
              TTN-2026-A8F3C12
            </div>
          </div>
          <div className="p-5">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Total TTC
            </div>
            <div className="mt-2 text-2xl font-bold text-slate-900">
              1 247,500 <span className="text-base font-medium">TND</span>
            </div>
            <div className="mt-4 grid grid-cols-2 text-xs">
              <div>
                <div className="text-slate-500">HT</div>
                <div className="font-semibold text-slate-700">1 048,319</div>
              </div>
              <div>
                <div className="text-slate-500">TVA 19%</div>
                <div className="font-semibold text-slate-700">199,181</div>
              </div>
            </div>
          </div>
          <div className="p-5">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Signature
            </div>
            <div className="mt-2 text-sm font-semibold text-slate-800">
              XAdES-B
            </div>
            <div className="mt-1 text-xs text-slate-500">RSA-SHA256</div>
            <div className="mt-4 text-xs text-slate-500">Certificat</div>
            <div className="text-xs font-medium text-slate-700">
              ANCE / TunTrust
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ---------- Trust badges ---------- */

function TrustBadges() {
  const badges = [
    { label: "TEIF 1.8.7", caption: "Format DGI" },
    { label: "XAdES-B", caption: "Signature ETSI" },
    { label: "ANCE", caption: "Autorite certif." },
    { label: "TunTrust", caption: "PKI tunisienne" },
    { label: "TTN", caption: "Tunisie TradeNet" },
    { label: "DGI", caption: "Direction generale impots" },
  ];
  return (
    <section className="border-y border-slate-200 bg-slate-50/50">
      <div className="mx-auto max-w-6xl px-6 py-10">
        <p className="text-center text-xs font-semibold uppercase tracking-widest text-slate-500">
          Conforme aux standards officiels
        </p>
        <div className="mt-6 grid grid-cols-3 gap-4 md:grid-cols-6">
          {badges.map((b) => (
            <div
              key={b.label}
              className="flex flex-col items-center justify-center rounded-lg border border-slate-200 bg-white px-3 py-4 text-center"
            >
              <div className="text-sm font-bold text-slate-800">{b.label}</div>
              <div className="mt-0.5 text-[10px] uppercase tracking-wide text-slate-500">
                {b.caption}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ---------- Features ---------- */

function Features() {
  const features = [
    {
      icon: "📄",
      title: "Generation TEIF 1.8.7",
      body: "Saisie simple, XML conforme genere automatiquement, valide contre le schema XSD officiel de la DGI.",
    },
    {
      icon: "🔐",
      title: "Signature XAdES-B",
      body: "Importez votre certificat ANCE (.p12) une fois. Chaque facture est signee avec la chaine de confiance TunTrust.",
    },
    {
      icon: "📡",
      title: "Soumission TTN",
      body: "Transmission directe a Tunisie TradeNet. Reference de soumission renvoyee en quelques secondes.",
    },
    {
      icon: "🇹🇳",
      title: "Hebergement tunisien",
      body: "Vos donnees fiscales restent sur des serveurs en Tunisie. Conservation legale 10 ans assuree.",
    },
    {
      icon: "⚡",
      title: "Pipeline automatise",
      body: "De la saisie a la reference TTN en moins d'une minute. Suivi du statut en temps reel.",
    },
    {
      icon: "🛡️",
      title: "Audit complet",
      body: "Chaque action (upload, signature, soumission) est tracee. Exportable pour vos controles fiscaux.",
    },
  ];
  return (
    <section id="features" className="py-24">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            Tout ce qu&apos;il vous faut pour facturer en regle
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            Conformite totale avec la reglementation TEIF, sans effort technique.
          </p>
        </div>

        <div className="mt-14 grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
          {features.map((f) => (
            <div
              key={f.title}
              className="group rounded-xl border border-slate-200 bg-white p-6 transition-all hover:-translate-y-1 hover:border-brand-200 hover:shadow-soft"
            >
              <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-brand-50 text-2xl">
                {f.icon}
              </div>
              <h3 className="mt-4 text-base font-semibold text-slate-900">
                {f.title}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">
                {f.body}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ---------- How it works ---------- */

function HowItWorks() {
  const steps = [
    {
      n: "01",
      title: "Importez votre certificat ANCE",
      body: "Une seule fois. Votre fichier .p12 est stocke chiffre, le mot de passe n'est jamais conserve.",
    },
    {
      n: "02",
      title: "Saisissez la facture",
      body: "Fournisseur, client, lignes, TVA. Calculs automatiques au millime pres.",
    },
    {
      n: "03",
      title: "Recevez la reference TTN",
      body: "Generation TEIF, signature XAdES-B, soumission TTN. Tout enchaine en arriere-plan.",
    },
  ];
  return (
    <section id="how" className="border-y border-slate-200 bg-slate-50 py-24">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            Trois etapes, moins d&apos;une minute
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            Du formulaire a la reference TTN, sans toucher au XML.
          </p>
        </div>

        <div className="mt-14 grid grid-cols-1 gap-6 md:grid-cols-3">
          {steps.map((s, i) => (
            <div key={s.n} className="relative">
              <div className="flex h-full flex-col rounded-xl border border-slate-200 bg-white p-6">
                <div className="text-sm font-bold text-brand-600">{s.n}</div>
                <h3 className="mt-3 text-lg font-semibold text-slate-900">
                  {s.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">
                  {s.body}
                </p>
              </div>
              {i < steps.length - 1 && (
                <div
                  className="absolute right-[-14px] top-1/2 hidden h-7 w-7 -translate-y-1/2 items-center justify-center rounded-full border border-slate-200 bg-white text-brand-600 md:flex"
                  aria-hidden
                >
                  →
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ---------- Pricing ---------- */

function Pricing() {
  const plans = [
    {
      name: "Solo",
      price: "49",
      tagline: "Pour le professionnel independant.",
      featured: false,
      features: [
        "Jusqu'a 30 factures / mois",
        "1 certificat ANCE",
        "Soumission TTN automatique",
        "Conservation 10 ans",
        "Support email",
      ],
    },
    {
      name: "Cabinet",
      price: "149",
      tagline: "Pour le cabinet en croissance.",
      featured: true,
      features: [
        "Jusqu'a 200 factures / mois",
        "1 certificat ANCE",
        "Export comptable mensuel",
        "Audit log telechargeable",
        "Support prioritaire",
        "30 jours d'essai",
      ],
    },
    {
      name: "Pro",
      price: "299",
      tagline: "Volume eleve, multi-utilisateurs.",
      featured: false,
      features: [
        "Factures illimitees",
        "Multi-utilisateurs (5 sieges)",
        "API d'integration",
        "SLA 99,5%",
        "Support telephonique",
        "Onboarding dedie",
      ],
    },
  ];
  return (
    <section id="pricing" className="py-24">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            Tarifs simples, sans surprise
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            Prix mensuel HT en TND. Resiliable a tout moment.
          </p>
        </div>

        <div className="mt-14 grid grid-cols-1 gap-6 md:grid-cols-3">
          {plans.map((p) => (
            <div
              key={p.name}
              className={
                "relative flex flex-col rounded-xl border bg-white p-6 " +
                (p.featured
                  ? "border-brand-500 shadow-glow ring-2 ring-brand-500/20"
                  : "border-slate-200")
              }
            >
              {p.featured && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-brand-gradient px-3 py-1 text-xs font-semibold text-white shadow-soft">
                  Le plus populaire
                </span>
              )}
              <h3 className="text-lg font-semibold text-slate-900">{p.name}</h3>
              <p className="mt-1 text-sm text-slate-600">{p.tagline}</p>
              <div className="mt-5 flex items-baseline gap-1">
                <span className="text-4xl font-extrabold text-slate-900">
                  {p.price}
                </span>
                <span className="text-sm font-medium text-slate-500">
                  TND / mois
                </span>
              </div>

              <ul className="mt-6 flex-1 space-y-3 text-sm text-slate-700">
                {p.features.map((f) => (
                  <li key={f} className="flex items-start gap-2">
                    <span className="mt-0.5 inline-flex h-4 w-4 flex-shrink-0 items-center justify-center rounded-full bg-brand-100 text-[10px] font-bold text-brand-700">
                      ✓
                    </span>
                    {f}
                  </li>
                ))}
              </ul>

              <Link href="/auth/register" className="mt-7">
                <Button
                  variant={p.featured ? "primary" : "outline"}
                  className="w-full"
                >
                  Commencer
                </Button>
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ---------- FAQ ---------- */

function Faq() {
  const items = [
    {
      q: "Ai-je besoin d'un certificat ANCE pour utiliser Fatwara ?",
      a: "Oui. La signature XAdES-B requiert un certificat emis par l'ANCE (TunTrust). Vous l'importez une fois lors de l'onboarding au format .p12.",
    },
    {
      q: "Mes donnees fiscales sortent-elles de Tunisie ?",
      a: "Non. Toute la stack (base de donnees, stockage des certificats, sauvegardes) est hebergee sur des serveurs en Tunisie. C'est une exigence reglementaire que nous respectons strictement.",
    },
    {
      q: "Que se passe-t-il si la TTN refuse ma facture ?",
      a: "Le statut passe a 'Rejetee TTN' avec le motif renvoye par la plateforme. Vous pouvez corriger les donnees et resoumettre - chaque tentative est tracee dans l'audit log.",
    },
    {
      q: "Puis-je tester Fatwara sans matricule fiscal ?",
      a: "Oui. Le mode bac-a-sable utilise un environnement TTN simule, ideal pour valider votre flux avant la mise en production.",
    },
    {
      q: "Combien de temps mes factures sont-elles conservees ?",
      a: "10 ans, conformement a l'article 62 du Code des droits et procedures fiscaux tunisien. Toutes les versions (XML, signe) sont retrouvables.",
    },
    {
      q: "Comment fonctionne le mot de passe du certificat ?",
      a: "Il est demande a chaque signature et n'est jamais stocke en base. Cela garantit qu'aucune compromise serveur ne peut conduire a des signatures non autorisees.",
    },
  ];
  return (
    <section id="faq" className="border-y border-slate-200 bg-slate-50 py-24">
      <div className="mx-auto max-w-3xl px-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            Questions frequentes
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            Tout ce que vous devez savoir avant de commencer.
          </p>
        </div>

        <div className="mt-12 space-y-3">
          {items.map((item) => (
            <details
              key={item.q}
              className="group rounded-lg border border-slate-200 bg-white p-5 open:shadow-soft"
            >
              <summary className="flex cursor-pointer items-center justify-between text-sm font-semibold text-slate-900">
                {item.q}
                <span className="ml-4 text-brand-600 transition-transform group-open:rotate-45">
                  +
                </span>
              </summary>
              <p className="mt-3 text-sm leading-relaxed text-slate-600">
                {item.a}
              </p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ---------- CTA banner ---------- */

function CtaBanner() {
  return (
    <section className="py-20">
      <div className="mx-auto max-w-5xl px-6">
        <div className="relative overflow-hidden rounded-2xl bg-brand-gradient px-8 py-12 text-center shadow-glow md:px-16 md:py-16">
          <div className="absolute inset-0 grid-pattern opacity-30" aria-hidden />
          <div className="relative">
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Pret a passer a la facturation electronique ?
            </h2>
            <p className="mx-auto mt-3 max-w-xl text-base text-brand-50/90">
              Creez votre compte en 30 secondes. Importez votre certificat. Emettez
              votre premiere facture conforme aujourd&apos;hui.
            </p>
            <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Link href="/auth/register">
                <Button
                  size="lg"
                  className="!bg-white !text-brand-700 hover:!bg-slate-100"
                >
                  Creer mon compte
                </Button>
              </Link>
              <Link href="/auth/login">
                <Button
                  variant="ghost"
                  size="lg"
                  className="!text-white hover:!bg-white/10"
                >
                  Se connecter
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
