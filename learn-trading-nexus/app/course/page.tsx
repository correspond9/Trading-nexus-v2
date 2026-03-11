// app/course/page.tsx
"use client";

import {
  ArrowLeft,
  Lightbulb,
  LineChart,
  Shield,
  Brain,
  Zap,
  BookOpen,
  Users,
  Clock,
  Award,
  ChevronRight,
} from "lucide-react";
import Link from "next/link";

export default function CoursePage() {
  const modules = [
    {
      id: 1,
      title: "Module 1: Introduction to Trading (The Foundation)",
      desc: "Build a solid understanding of what trading really means and the tools you'll use.",
      icon: <img src="/vector_clipboard.png" alt="Clipboard" className="h-14 w-14 object-contain drop-shadow-md group-hover:scale-110 transition-transform" />,
      topics: [
        { name: "1. Basics of Trading", details: "Distinguishing trading (short-term) from investing (long-term). Understanding the goal: profit from price movements." },
        { name: "2. Types of Trading", details: "Defining Scalping (seconds/minutes), Day Trading (intraday), Swing Trading (days/weeks), and Position Trading (weeks/years)." },
        { name: "3. Trading Instruments", details: "Overview of Stocks (equity), Forex (currency pairs), Options (derivative right, not obligation), and Futures (derivative obligation)." }
      ]
    },
    {
      id: 2,
      title: "Module 2: Technical Analysis and Charting",
      desc: "Learn to read charts like a pro and identify high-probability setups.",
      icon: <img src="/vector_monitor.png" alt="Monitor" className="h-14 w-14 object-contain drop-shadow-md group-hover:scale-110 transition-transform" />,
      topics: [
        { name: "1. Introduction to TA", details: "The three pillars: Price discounts everything, price moves in trends, history repeats. Focus on price action over fundamentals." },
        { name: "2. Understanding Charts", details: "Focus on Candlestick Charts (OHLC data). The difference between Bullish (Green) and Bearish (Red) candles." },
        { name: "3. Key Concepts of TA", details: "Identifying Support (floor) and Resistance (ceiling). Drawing Trend Lines and interpreting Volume as a confirmation tool." }
      ]
    },
    {
      id: 3,
      title: "Module 3: Risk Management and Position Sizing",
      desc: "The most critical skill — protecting your capital so you can trade another day.",
      icon: <img src="/vector_scale.png" alt="Risk Scale" className="h-14 w-14 object-contain drop-shadow-md group-hover:scale-110 transition-transform" />,
      topics: [
        { name: "1. Risk Philosophy", details: "The golden rule: Preserve capital first. Never risk more than a small, fixed percentage of the account on any single trade (e.g., 1% to 2%)." },
        { name: "2. Defining Risk", details: "Calculating the Maximum Dollar Risk per trade (Account Size x Risk Percentage)." },
        { name: "3. Implementing the Stop-Loss", details: "Using the Stop-Loss (S/L) order to enforce the maximum loss limit, based on technical chart points." },
        { name: "4. Position Sizing", details: "The critical formula to determine how many shares/contracts to buy: Maximum Dollar Risk / Risk Per Share." }
      ]
    },
    {
      id: 4,
      title: "Module 4: Strategy Development and Psychology",
      desc: "Build a repeatable trading process and master the mental game.",
      icon: <img src="/vector_brain_bulb.png" alt="Brain Intel" className="h-14 w-14 object-contain drop-shadow-md group-hover:scale-110 transition-transform" />,
      topics: [
        { name: "1. Developing a Strategy", details: "Creating an objective Checklist of entry, exit, and management rules. Understanding the concept of a statistical 'Edge'." },
        { name: "2. Risk-to-Reward Ratio", details: "Defining the R:R (Reward ÷ Risk). Understanding why aiming for 1 : 1.5 or 1 : 2 is necessary for long-term profitability, even with losses." },
        { name: "3. Trading Psychology", details: "Identifying and combating common traps like FOMO, Revenge Trading, and moving the Stop-Loss." },
        { name: "4. Trading Journal", details: "The importance of documenting every trade and the associated emotions for performance review and rule reinforcement." }
      ]
    },
    {
      id: 5,
      title: "Module 5: Practical Implementation and Tools",
      desc: "Put it all together — choosing a broker, placing orders, and executing your first trade.",
      icon: <img src="/vector_rocket.png" alt="Execution" className="h-14 w-14 object-contain drop-shadow-md group-hover:scale-110 transition-transform" />,
      topics: [
        { name: "1. Choosing a Broker", details: "Criteria for selection: Regulation, low commissions/spreads, and a reliable Trading Platform." },
        { name: "2. Order Execution", details: "Differentiating between Market Orders (immediate execution) and Limit Orders (execution only at a desired price)." },
        { name: "3. The Trading Workflow", details: "Step-by-step process: Preparation -> Analysis -> Position Sizing -> Order Placement (with S/L & T/P) -> Review." }
      ]
    }
  ];

  return (
    <main className="relative mx-auto min-h-screen max-w-6xl px-4 pb-20 pt-10 md:px-8">
      {/* Navigation */}
      <nav className="flex items-center justify-between mb-16 px-6 py-4 neo-card">
        <Link href="/" className="flex items-center gap-2 group">
          <div className="relative flex items-center justify-center p-1 rounded-xl transition-transform group-hover:scale-105">
            <img src="/logo.png" alt="Trading Nexus" className="h-[120px] md:h-[120px] w-auto max-w-[420px] object-contain drop-shadow-[0_15px_15px_var(--neo-shadow-dark)] animate-float-slow" />
          </div>
        </Link>
        <Link href="/" className="flex items-center gap-2 text-sm font-bold text-[var(--neo-text-muted)] hover:text-[var(--neo-text-main)] transition-colors">
          <ArrowLeft className="h-4 w-4" />
          Back to Home
        </Link>
      </nav>

      <div className="max-w-5xl mx-auto space-y-12">
        {/* Page Header */}
        <header className="space-y-6 text-center">
          <div className="neo-badge mx-auto">
            <BookOpen className="h-4 w-4" />
            <span>5-Module Academy Curriculum</span>
          </div>

          <div className="space-y-3">
            <h1 className="text-4xl font-extrabold sm:text-6xl text-[var(--neo-text-main)]">
              From zero to <span className="text-gradient">first trade</span>
            </h1>
            <p className="max-w-3xl mx-auto text-lg text-[var(--neo-text-muted)] leading-relaxed">
              A practical, immersive journey designed by a proprietary desk trader with NSE & SEBI certifications.
              No fluff, only the frameworks used on professional trading desks.
            </p>
          </div>

          {/* Stats Bar */}
          <div className="flex flex-wrap justify-center gap-4 text-[10px] font-black uppercase tracking-[0.1em] text-[var(--neo-text-main)] pt-4">
            <span className="neo-btn px-6 py-3 flex items-center gap-2">
              <Award className="h-4 w-4 text-[var(--neo-color-blue)]" /> 5 Core Modules
            </span>
            <span className="neo-btn px-6 py-3 flex items-center gap-2">
              <Clock className="h-4 w-4 text-[var(--neo-color-purple)]" /> 15+ topics
            </span>
            <span className="neo-btn px-6 py-3 flex items-center gap-2">
              <Users className="h-4 w-4 text-[var(--neo-color-pink)]" /> Live sessions
            </span>
          </div>
        </header>

        {/* Modules Breakdown */}
        <div className="space-y-10">
          {modules.map((mod) => (
            <div key={mod.id} className="neo-card p-10 group">
              <div className="flex flex-col md:flex-row gap-10 items-start">
                <div className="h-16 w-16 shrink-0 rounded-2xl neo-dug flex items-center justify-center group-hover:-translate-y-1 transition-transform">
                  {mod.icon}
                </div>
                <div className="space-y-6 flex-1">
                  <div className="space-y-2">
                    <h2 className="text-2xl font-black text-[var(--neo-text-main)]">{mod.title}</h2>
                    <p className="text-[var(--neo-text-muted)] text-sm leading-relaxed font-medium">{mod.desc}</p>
                  </div>

                  <div className="grid sm:grid-cols-2 gap-6 pt-4">
                    {mod.topics.map((topic, i) => (
                      <div key={i} className="p-6 rounded-2xl neo-dug group/item hover:bg-black/5 transition-colors">
                        <p className="font-bold text-[var(--neo-text-main)] text-sm mb-2">{topic.name}</p>
                        <p className="text-xs text-[var(--neo-text-muted)] leading-relaxed font-medium">{topic.details}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Final CTA */}
        <section className="neo-card p-12 text-center space-y-8">
          <Award className="h-10 w-10 text-[var(--neo-text-accent)] mx-auto mb-4" />
          <div className="space-y-4 relative">
            <h2 className="text-3xl font-black text-[var(--neo-text-main)]">Ready to Start Your Journey?</h2>
            <p className="max-w-2xl mx-auto text-base text-[var(--neo-text-muted)] font-medium leading-relaxed">
              Join our next live batch. No hidden fees, no upsells — just genuine education from a
              proprietary desk trader with NSE & SEBI certifications.
            </p>
          </div>

          <div className="flex flex-wrap justify-center gap-6 pt-4 relative">
            <Link href="/register" className="neo-btn-solid-green text-lg px-12 py-6 scale-105">
              Apply for Next Batch
              <ChevronRight className="h-6 w-6 ml-2" />
            </Link>
          </div>
          <p className="text-[10px] text-[var(--neo-text-muted)] font-bold uppercase tracking-widest pt-4">
            Lifetime support & community access included
          </p>
        </section>
      </div>
    </main>
  );
}
