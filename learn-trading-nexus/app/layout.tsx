// app/layout.tsx
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Trading Nexus Learn | Premium Trading Crash Course",
  description:
    "Master the markets with elite frameworks from a certified proprietary desk trader. 100% Free Live Crash Course.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className="min-h-screen antialiased overflow-x-hidden bg-neo-bg text-neo-text-main">
        <div className="relative z-10">
          {children}
        </div>
      </body>
    </html>
  );
}
