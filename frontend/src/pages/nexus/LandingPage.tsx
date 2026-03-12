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
    Crosshair,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import '../../styles/nexus/NeoTheme.css';

interface LandingPageProps {
    toggleTheme?: () => void;
    theme?: string;
}

const LandingPage: React.FC<LandingPageProps> = () => {
    return (
        <main className="relative mx-auto flex min-h-screen max-w-6xl flex-col gap-24 px-4 pb-20 pt-10 md:px-8 md:pt-16 lg:pt-20">
            <nav className="neo-card relative z-50 flex items-center justify-between gap-4 px-8 py-5">
                <Link to="/" className="group transition-transform hover:-translate-y-1">
                    <img src="/logo.png" alt="Trading Nexus" className="h-[120px] w-auto max-w-[420px] animate-float-slow object-contain drop-shadow-[0_15px_15px_var(--neo-shadow-dark)] md:h-[120px]" />
                </Link>
                <div className="hidden flex-1 items-center justify-center gap-10 text-sm font-black uppercase tracking-widest text-[var(--neo-text-muted)] sm:flex">
                    <Link to="/about" className="transition-colors hover:text-[var(--neo-color-purple)]">About Mentor</Link>
                    <Link to="/course" className="transition-colors hover:text-[var(--neo-color-green)]">Curriculum</Link>
                </div>
                <div className="hidden sm:block">
                    <Link to="/register" className="neo-btn neo-btn-purple px-8 py-4 text-sm uppercase">
                        Reserve Spot
                    </Link>
                </div>
            </nav>

            <section className="grid items-center gap-16 pt-4 md:grid-cols-[1.2fr_1fr]">
                <div className="relative z-10 space-y-10">
                    <div className="neo-badge border-white shadow-md">
                        <Sparkles className="h-4 w-4 text-[var(--neo-color-pink)]" />
                        <span className="text-[var(--neo-color-purple)]">100% Free · Live Trading Crash Course</span>
                    </div>

                    <div className="space-y-6">
                        <h1 className="text-4xl font-extrabold leading-[1.15] tracking-tight text-[var(--neo-text-main)] drop-shadow-sm sm:text-5xl lg:text-7xl">
                            Learn to trade from a real desk trader -{' '}
                            <span className="font-black text-[var(--neo-color-purple)]">100% Free.</span>
                        </h1>
                        <p className="max-w-xl text-xl font-bold leading-relaxed text-[var(--neo-text-muted)]">
                            Forget expensive courses and high-ticket upsells. Join our live crash course where we decode equity and derivatives trading using the exact institutional frameworks we use on our own desk.
                        </p>
                    </div>

                    <div className="flex flex-wrap items-center gap-5">
                        <span className="neo-btn-dug bg-[var(--neo-bg)] px-6 py-3 text-xs">
                            <ShieldCheck className="h-5 w-5 text-[var(--neo-color-green)]" />
                            NSE / SEBI Certified
                        </span>
                        <span className="neo-btn-dug px-6 py-3 text-xs">
                            <Users className="h-5 w-5 text-[var(--neo-color-blue)]" />
                            Beginners &amp; Professionals
                        </span>
                    </div>

                    <div className="space-y-8 pt-4">
                        <div className="flex flex-wrap items-center gap-6">
                            <Link to="/register" className="neo-btn-solid-purple px-10 py-5 text-lg">
                                <PlayCircle className="mr-1 h-6 w-6" />
                                Join Free Crash Course
                            </Link>
                            <Link to="/course" className="neo-btn neo-btn-green px-8 py-5 text-lg">
                                <BadgeCheck className="mr-1 h-6 w-6" />
                                See Curriculum
                            </Link>
                        </div>
                        <p className="flex items-center gap-2 pl-2 text-sm font-black uppercase tracking-[0.2em] text-[var(--neo-color-red)]">
                            <ArrowDownCircle className="h-4 w-4" />
                            Limited to 100 students
                        </p>
                    </div>
                </div>

                <div className="relative flex h-[500px] w-full items-center justify-center">
                    <img src="/vector_monitor.png" alt="3D Trading Monitor" className="h-auto w-[100%] max-w-[550px] animate-float-slow object-contain" />
                </div>
            </section>

            <section className="neo-card relative mt-10 overflow-hidden p-[4rem]">
                <div className="grid items-center gap-16 lg:grid-cols-[1.5fr_1fr]">
                    <div className="space-y-10">
                        <div className="flex items-center gap-3">
                            <div className="-ml-4 flex h-28 w-28 items-center justify-center">
                                <img src="/vector_crystal_ball.png" alt="Crystal Ball" className="h-full w-full animate-float-slow object-contain" />
                            </div>
                            <span className="relative z-10 text-sm font-black uppercase tracking-[0.2em] text-[var(--neo-color-purple)]">Our Philosophy</span>
                        </div>

                        <h2 className="text-4xl font-extrabold text-[var(--neo-text-main)] sm:text-5xl">
                            Why Do We Believe in <br /><span className="text-[var(--neo-color-pink)]">Free Learning?</span>
                        </h2>

                        <div className="space-y-6 pt-2 text-lg font-medium leading-relaxed text-[var(--neo-text-muted)]">
                            <p>
                                The stock market is an incredibly challenging environment. We believe that professional financial education shouldn&apos;t be locked behind a massive paywall. Too many aspiring traders spend their capital on courses before they ever place their first trade. Our mission is to democratize access to institutional-grade trading frameworks.
                            </p>
                            <p>
                                Throughout our programs, we actively monitor our students. Exceptional candidates who demonstrate consistent emotional control and strategic discipline may be considered for a highly exclusive, merit-based opportunity: the chance to trade alongside our proprietary desk using leveraged firm capital.
                            </p>
                            <p className="neo-dug rounded-2xl border-l-4 border-l-[var(--neo-color-orange)] bg-[var(--neo-bg)] py-3 pl-6 text-sm font-bold italic text-[var(--neo-color-orange)]">
                                This opportunity is at our sole discretion. Our primary obligation is education. Sessions are provided free of charge, with no obligation to recruit or fund.
                            </p>
                        </div>
                    </div>

                    <div className="space-y-8 lg:px-10">
                        {[
                            { title: 'Zero Upfront Fees', desc: 'Capital should be deployed in the market.', color: 'var(--neo-color-green)' },
                            { title: 'Aligned Interests', desc: 'We succeed only when our students build real consistency.', color: 'var(--neo-color-blue)' },
                            { title: 'No Obligation', desc: 'You are completely free to learn our full system alone.', color: 'var(--neo-color-purple)' }
                        ].map((item, idx) => (
                            <div key={idx} className="neo-card flex gap-6 rounded-[2rem] p-8 transition-all hover:scale-105">
                                <div className="neo-dug mt-1 flex h-12 w-12 shrink-0 items-center justify-center rounded-full border-2 border-white">
                                    <CheckCircle2 className="h-6 w-6" style={{ color: item.color }} />
                                </div>
                                <div>
                                    <p className="mb-2 text-xl font-black uppercase tracking-wide text-[var(--neo-text-main)]" style={{ color: item.color }}>{item.title}</p>
                                    <p className="text-sm font-bold leading-relaxed text-[var(--neo-text-main)]">{item.desc}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            <section id="what-you-learn" className="space-y-16">
                <div className="space-y-6 text-center">
                    <h2 className="text-4xl font-extrabold text-[var(--neo-text-main)] md:text-5xl">What you&apos;ll learn</h2>
                    <p className="mx-auto max-w-2xl text-xl font-black text-[var(--neo-color-purple)]">
                        The exact risk-architecture path from zero to first executed trade.
                    </p>
                </div>

                <div className="grid gap-12 md:grid-cols-3">
                    {[
                        { icon: <img src="/vector_research.png" alt="Research" className="h-40 w-auto animate-float-slow" />, title: 'Foundation Mastery', desc: 'Stocks, indices, lot sizes, margins.', points: ['Market myths', 'Basics of Equity'] },
                        { icon: <img src="/vector_brain_bulb.png" alt="Brain Intel" className="h-40 w-auto animate-float-slow" style={{ animationDelay: '1s' }} />, title: 'Technical Intel', desc: 'Read price action and psychology.', points: ['Support / Resistance', 'Volume confirmation'] },
                        { icon: <img src="/vector_cert.png" alt="Risk Cert" className="h-40 w-auto animate-float-slow" style={{ animationDelay: '2s' }} />, title: 'Risk Architecture', desc: 'Survive long enough to grow in capital.', points: ['Position sizing', 'Risk-to-Reward'] }
                    ].map((card, idx) => (
                        <div key={idx} className="neo-card group flex flex-col items-center p-12 text-center">
                            <div className="mb-6 flex h-48 w-48 items-center justify-center overflow-visible">
                                {card.icon}
                            </div>
                            <h3 className="mb-4 text-2xl font-black text-[var(--neo-text-main)]">{card.title}</h3>
                            <p className="mb-8 text-base font-bold leading-relaxed text-[var(--neo-text-muted)]">{card.desc}</p>
                            <div className="neo-dug mb-8 h-1 w-full rounded-full"></div>
                            <ul className="w-full space-y-5 text-left">
                                {card.points.map((p, i) => (
                                    <li key={i} className="flex items-center justify-center gap-3 text-center text-sm font-black text-[var(--neo-text-main)]">
                                        <CheckCircle2 className="h-5 w-5 shrink-0 text-[var(--neo-color-green)]" />
                                        <span>{p}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>

                <div className="pt-8 text-center">
                    <Link to="/course" className="neo-btn-solid-green inline-flex px-12 py-6 text-lg">
                        View Full 5-Module Curriculum <ChevronRight className="ml-2 h-6 w-6" />
                    </Link>
                </div>
            </section>

            <section className="grid gap-10 md:grid-cols-2">
                <Link to="/course" className="neo-card group flex items-start justify-between p-12">
                    <div className="space-y-4">
                        <p className="text-sm font-black uppercase tracking-[0.2em] text-[var(--neo-color-blue)]">Detailed Portal</p>
                        <h3 className="text-3xl font-black text-[var(--neo-text-main)]">Full Module Roadmap</h3>
                        <p className="text-lg font-medium text-[var(--neo-text-muted)]">Explore lesson plans and session timings.</p>
                    </div>
                    <div className="flex shrink-0 items-center justify-center">
                        <img src="/vector_laptop.png" alt="Detailed Portal" className="h-auto w-[140px] transition-transform group-hover:scale-110 xl:w-[160px]" />
                    </div>
                </Link>

                <Link to="/register" className="neo-card group flex items-start justify-between border-4 border-[var(--neo-bg)] p-12 shadow-[0_20px_40px_var(--neo-shadow-dark),_0_0_0_inset_white] transition-colors hover:border-white">
                    <div className="space-y-4">
                        <p className="text-sm font-black uppercase tracking-[0.2em] text-[var(--neo-color-red)]">Next Batch</p>
                        <h3 className="text-3xl font-black text-[var(--neo-text-main)]">Pre-Register Spot</h3>
                        <p className="text-lg font-medium text-[var(--neo-text-muted)]">Live classroom seats are limited to 100 per batch.</p>
                    </div>
                    <div className="neo-btn-solid-purple flex h-16 w-16 shrink-0 items-center justify-center rounded-[2rem] transition-transform group-hover:scale-110">
                        <Users className="h-8 w-8 text-white" />
                    </div>
                </Link>
            </section>

            <footer className="space-y-10 pt-[5rem]">
                <div className="neo-divider mx-auto w-full"></div>
                <div className="flex flex-col items-start justify-between gap-12 pt-6 lg:flex-row">
                    <div className="max-w-3xl">
                        <p className="mb-4 text-sm font-black uppercase tracking-[0.2em] text-[var(--neo-color-purple)]">Important Disclaimer</p>
                        <p className="text-justify text-sm font-medium leading-relaxed text-[var(--neo-text-muted)]">
                            Financio Academy is strictly an educational initiative. We are not SEBI-registered investment advisors, nor do we provide financial, investment, or trading advisory services of any kind. All content, frameworks, case studies, and examples are for educational and informational purposes only and must not be construed as investment advice or recommendations to buy or sell any securities. Trading involves substantial risk of loss. We do not encourage, solicit, or offer advisory services. Past performance is not indicative of future results. Please consult a SEBI-registered financial advisor before making any investment decisions.
                        </p>
                    </div>
                    <div className="flex shrink-0 flex-col gap-6 text-sm font-black uppercase tracking-[0.1em] text-[var(--neo-text-main)]">
                        <Link to="/about" className="transition-colors hover:text-[var(--neo-color-purple)]">About Mentor</Link>
                        <Link to="/course" className="transition-colors hover:text-[var(--neo-color-green)]">Curriculum</Link>
                        <Link to="/funded" className="transition-colors hover:text-[var(--neo-color-blue)]">Funded Program</Link>
                        <Link to="/rules" className="transition-colors hover:text-[var(--neo-color-green)]">Trading Rules</Link>
                        <Link to="/register" className="transition-colors hover:text-[var(--neo-color-red)]">Register</Link>
                    </div>
                </div>
                <div className="pb-8 pt-8 text-center text-sm font-bold text-[var(--neo-text-muted)]">
                    &copy; {new Date().getFullYear()} Trading Nexus Academy. All rights reserved.
                </div>
            </footer>
        </main>
    );
};

export default LandingPage;
