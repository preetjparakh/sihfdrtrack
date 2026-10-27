import type { Metadata } from "next";
import "./globals.css";
import "./portal-refresh.css";
import "./college-status.css";

export const metadata: Metadata = {
  title: "AICTE | Security Deposit Portal",
  description: "Synthetic AICTE security deposit and FDR management prototype.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
