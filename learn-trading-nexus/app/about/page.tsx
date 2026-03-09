// app/about/page.tsx
"use client";

import {
    ArrowLeft,
    ShieldCheck,
    Users,
    Briefcase,
    Target,
    BadgeCheck,
    Globe,
    Star,
    CheckCircle2,
    MapPin,
    Mail,
    Phone,
} from "lucide-react";
import Link from "next/link";

export default function AboutPage() {
    return (
        <main className="relative mx-auto flex min-h-screen max-w-6xl flex-col px-4 pb-20 pt-8 md:px-8">
            {/* Navigation */}
            <nav className="flex items-center justify-between mb-16 px-6 py-4 neo-card">
                <Link href="/" className="group transition-transform hover:-translate-y-1">
                    <img src="/logo.png" alt="Trading Nexus" className="h-[80px] md:h-[100px] w-auto max-w-[300px] object-contain drop-shadow-[0_15px_15px_var(--neo-shadow-dark)] animate-float-slow" />
                </Link>
                <Link href="/" className="flex items-center gap-2 text-sm font-bold text-[var(--neo-text-muted)] hover:text-[var(--neo-text-main)] transition-colors">
                    <ArrowLeft className="h-4 w-4" />
                    Back to Home
                </Link>
            </nav>

            <div className="max-w-5xl mx-auto space-y-24">

                {/* ── Hero ─────────────────────────────────────── */}
                <section className="space-y-8 text-center pt-8">
                    <div className="neo-badge mx-auto">
                        <Globe className="h-4 w-4" />
                        <span>Redefining Market Education</span>
                    </div>
                    <h1 className="text-4xl font-extrabold sm:text-6xl text-[var(--neo-text-main)]">
                        Learn from someone who <br />
                        <span className="text-gradient">actually trades</span> for a living.
                    </h1>
                    <p className="text-xl leading-relaxed max-w-3xl mx-auto text-[var(--neo-text-muted)] font-medium">
                        Trading Nexus was founded to strip away the noise and focus on what matters:
                        professional-grade frameworks designed for real market survival.
                    </p>
                    <div className="flex items-center justify-center pt-8">
                        <img src="/vector_target.png" alt="Target" className="h-40 w-auto animate-float-slow drop-shadow-xl" />
                    </div>
                </section>

                {/* ── Mentor Card ──────────────────────────────── */}
                <section className="neo-card p-10 relative overflow-hidden">
                    <div className="grid md:grid-cols-[280px_1fr] gap-10 relative z-10 items-start">

                        {/* LEFT column: avatar + credential badges */}
                        <div className="flex flex-col gap-8">
                            {/* Avatar box (Inset/Dug) */}
                            <div className="relative rounded-3xl neo-dug flex flex-col items-center justify-center p-8 min-h-[220px]">
                                <Briefcase className="h-16 w-16 mb-6 text-[var(--neo-text-accent)]" />
                                <p className="text-2xl font-black text-[var(--neo-text-main)] tracking-tight">THE MENTOR</p>
                                <p className="text-xs font-bold uppercase tracking-widest mt-2 text-[var(--neo-text-muted)]">Certified Prop Trader</p>
                            </div>

                            {/* Credential badge row */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="neo-dug p-4 text-center">
                                    <p className="text-[10px] font-black uppercase tracking-[0.1em] mb-1 text-[var(--neo-text-muted)]">Accredited</p>
                                    <p className="text-sm font-bold text-[var(--neo-text-main)]">NSE Academy</p>
                                </div>
                                <div className="neo-dug p-4 text-center">
                                    <p className="text-[10px] font-black uppercase tracking-[0.1em] mb-1 text-[var(--neo-text-muted)]">Regulatory</p>
                                    <p className="text-sm font-bold text-[var(--neo-text-main)]">SEBI Certified</p>
                                </div>
                            </div>

                            {/* Experience stat */}
                            <div className="neo-floating-cube p-6 text-center rounded-[2rem] bg-white border-2 border-[var(--neo-bg)]">
                                <p className="text-5xl font-black text-[var(--neo-color-green)] mb-2">15+</p>
                                <p className="text-xs font-black uppercase tracking-[0.1em] mt-2 text-[var(--neo-text-muted)]">Years Market Experience</p>
                            </div>              </div>

                        {/* RIGHT column */}
                        <div className="space-y-10 pl-2">
                            <div className="space-y-4">
                                <h2 className="text-3xl font-bold text-[var(--neo-text-main)]">Market-Hardened Experience</h2>
                                <p className="text-base leading-relaxed text-[var(--neo-text-muted)] font-medium">
                                    With over <strong className="text-[var(--neo-text-main)]">15 years of live market experience</strong> as a proprietary desk trader actively managing capital in the Indian markets, our mentor brings real institutional frameworks to the classroom. Unlike theoretical courses, you won&apos;t find complex technical jargon here — only the precise risk-first thinking that professional desks use every single trading day.
                                </p>
                            </div>

                            <div className="neo-divider"></div>

                            <div className="space-y-4">
                                <h3 className="text-xl font-bold text-[var(--neo-text-main)]">Certifications &amp; Credentials</h3>
                                <p className="text-base leading-relaxed text-[var(--neo-text-muted)] font-medium">
                                    Certified by the National Stock Exchange (NSE) and SEBI in Equity, Derivatives, and Technical Analysis. Every framework taught in our sessions is directly backed by these professional accreditations and tested through years of live capital deployment.
                                </p>
                            </div>

                            <div className="grid grid-cols-2 gap-5 pt-4">
                                {[
                                    { icon: ShieldCheck, text: "Risk-First Architecture" },
                                    { icon: Target, text: "Price Action Systems" },
                                    { icon: Users, text: "1,200+ Students Mentored" },
                                    { icon: Star, text: "15+ Years Desk Experience" }
                                ].map((item, idx) => (
                                    <div key={idx} className="flex items-center gap-4">
                                        <div className="h-10 w-10 rounded-xl neo-button flex items-center justify-center shrink-0">
                                            <item.icon className="h-5 w-5 text-[var(--neo-text-accent)]" />
                                        </div>
                                        <span className="text-sm font-bold text-[var(--neo-text-main)]">{item.text}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </section>

                {/* ── Why Free? ────────────────────────────────── */}
                <section className="grid md:grid-cols-2 gap-16 items-start">
                    <div className="space-y-8">
                        <h2 className="text-3xl font-bold text-[var(--neo-text-main)]">Why is this course 100% free?</h2>
                        <p className="text-base leading-relaxed text-[var(--neo-text-muted)] font-medium">
                            Trading Nexus runs on a simple belief: the best traders are made, not bought. Our sessions are fully
                            free to ensure no financial barrier stands between good education and aspiring traders.
                        </p>
                        <div className="space-y-4">
                            {[
                                "No extra charges — same brokerage as opening directly.",
                                "You receive a manual + full hand-holding + priority support.",
                                "You are free to only learn and never open an account with us."
                            ].map((text, i) => (
                                <div key={i} className="flex gap-4 p-5 neo-dug items-center">
                                    <CheckCircle2 className="h-5 w-5 text-indigo-500 shrink-0" />
                                    <p className="text-base font-bold text-[var(--neo-text-main)]">{text}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="neo-card p-12 text-center space-y-8 mt-[4rem]">
                        <div className="h-20 w-20 rounded-2xl mx-auto flex items-center justify-center neo-button mt-[-6rem]">
                            <BadgeCheck className="h-10 w-10 text-purple-500" />
                        </div>
                        <p className="text-lg font-bold text-[var(--neo-text-main)] leading-relaxed">
                            Opening your demat account is <span className="text-[var(--neo-text-accent)]">completely optional.</span> <br />We prioritize genuine education first.
                        </p>
                        <p className="text-sm italic font-medium text-[var(--neo-text-muted)]">
                            *Referral partners receive dedicated trading setup help &amp; lifetime community access.
                        </p>
                        <Link href="/register" className="neo-btn-solid-purple w-full inline-flex justify-center mt-4 text-lg py-5 px-8">
                            Pre-Register for Next Batch
                        </Link>            </div>
                </section>

                {/* ── Contact & Address ────────────────────────── */}
                <section className="neo-card p-12 overflow-hidden">
                    <div className="grid md:grid-cols-2 gap-12">
                        <div className="space-y-8">
                            <h2 className="text-2xl font-bold text-[var(--neo-text-main)]">Contact Us</h2>
                            <p className="text-base text-[var(--neo-text-muted)] font-medium">Reach out to us for any queries, course registrations, or mentor access.</p>

                            <div className="space-y-6 pt-2">
                                <div className="flex items-center gap-5">
                                    <div className="h-12 w-12 rounded-2xl flex items-center justify-center shrink-0 neo-dug">
                                        <Mail className="h-5 w-5 text-blue-500" />
                                    </div>
                                    <div>
                                        <p className="text-[10px] font-black uppercase tracking-widest text-[var(--neo-text-muted)] mb-1">Email</p>
                                        <a href="mailto:info@tradewithstraddly.com" className="text-base font-bold text-[var(--neo-text-main)] hover:text-blue-500 transition-colors">
                                            info@tradewithstraddly.com
                                        </a>
                                    </div>
                                </div>

                                <div className="flex items-center gap-5">
                                    <div className="h-12 w-12 rounded-2xl flex items-center justify-center shrink-0 neo-dug">
                                        <Phone className="h-5 w-5 text-purple-500" />
                                    </div>
                                    <div>
                                        <p className="text-[10px] font-black uppercase tracking-widest text-[var(--neo-text-muted)] mb-1">Call / WhatsApp</p>
                                        <a href="tel:+918928940525" className="text-base font-bold text-[var(--neo-text-main)] hover:text-purple-500 transition-colors">
                                            +91 89289 40525
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-8">
                            <h2 className="text-2xl font-bold text-[var(--neo-text-main)]">Our Office</h2>
                            <div className="flex items-start gap-5">
                                <div className="h-12 w-12 rounded-2xl flex items-center justify-center shrink-0 neo-dug">
                                    <MapPin className="h-5 w-5 text-indigo-500" />
                                </div>
                                <div>
                                    <p className="text-[10px] font-black uppercase tracking-widest text-[var(--neo-text-muted)] mb-2">Address</p>
                                    <p className="text-base font-bold text-[var(--neo-text-main)] leading-relaxed">
                                        13th Floor, Ozone Biz Centre,<br />
                                        1307, Bellasis Rd, Mumbai Central,<br />
                                        Mumbai, Maharashtra 400008
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Footer */}
                <footer className="text-center pt-12 pb-6 space-y-6">
                    <div className="neo-divider mx-auto w-32 mb-8"></div>
                    <p className="text-xs font-bold uppercase tracking-widest text-[var(--neo-text-muted)]">
                        NSE &amp; SEBI Certification Credentials are available upon request.
                    </p>
                    <p className="text-xs leading-relaxed max-w-3xl mx-auto text-[var(--neo-text-muted)] font-medium">
                        Important Disclaimer: All content, frameworks, and examples discussed are for educational and informational purposes only and should not be construed as investment advice or recommendations to buy or sell any securities. Trading and investing in the financial markets involve substantial risk of loss and are not suitable for every individual. We do not encourage, solicit, or offer advisory services.
                    </p>
                </footer>
            </div>
        </main>
    );
}
