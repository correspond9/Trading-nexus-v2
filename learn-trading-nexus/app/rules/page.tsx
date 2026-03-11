import Image from "next/image";
import Link from "next/link";

export default function FundedProgram() {
  return (
    <div className="max-w-6xl mx-auto px-6 py-12">

      {/* NAVBAR */}

      <nav className="flex items-center justify-between neo-card p-4 mb-12">

        <div className="flex items-center gap-3">

          <Image
            src="/logo.png"
            alt="TradingNexus"
            width={120}
            height={120}
          />

          <span className="font-bold text-lg">
            TradingNexus
          </span>

        </div>

        <div className="flex gap-6 text-sm font-medium">

          <Link href="/">Home</Link>
          <Link href="/about">About</Link>
          <Link href="/course">Courses</Link>
          <Link href="/funded">Funded Program</Link>

          <Link
            href="/register"
            className="neo-btn-solid-purple px-4 py-2"
          >
            Sign Up
          </Link>

        </div>

      </nav>

      {/* HERO */}

      <section className="neo-card text-center p-12">

        <div className="neo-badge mb-4">
          Funded Trader Opportunity
        </div>

        <h1 className="text-4xl font-bold mb-6">
          Become a <span className="text-gradient">Funded Trader</span>
        </h1>

        <p className="max-w-2xl mx-auto text-[var(--neo-text-muted)] text-lg">

          TradingNexus is launching a program to discover talented derivatives
          traders across India.

          Participate in our <b>Free 2-Day Derivatives Crash Course</b> where
          we will observe trading discipline, strategy thinking and
          decision-making ability.

          Top performers may receive the opportunity to trade with
          <b> 80% capital provided by TradingNexus.</b>

        </p>

        <div className="mt-8">

          <Link
            href="/register"
            className="neo-btn-solid-purple px-6 py-3"
          >
            Sign Up Now
          </Link>

        </div>

      </section>

      {/* BENEFITS */}

      <section className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mt-12">

        <div className="neo-card p-6 text-center">

          <Image
            src="/vector_monitor.png"
            alt="Course"
            width={60}
            height={60}
            className="mx-auto animate-float-slow mb-4"
          />

          <h3 className="font-semibold mb-2">
            Derivatives Crash Course
          </h3>

          <p className="text-sm text-[var(--neo-text-muted)]">
            A structured 2-day program covering practical futures and options
            trading concepts.
          </p>

        </div>

        <div className="neo-card p-6 text-center">

          <Image
            src="/vector_brain_bulb.png"
            alt="Skill Evaluation"
            width={60}
            height={60}
            className="mx-auto animate-float-slow mb-4"
          />

          <h3 className="font-semibold mb-2">
            Skill Evaluation
          </h3>

          <p className="text-sm text-[var(--neo-text-muted)]">
            Participants will be evaluated through discussions,
            exercises and a short test.
          </p>

        </div>

        <div className="neo-card p-6 text-center">

          <Image
            src="/vector_cert.png"
            alt="Certification"
            width={60}
            height={60}
            className="mx-auto animate-float-slow mb-4"
          />

          <h3 className="font-semibold mb-2">
            Certification
          </h3>

          <p className="text-sm text-[var(--neo-text-muted)]">
            Participants who complete the program successfully will receive
            TradingNexus certification.
          </p>

        </div>

        <div className="neo-card p-6 text-center">

          <Image
            src="/vector_target.png"
            alt="Funding"
            width={60}
            height={60}
            className="mx-auto animate-float-slow mb-4"
          />

          <h3 className="font-semibold mb-2">
            80% Capital Funding
          </h3>

          <p className="text-sm text-[var(--neo-text-muted)]">
            Top candidates may be selected to trade with TradingNexus capital
            under structured risk guidelines.
          </p>

        </div>

      </section>

      {/* PROCESS */}

      <section className="neo-card p-10 mt-16">

        <h2 className="text-2xl font-bold text-center mb-8">
          Selection Process
        </h2>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">

          <div className="neo-dug p-6">

            <h4 className="font-semibold mb-2">Step 1</h4>

            <p className="text-sm text-[var(--neo-text-muted)]">
              Register for the Free Derivatives Crash Course.
            </p>

          </div>

          <div className="neo-dug p-6">

            <h4 className="font-semibold mb-2">Step 2</h4>

            <p className="text-sm text-[var(--neo-text-muted)]">
              Attend the 2-day live training program.
            </p>

          </div>

          <div className="neo-dug p-6">

            <h4 className="font-semibold mb-2">Step 3</h4>

            <p className="text-sm text-[var(--neo-text-muted)]">
              Complete the evaluation test conducted during the program.
            </p>

          </div>

          <div className="neo-dug p-6">

            <h4 className="font-semibold mb-2">Step 4</h4>

            <p className="text-sm text-[var(--neo-text-muted)]">
              Top candidates are shortlisted for TradingNexus funded trading
              opportunities.
            </p>

          </div>

        </div>

      </section>

      {/* CTA */}

      <section className="neo-card text-center p-12 mt-16">

        <h2 className="text-2xl font-bold mb-4">
          Limited Seats Available
        </h2>

        <p className="text-[var(--neo-text-muted)] mb-6">

          Join the upcoming batch of the Free Derivatives Crash Course and
          get the opportunity to become a funded trader.

        </p>

        <Link
          href="/register"
          className="neo-btn-solid-green px-8 py-3"
        >
          Secure Your Seat
        </Link>

      </section>

    </div>
  );
}