import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "SceneMind AI – Intelligent Film Scheduling",
  description:
    "AI-powered production scheduling platform. Turn your script into an optimized shooting schedule in minutes.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans bg-film-dark text-white antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
