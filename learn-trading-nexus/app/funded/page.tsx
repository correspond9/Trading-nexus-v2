import Image from "next/image";
import Link from "next/link";

export default function FundedProgram() {
  const journey = [
    {
      step: "Step 1",
      title: "Free Crash Course",
      subtitle: "Build your trading foundation",
      description:
        "Join our no-cost crash course designed for practical, market-ready learning.",
      image: "/vector_research.png",
      alt: "Free crash course",
    },
    {
      step: "Step 2",
      title: "Evaluation",
      subtitle: "Skill monitoring + short questionnaire",
      description:
        "We evaluate discipline, risk thinking, and execution quality through guided observation and a concise test.",
      image: "/vector_brain_bulb.png",
      alt: "Evaluation process",
    },
    {
      step: "Step 3",
      title: "400% Capital Allocation",
      subtitle: "Selected traders receive added capital",
      description:
        "Shortlisted traders can receive up to 400% additional capital allocation to trade at a larger scale.",
      image: "/vector_rocket.png",
      alt: "Capital allocation",
    },
    {
      step: "Step 4",
      title: "Trade & Keep Profits",
      subtitle: "No profit-sharing model",
      description:
        "You trade on our platform, keep your trading profits, and only pay a small platform usage fee.",
      image: "/vector_target.png",
      alt: "Trade and keep profits",
    },
  ];

  const highlights = [
    {
      title: "Free Learning Entry",
      text: "Start with our no-cost crash course and practical market drills.",
      image: "/vector_laptop.png",
      alt: "Free learning",
    },
    {
      title: "Risk-Led Selection",
      text: "Selection is based on discipline, consistency, and risk behavior.",
      image: "/vector_scale.png",
      alt: "Risk selection",
    },
    {
      title: "Keep Your Trading Profits",
      text: "No profit-sharing; only a small platform usage fee applies.",
      image: "/vector_cert.png",
      alt: "Keep profits",
    },
  ];

  return (
    <div className="max-w-6xl mx-auto px-6 py-12">
      <nav className="flex items-center justify-between neo-card p-4 mb-12">
        <div className="flex items-center gap-3">
          <Image src="/logo.png" alt="TradingNexus" width={120} height={120} />
          <span className="font-bold text-lg">TradingNexus</span>
        </div>
        <div className="flex gap-6 text-sm font-medium">
          <Link href="/">Home</Link>
          <Link href="/about">About</Link>
          <Link href="/course">Courses</Link>
          <Link href="/funded">Funded Program</Link>

          <Link href="/register" className="neo-btn-solid-purple px-4 py-2">
            Sign Up
          </Link>
        </div>
      </nav>

      <section className="neo-card text-center p-12 relative overflow-hidden">
        <div className="absolute -top-16 -left-10 h-40 w-40 rounded-full bg-[#0a7cff]/15 blur-3xl animate-pulse" />
        <div className="absolute -bottom-16 -right-10 h-48 w-48 rounded-full bg-[#22c55e]/15 blur-3xl animate-pulse" />
        <div className="neo-badge mb-4">Learn -&gt; Get Selected -&gt; Receive Capital -&gt; Trade</div>
        <h1 className="text-4xl font-bold mb-6">
          Zero-Cost Training to <span className="text-gradient">Real Capital Access</span>
        </h1>
        <p className="max-w-2xl mx-auto text-[var(--neo-text-muted)] text-lg">
          We run a practical free crash course, monitor trading skills, conduct
          a short evaluation questionnaire, and select high-potential traders
          for a funded path. Selected participants can receive
          <b> 400% additional capital allocation</b> on top of their pay-in,
          under structured risk controls.
        </p>

        <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/register" className="neo-btn-solid-purple px-6 py-3">
            Sign Up Now
          </Link>
          <Link href="/course" className="neo-btn-solid-green px-6 py-3">
            View Free Course
          </Link>
        </div>

        <div className="grid sm:grid-cols-3 gap-4 mt-10 text-left">
          {highlights.map((item) => (
            <div key={item.title} className="neo-dug p-4">
              <div className="flex items-center gap-3 mb-3">
                <Image
                  src={item.image}
                  alt={item.alt}
                  width={42}
                  height={42}
                  className="animate-float-slow object-contain"
                />
                <h3 className="font-semibold">{item.title}</h3>
              </div>
              <p className="text-sm text-[var(--neo-text-muted)]">{item.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="neo-card p-10 mt-16">
        <h2 className="text-3xl font-bold text-center mb-3">How The Program Works</h2>
        <p className="text-center text-[var(--neo-text-muted)] mb-10 max-w-3xl mx-auto">
          A simple, transparent path: learn with us, clear evaluation, receive
          additional capital support, and trade with professional risk guardrails.
        </p>

        <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-6">
          {journey.map((item, index) => (
            <div key={item.step} className="neo-dug p-6 relative">
              <div className="inline-flex items-center rounded-full bg-[#0a7cff] text-white text-xs font-semibold px-4 py-1 mb-4">
                {item.step}
              </div>

              <div className="flex justify-center mb-4 min-h-[110px] items-center">
                <Image
                  src={item.image}
                  alt={item.alt}
                  width={110}
                  height={110}
                  className="animate-float-slow object-contain"
                />
              </div>

              <h3 className="text-xl font-semibold mb-1">{item.title}</h3>
              <p className="text-sm font-medium text-[#0a7cff] mb-3">{item.subtitle}</p>
              <p className="text-sm text-[var(--neo-text-muted)]">{item.description}</p>

              <div className="mt-4 h-1.5 rounded-full bg-white/60 overflow-hidden">
                <div
                  className="h-full rounded-full bg-[#0a7cff] animate-pulse"
                  style={{ width: `${(index + 1) * 25}%` }}
                />
              </div>

              {index < journey.length - 1 && (
                <div className="hidden xl:flex absolute -right-4 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-[#0a7cff] text-white items-center justify-center text-lg font-bold shadow-lg">
                  &gt;
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      <section className="grid lg:grid-cols-2 gap-6 mt-12">
        <div className="neo-card p-8">
          <h3 className="text-2xl font-bold mb-4">Why Traders Prefer This Model</h3>
          <ul className="space-y-3 text-[var(--neo-text-muted)]">
            <li>1. No profit-sharing requirement from your trading gains.</li>
            <li>2. Only a small platform usage fee is charged.</li>
            <li>3. RMS team actively monitors leveraged risk exposure.</li>
            <li>4. Timely alerts when MTM moves negative beyond policy limits.</li>
            <li>5. Built for serious traders who want scale with structure.</li>
          </ul>
        </div>

        <div className="neo-card p-8">
          <h3 className="text-2xl font-bold mb-4">What We Look For In Selection</h3>
          <ul className="space-y-3 text-[var(--neo-text-muted)]">
            <li>1. Discipline during live market scenarios.</li>
            <li>2. Consistency in decision-making approach.</li>
            <li>3. Respect for risk boundaries and capital protection.</li>
            <li>4. Clear understanding of basic trading concepts.</li>
            <li>5. Strong performance in the short evaluation questionnaire.</li>
          </ul>
        </div>
      </section>

      <section className="neo-card p-8 mt-12">
        <h3 className="text-2xl font-bold text-center mb-8">Visual Capital Journey</h3>
        <div className="grid md:grid-cols-7 gap-4 items-center">
          <div className="md:col-span-2 neo-dug p-5 text-center">
            <Image
              src="/vector_monitor.png"
              alt="Training and evaluation"
              width={120}
              height={120}
              className="mx-auto animate-float-slow"
            />
            <p className="font-semibold mt-2">Learn + Evaluation</p>
          </div>

          <div className="md:col-span-1 text-center text-3xl font-bold text-[#0a7cff] animate-pulse">
            +
          </div>

          <div className="md:col-span-2 neo-dug p-5 text-center">
            <Image
              src="/vector_rocket.png"
              alt="400 percent capital allocation"
              width={120}
              height={120}
              className="mx-auto animate-float-slow"
            />
            <p className="font-semibold mt-2">400% Capital Allocation</p>
          </div>

          <div className="md:col-span-1 text-center text-3xl font-bold text-[#0a7cff] animate-pulse">
            =
          </div>

          <div className="md:col-span-1 neo-dug p-5 text-center">
            <Image
              src="/vector_target.png"
              alt="Trade and keep profits"
              width={100}
              height={100}
              className="mx-auto animate-float-slow"
            />
            <p className="font-semibold mt-2">Trade Bigger</p>
          </div>
        </div>
      </section>

      <section className="neo-card text-center p-12 mt-16">
        <h2 className="text-3xl font-bold mb-4">Start Free. Qualify. Trade Bigger.</h2>
        <p className="text-[var(--neo-text-muted)] mb-7 max-w-2xl mx-auto">
          Seats are limited for each batch. Join the free crash course and begin
          your path toward funded capital access.
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Link href="/register" className="neo-btn-solid-green px-8 py-3">
            Secure Your Seat
          </Link>
          <Link href="/course" className="neo-btn-solid-purple px-8 py-3">
            Explore Course Curriculum
          </Link>
        </div>
      </section>
    </div>
  );
}