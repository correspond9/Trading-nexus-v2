// app/page.tsx
"use client";

import {
  LineChart,
  ShieldCheck,
  Users,
  Clock,
  Brain,
  Sparkles,
  CheckCircle2,
  PlayCircle,
  BadgeCheck,
  ArrowDownCircle,
  ChevronRight,
  TrendingUp,
  Activity,
  Crosshair
} from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    <main className="relative mx-auto flex min-h-screen max-w-6xl flex-col gap-24 px-4 pb-20 pt-10 md:px-8 md:pt-16 lg:pt-20">

      {/* ── Navigation ──────────────────────────────────── */}
      <nav className="neo-card px-8 py-5 flex items-center justify-between gap-4 relative z-50">
        <Link href="/" className="group transition-transform hover:-translate-y-1">
          {/* Logo container allows any logo.png placed in the public folder to display naturally */}
          <img src="/logo.png" alt="Trading Nexus" className="h-[120px] md:h-[120px] w-auto max-w-[420px] object-contain drop-shadow-[0_15px_15px_var(--neo-shadow-dark)] animate-float-slow" />
        </Link>
        <div className="hidden flex-1 items-center justify-center gap-10 text-sm font-black text-[var(--neo-text-muted)] sm:flex uppercase tracking-widest">
          <Link href="/about" className="hover:text-[var(--neo-color-purple)] transition-colors">About Mentor</Link>
          <Link href="/course" className="hover:text-[var(--neo-color-green)] transition-colors">Curriculum</Link>
        </div>
        <div className="hidden sm:block">
          <Link href="/register" className="neo-btn neo-btn-purple text-sm px-8 py-4 uppercase">
            Reserve Spot
          </Link>
        </div>
      </nav>

      {/* ── Hero ────────────────────────────────────────── */}
      <section className="grid gap-16 md:grid-cols-[1.2fr_1fr] items-center pt-4">

        {/* Left: Copy */}
        <div className="space-y-10 relative z-10">
          <div className="neo-badge shadow-md border-white">
            <Sparkles className="h-4 w-4 text-[var(--neo-color-pink)]" />
            <span className="text-[var(--neo-color-purple)]">100% Free · Live Trading Crash Course</span>
          </div>

          <div className="space-y-6">
            <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl lg:text-7xl leading-[1.15] text-[var(--neo-text-main)] drop-shadow-sm">
              Learn to trade from a real desk trader —{" "}
              <span className="text-[var(--neo-color-purple)] font-black">100% Free.</span>
            </h1>
            <p className="max-w-xl text-xl leading-relaxed text-[var(--neo-text-muted)] font-bold">
              Forget expensive courses and high-ticket upsells. Join our live crash course where we decode equity and derivatives trading using the exact institutional frameworks we use on our own desk.
            </p>
          </div>

          {/* Trust badges - 3D pill look */}
          <div className="flex flex-wrap items-center gap-5">
            <span className="neo-btn-dug px-6 py-3 text-xs bg-[var(--neo-bg)]">
              <ShieldCheck className="h-5 w-5 text-[var(--neo-color-green)]" />
              NSE / SEBI Certified
            </span>
            <span className="neo-btn-dug px-6 py-3 text-xs">
              <Users className="h-5 w-5 text-[var(--neo-color-blue)]" />
              Beginners &amp; Professionals
            </span>
          </div>

          {/* CTAs */}
          <div className="space-y-8 pt-4">
            <div className="flex flex-wrap items-center gap-6">
              <Link href="/register" className="neo-btn-solid-purple text-lg py-5 px-10">
                <PlayCircle className="h-6 w-6 mr-1" />
                Join Free Crash Course
              </Link>
              <Link href="/course" className="neo-btn neo-btn-green text-lg py-5 px-8">
                <BadgeCheck className="h-6 w-6 mr-1" />
                See Curriculum
              </Link>
            </div>
            <p className="flex items-center gap-2 text-sm font-black uppercase tracking-[0.2em] text-[var(--neo-color-red)] pl-2">
              <ArrowDownCircle className="h-4 w-4" />
              Limited to 100 students
            </p>
          </div>
        </div>

        {/* Right: 3D Graphical Element representing Stock Chart */}
        <div className="relative w-full h-[500px] flex items-center justify-center">
          <img src="/vector_monitor.png" alt="3D Trading Monitor" className="w-[100%] max-w-[550px] object-contain animate-float-slow" />
        </div>
      </section>

      {/* ── Why Free Learning? ───────────────────────────── */}
      <section className="neo-card p-[4rem] relative overflow-hidden mt-10">
        <div className="grid lg:grid-cols-[1.5fr_1fr] gap-16 items-center">
          <div className="space-y-10">
            <div className="flex items-center gap-3">
              <div className="h-28 w-28 flex items-center justify-center -ml-4">
                <img src="/vector_crystal_ball.png" alt="Crystal Ball" className="object-contain w-full h-full animate-float-slow" />
              </div>
              <span className="text-sm font-black uppercase tracking-[0.2em] text-[var(--neo-color-purple)] z-10 relative">Our Philosophy</span>
            </div>

            <h2 className="text-4xl font-extrabold sm:text-5xl text-[var(--neo-text-main)]">
              Why Do We Believe in <br /><span className="text-[var(--neo-color-pink)]">Free Learning?</span>
            </h2>

            <div className="space-y-6 text-lg leading-relaxed text-[var(--neo-text-muted)] font-medium pt-2">
              <p>
                The stock market is an incredibly challenging environment. We believe that professional financial education shouldn&apos;t be locked behind a massive paywall. Too many aspiring traders spend their capital on courses before they ever place their first trade. Our mission is to democratize access to institutional-grade trading frameworks.
              </p>
              <p>
                Throughout our programs, we actively monitor our students. Exceptional candidates who demonstrate consistent emotional control and strategic discipline may be considered for a highly exclusive, merit-based opportunity: the chance to trade alongside our proprietary desk using leveraged firm capital.
              </p>
              <p className="text-sm italic pl-6 py-3 neo-dug border-l-4 border-l-[var(--neo-color-orange)] font-bold bg-[var(--neo-bg)] rounded-2xl text-[var(--neo-color-orange)]">
                This opportunity is at our sole discretion. Our primary obligation is education. Sessions are provided free of charge, with no obligation to recruit or fund.
              </p>
            </div>
          </div>

          <div className="space-y-8 lg:px-10">
            {[
              { title: "Zero Upfront Fees", desc: "Capital should be deployed in the market.", color: "var(--neo-color-green)" },
              { title: "Aligned Interests", desc: "We succeed only when our students build real consistency.", color: "var(--neo-color-blue)" },
              { title: "No Obligation", desc: "You are completely free to learn our full system alone.", color: "var(--neo-color-purple)" }
            ].map((item, idx) => (
              <div key={idx} className="p-8 rounded-[2rem] neo-card flex gap-6 hover:scale-105 transition-all">
                <div className="h-12 w-12 rounded-full flex items-center justify-center shrink-0 neo-dug mt-1 border-2 border-white">
                  <CheckCircle2 className="h-6 w-6" style={{ color: item.color }} />
                </div>
                <div>
                  <p className="text-xl font-black text-[var(--neo-text-main)] mb-2 uppercase tracking-wide" style={{ color: item.color }}>{item.title}</p>
                  <p className="text-sm leading-relaxed text-[var(--neo-text-main)] font-bold">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Curriculum Highlights ────────────────────────── */}
      <section id="what-you-learn" className="space-y-16">
        <div className="text-center space-y-6">
          <h2 className="text-4xl font-extrabold md:text-5xl text-[var(--neo-text-main)]">What you&apos;ll learn</h2>
          <p className="max-w-2xl mx-auto text-xl text-[var(--neo-color-purple)] font-black">
            The exact risk-architecture path from zero to first executed trade.
          </p>
        </div>

        <div className="grid gap-12 md:grid-cols-3">
          {[
            { icon: <img src="/vector_research.png" alt="Research" className="h-40 w-auto animate-float-slow" />, title: "Foundation Mastery", desc: "Stocks, indices, lot sizes, margins.", points: ["Market myths", "Basics of Equity"] },
            { icon: <img src="/vector_brain_bulb.png" alt="Brain Intel" className="h-40 w-auto animate-float-slow" style={{ animationDelay: '1s' }} />, title: "Technical Intel", desc: "Read price action and psychology.", points: ["Support / Resistance", "Volume confirmation"] },
            { icon: <img src="/vector_cert.png" alt="Risk Cert" className="h-40 w-auto animate-float-slow" style={{ animationDelay: '2s' }} />, title: "Risk Architecture", desc: "Survive long enough to grow in capital.", points: ["Position sizing", "Risk-to-Reward"] }
          ].map((card, idx) => (
            <div key={idx} className="neo-card p-12 group flex flex-col items-center text-center">
              <div className="h-48 w-48 flex items-center justify-center mb-6 overflow-visible">
                {card.icon}
              </div>
              <h3 className="text-2xl font-black text-[var(--neo-text-main)] mb-4">{card.title}</h3>
              <p className="text-base leading-relaxed mb-8 text-[var(--neo-text-muted)] font-bold">{card.desc}</p>
              <div className="w-full h-1 neo-dug mb-8 rounded-full"></div>
              <ul className="space-y-5 w-full text-left">
                {card.points.map((p, i) => (
                  <li key={i} className="flex items-center justify-center gap-3 text-sm font-black text-[var(--neo-text-main)] text-center">
                    <CheckCircle2 className="h-5 w-5 shrink-0 text-[var(--neo-color-green)]" />
                    <span>{p}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="text-center pt-8">
          <Link href="/course" className="neo-btn-solid-green inline-flex py-6 px-12 text-lg">
            View Full 5-Module Curriculum <ChevronRight className="h-6 w-6 ml-2" />
          </Link>
        </div>
      </section>

      {/* ── Bottom CTAs ─────────────────────────────────── */}
      <section className="grid gap-10 md:grid-cols-2">
        <Link href="/course" className="neo-card p-12 group flex items-start justify-between">
          <div className="space-y-4">
            <p className="text-sm font-black uppercase tracking-[0.2em] text-[var(--neo-color-blue)]">Detailed Portal</p>
            <h3 className="text-3xl font-black text-[var(--neo-text-main)]">Full Module Roadmap</h3>
            <p className="text-lg text-[var(--neo-text-muted)] font-medium">Explore lesson plans and session timings.</p>
          </div>
          <div className="flex items-center justify-center shrink-0">
            <img src="/vector_laptop.png" alt="Detailed Portal" className="w-[140px] xl:w-[160px] h-auto group-hover:scale-110 transition-transform" />
          </div>
        </Link>

        <Link href="/register" className="neo-card p-12 group flex items-start justify-between border-4 border-[var(--neo-bg)] hover:border-white transition-colors shadow-[0_20px_40px_var(--neo-shadow-dark),_0_0_0_inset_white]">
          <div className="space-y-4">
            <p className="text-sm font-black uppercase tracking-[0.2em] text-[var(--neo-color-red)]">Next Batch</p>
            <h3 className="text-3xl font-black text-[var(--neo-text-main)]">Pre-Register Spot</h3>
            <p className="text-lg text-[var(--neo-text-muted)] font-medium">Live classroom seats are limited to 100 per batch.</p>
          </div>
          <div className="h-16 w-16 rounded-[2rem] neo-btn-solid-purple flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform">
            <Users className="h-8 w-8 text-white" />
          </div>
        </Link>
      </section>

      {/* ── Footer ──────────────────────────────────────── */}
      <footer className="pt-[5rem] space-y-10">
        <div className="neo-divider mx-auto w-full"></div>
        <div className="flex flex-col lg:flex-row items-start justify-between gap-12 pt-6">
          <div className="max-w-3xl">
            <p className="text-sm font-black uppercase tracking-[0.2em] mb-4 text-[var(--neo-color-purple)]">Important Disclaimer</p>
            <p className="text-sm leading-relaxed text-justify text-[var(--neo-text-muted)] font-medium">
              Financio Academy is strictly an educational initiative. We are not SEBI-registered investment advisors, nor do we provide financial, investment, or trading advisory services of any kind. All content, frameworks, case studies, and examples are for educational and informational purposes only and must not be construed as investment advice or recommendations to buy or sell any securities. Trading involves substantial risk of loss. We do not encourage, solicit, or offer advisory services. Past performance is not indicative of future results. Please consult a SEBI-registered financial advisor before making any investment decisions.
            </p>
          </div>
          <div className="flex flex-col gap-6 text-sm font-black uppercase tracking-[0.1em] shrink-0 text-[var(--neo-text-main)]">
            <Link href="/about" className="hover:text-[var(--neo-color-purple)] transition-colors">About Mentor</Link>
            <Link href="/course" className="hover:text-[var(--neo-color-green)] transition-colors">Curriculum</Link>
            <Link href="/funded" className="hover:text-[var(--neo-color-blue)] transition-colors">Funded Program</Link>
            <Link href="/rules" className="hover:text-[var(--neo-color-green)] transition-colors">Trading Rules</Link>
            <Link href="/register" className="hover:text-[var(--neo-color-red)] transition-colors">Register</Link>
          </div>
        </div>
        <div className="text-center text-sm pb-8 font-bold text-[var(--neo-text-muted)] pt-8">
          &copy; {new Date().getFullYear()} Trading Nexus Academy. All rights reserved.
        </div>
      </footer>
    </main>
  );
}
