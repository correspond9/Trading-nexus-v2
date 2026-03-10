import Image from "next/image";
import Link from "next/link";

export default function TradingRules() {
  return (
    <div className="max-w-6xl mx-auto px-6 py-12">

      {/* NAVBAR */}

      <nav className="neo-card flex justify-between items-center p-4 mb-12">

        <div className="flex items-center gap-3">

          <Image
            src="/logo.png"
            alt="TradingNexus"
            width={40}
            height={40}
          />

          <span className="font-bold text-lg">
            TradingNexus
          </span>

        </div>

        <div className="flex gap-6 text-sm font-medium">

          <Link href="/">Home</Link>
          <Link href="/funded">Funded Program</Link>
          <Link href="/trading-rules">Trading Rules</Link>

          <Link
            href="/register"
            className="neo-btn-solid-purple px-4 py-2"
          >
            Sign Up
          </Link>

        </div>

      </nav>

      {/* HEADER */}

      <section className="neo-card text-center p-12">

        <h1 className="text-4xl font-bold mb-4">
          Trading Rules & Risk Framework
        </h1>

        <p className="max-w-2xl mx-auto text-lg text-[var(--neo-text-muted)]">

          TradingNexus provides additional trading capital to traders while
          maintaining strict risk controls to ensure stability of the system.

          The following framework governs how funded trading accounts operate.

        </p>

      </section>

      {/* FUNDING MODEL */}

      <section className="neo-card p-10 mt-12">

        <h2 className="text-2xl font-bold mb-6">
          Capital Allocation Model
        </h2>

        <p className="text-[var(--neo-text-muted)] mb-6">

          TradingNexus enables traders to trade with higher capital by
          allocating additional funds to their account.

        </p>

        <div className="grid md:grid-cols-3 gap-6">

          <div className="neo-dug p-6 text-center">

            <h4 className="font-semibold mb-2">
              Trader Deposit
            </h4>

            <p className="text-xl font-bold">
              ₹1,00,000
            </p>

          </div>

          <div className="neo-dug p-6 text-center">

            <h4 className="font-semibold mb-2">
              TradingNexus Capital
            </h4>

            <p className="text-xl font-bold">
              ₹4,00,000
            </p>

          </div>

          <div className="neo-dug p-6 text-center">

            <h4 className="font-semibold mb-2">
              Total Trading Capital
            </h4>

            <p className="text-xl font-bold text-gradient">
              ₹5,00,000
            </p>

          </div>

        </div>

      </section>

      {/* RMS */}

      <section className="neo-card p-10 mt-12">

        <h2 className="text-2xl font-bold mb-6">
          Risk Monitoring (RMS)
        </h2>

        <p className="text-[var(--neo-text-muted)]">

          TradingNexus maintains a dedicated Risk Management System (RMS)
          team that continuously monitors trading activity. The objective of
          RMS monitoring is to maintain trading discipline and ensure that
          risk exposure remains within acceptable limits.

        </p>

      </section>

      {/* STOP LOSS */}

      <section className="neo-card p-10 mt-12">

        <h2 className="text-2xl font-bold mb-6">
          Maximum Loss Protection
        </h2>

        <p className="text-[var(--neo-text-muted)]">

          A strict system-level stop loss is enforced to protect trading
          capital. If the mark-to-market (MTM) loss on live positions reaches
          <b> 50% of the trader's base capital</b>, positions may be
          automatically squared off by the system.

        </p>

      </section>

      {/* CAPITAL STABILITY */}

      <section className="neo-card p-10 mt-12">

        <h2 className="text-2xl font-bold mb-6">
          Capital Stability During the Month
        </h2>

        <p className="text-[var(--neo-text-muted)]">

          Once capital allocation is provided at the beginning of the month,
          it will not be reduced during the same month even if losses occur.

          Adjustments, if any, are applied only during the settlement cycle.

        </p>

      </section>

      {/* SETTLEMENT */}

      <section className="neo-card p-10 mt-12">

        <h2 className="text-2xl font-bold mb-6">
          Monthly Settlement
        </h2>

        <p className="text-[var(--neo-text-muted)]">

          Final settlement of profits and losses for funded trading accounts
          is calculated on the <b>last Thursday of every month.</b>

          Withdrawals between settlement cycles are not permitted.

        </p>

      </section>

      {/* PROFIT POLICY */}

      <section className="neo-card p-10 mt-12">

        <h2 className="text-2xl font-bold mb-6">
          Profit Policy
        </h2>

        <p className="text-[var(--neo-text-muted)]">

          TradingNexus does not operate on a profit sharing model.

          Traders retain the profits generated through their trading
          activities.

        </p>

      </section>

      {/* PLATFORM CHARGES */}

      <section className="neo-card p-10 mt-12">

        <h2 className="text-2xl font-bold mb-6">
          Platform Charges
        </h2>

        <p className="text-[var(--neo-text-muted)]">

          TradingNexus charges a platform fee of
          <b> 0.005 × turnover</b> for facilitating trading on the system.

        </p>

        <p className="text-[var(--neo-text-muted)] mt-4">

          If no trading activity occurs during a month, no platform
          charges are applied.

        </p>

      </section>

      {/* CTA */}

      <section className="neo-card text-center p-12 mt-16">

        <h2 className="text-2xl font-bold mb-4">
          Start Trading With Higher Capital
        </h2>

        <Link
          href="/funded"
          className="neo-btn-solid-green px-8 py-3"
        >
          View Funded Program
        </Link>

      </section>

    </div>
  );
}
