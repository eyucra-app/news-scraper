import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import BackendStatus from "@/components/BackendStatus";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "News Scraper - Professional News Management",
  description: "Sistema profesional de scraping y gestión de noticias con integración a Singular.live",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
          {/* Backend Status Indicator */}
          <BackendStatus />

          {/* Navigation */}
          <nav className="bg-slate-800/50 backdrop-blur-lg border-b border-slate-700">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center h-16">
                <div className="flex items-center space-x-8">
                  <Link href="/" className="flex items-center space-x-3">
                    <span className="text-2xl">📰</span>
                    <span className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
                      News Scraper
                    </span>
                  </Link>
                  <div className="hidden md:flex space-x-4">
                    <Link
                      href="/"
                      className="px-3 py-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-700/50 transition"
                    >
                      Dashboard
                    </Link>
                    <Link
                      href="/sources"
                      className="px-3 py-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-700/50 transition"
                    >
                      Fuentes
                    </Link>
                    <Link
                      href="/headlines"
                      className="px-3 py-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-700/50 transition"
                    >
                      Titulares
                    </Link>
                    <Link
                      href="/ticker"
                      className="px-3 py-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-700/50 transition"
                    >
                      🎬 Ticker
                    </Link>
                    <Link
                      href="/config"
                      className="px-3 py-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-700/50 transition"
                    >
                      ⚙️ Config
                    </Link>
                    <a
                      href="http://localhost:8000/docs"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-3 py-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-700/50 transition"
                    >
                      API Docs
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </nav>

          {/* Main Content */}
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
