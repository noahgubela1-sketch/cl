import Link from "next/link";
import { Film, Zap, BarChart3, Smartphone } from "lucide-react";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-film-dark">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-5 border-b border-white/5">
        <div className="flex items-center gap-3">
          <Film className="text-brand-500" size={28} />
          <span className="text-xl font-bold tracking-tight">SceneMind AI</span>
        </div>
        <div className="flex gap-3">
          <Link href="/login" className="btn-ghost">Sign in</Link>
          <Link href="/register" className="btn-primary">Get started free</Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="text-center px-6 pt-24 pb-20">
        <p className="text-brand-500 text-sm font-semibold uppercase tracking-widest mb-4">
          AI-Powered Film Scheduling
        </p>
        <h1 className="text-5xl md:text-7xl font-extrabold leading-tight mb-6 max-w-4xl mx-auto">
          From script to shooting schedule{" "}
          <span className="text-brand-500">in minutes</span>
        </h1>
        <p className="text-white/60 text-xl max-w-2xl mx-auto mb-10">
          SceneMind AI automates your entire pre-production planning and optimizes it in
          real-time on set. Stop spending days on scheduling — focus on making great films.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/register" className="btn-primary text-base px-8 py-3">
            Start for free
          </Link>
          <Link href="/demo" className="btn-ghost text-base px-8 py-3 border border-white/10">
            Watch demo
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="px-8 py-20 max-w-6xl mx-auto grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          {
            icon: <Zap className="text-brand-500" size={24} />,
            title: "AI Scheduling Engine",
            desc: "Upload your script. Get a fully optimized day-by-day shooting schedule automatically.",
          },
          {
            icon: <BarChart3 className="text-film-accent" size={24} />,
            title: "Live Production Monitor",
            desc: "Real-time tracking on set. Automatic re-scheduling when delays happen.",
          },
          {
            icon: <Smartphone className="text-emerald-400" size={24} />,
            title: "Set App",
            desc: "iOS & Android app for 1st AD. Log scene starts, breaks, and wraps in one tap.",
          },
          {
            icon: <Film className="text-amber-400" size={24} />,
            title: "Smart Exports",
            desc: "PDF call sheets, Excel, iCal, and Movie Magic Scheduling compatible exports.",
          },
        ].map((f) => (
          <div key={f.title} className="card hover:border-white/10 transition-colors">
            <div className="mb-4">{f.icon}</div>
            <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
            <p className="text-white/50 text-sm leading-relaxed">{f.desc}</p>
          </div>
        ))}
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 text-center py-8 text-white/30 text-sm">
        © {new Date().getFullYear()} SceneMind AI GmbH. All rights reserved.
      </footer>
    </main>
  );
}
