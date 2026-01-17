import type { Metadata } from "next";
import "./globals.css";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { Toaster } from "@/components/ui/sonner";
import { ThemeProvider } from "@/components/ThemeProvider";
import { Geist, Geist_Mono } from "next/font/google";

const geistSans = Geist({ subsets: ["latin"], variable: "--font-geist-sans" });
const geistMono = Geist_Mono({ subsets: ["latin"], variable: "--font-geist-mono" });

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "https://flowtab.pro";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "Flowtab.Pro - Automated Browser Prompt Library",
    template: "%s | Flowtab.Pro",
  },
  description:
    "Discover and share automated browser prompts for Comet, Playwright, and Opera Neon.",
  openGraph: {
    type: "website",
    url: siteUrl,
    title: "Flowtab.Pro - Automated Browser Prompt Library",
    description:
      "Discover and share automated browser prompts for Comet, Playwright, and Opera Neon.",
    siteName: "Flowtab.Pro",
  },
  twitter: {
    card: "summary_large_image",
    title: "Flowtab.Pro - Automated Browser Prompt Library",
    description:
      "Discover and share automated browser prompts for Comet, Playwright, and Opera Neon.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} font-sans antialiased min-h-screen bg-background text-foreground flex flex-col`}
      >
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
          <SiteHeader />
          <main className="flex-1 w-full">{children}</main>
          <SiteFooter />
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  );
}
