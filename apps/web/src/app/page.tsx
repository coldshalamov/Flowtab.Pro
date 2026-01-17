import { Button } from "@/components/ui/button";
import { PromptCard } from "@/components/PromptCard";
import { fetchPrompts } from "@/lib/api";
import Link from "next/link";
import { ArrowRight, Sparkles } from "lucide-react";
import Image from "next/image";

export default async function Home() {
  const { items: featuredPrompts } = await fetchPrompts({ pageSize: 3 });

  return (
    <div className="flex flex-col min-h-[calc(100vh-4rem)]">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-16 md:py-24 lg:py-32 bg-background flex flex-col items-center justify-center text-center px-4">
        {/* Hero Gradient Background */}
        <div className="absolute inset-0 opacity-40">
          <Image
            src="/images/hero-gradient.png"
            alt=""
            fill
            className="object-cover"
            priority
          />
        </div>

        {/* Abstract Background Elements */}
        <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:60px_60px] pointer-events-none" />
        <div className="absolute top-0 left-1/4 h-96 w-96 bg-primary/20 rounded-full blur-[128px] opacity-30 pointer-events-none" />
        <div className="absolute bottom-0 right-1/4 h-96 w-96 bg-purple-500/20 rounded-full blur-[128px] opacity-30 pointer-events-none" />

        <div className="relative z-10 max-w-4xl space-y-6">
          <div className="inline-flex items-center rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-sm font-medium text-primary backdrop-blur-md mb-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <Sparkles className="mr-2 h-3.5 w-3.5" />
            The Ultimate Browser Automation Library
          </div>

          <h1 className="text-3xl font-extrabold tracking-tight sm:text-5xl md:text-6xl lg:text-7xl bg-clip-text text-transparent bg-gradient-to-r from-white via-primary to-purple-400 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-100">
            Automate the Web with Flowtab
          </h1>

          <p className="max-w-[700px] mx-auto text-base text-muted-foreground md:text-lg lg:text-xl animate-in fade-in slide-in-from-bottom-8 duration-700 delay-200">
            Discover community-crafted prompt recipes for Comet, Playwright, and Opera Neon.
            Supercharge your agents with reliable automation workflows.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-300">
            <Link href="/library">
              <Button
                size="lg"
                className="relative h-12 px-8 text-lg rounded-full shadow-lg shadow-primary/20 hover:shadow-primary/40 transition-all overflow-hidden group"
              >
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Image
                    src="/images/button-gradient.png"
                    alt=""
                    fill
                    className="object-cover mix-blend-overlay"
                  />
                </div>
                <span className="relative z-10 flex items-center">
                  Browse Library <ArrowRight className="ml-2 h-5 w-5" />
                </span>
              </Button>
            </Link>
            <Link href="/submit">
              <Button size="lg" variant="outline" className="h-12 px-8 text-lg rounded-full bg-background/50 backdrop-blur-sm hover:bg-white/5 border-primary/20">
                Submit Recipe
              </Button>
            </Link>
          </div>

          <div className="pt-12 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-500">
            <p className="text-sm text-muted-foreground mb-6 uppercase tracking-wider font-medium">
              Works perfectly with
            </p>
            <div className="flex flex-wrap justify-center gap-8 md:gap-12 items-center opacity-70 grayscale hover:grayscale-0 transition-all duration-500">
              <Link href="https://checkcomet.com" target="_blank" className="hover:opacity-100 transition-opacity">
                <div className="flex items-center gap-2">
                  <Image src="/images/logos/comet.svg" alt="Comet" width={32} height={32} />
                  <span className="font-semibold text-lg">Comet</span>
                </div>
              </Link>
              <Link href="https://www.opera.com/browsers/neon" target="_blank" className="hover:opacity-100 transition-opacity">
                <div className="flex items-center gap-2">
                  <Image src="/images/logos/neon.svg" alt="Opera Neon" width={32} height={32} />
                  <span className="font-semibold text-lg">Neon</span>
                </div>
              </Link>
              <Link href="https://playwright.dev" target="_blank" className="hover:opacity-100 transition-opacity">
                <div className="flex items-center gap-2">
                  <Image src="/images/logos/playwright.svg" alt="Playwright" width={32} height={32} />
                  <span className="font-semibold text-lg">Playwright</span>
                </div>
              </Link>
              <Link href="#" className="hover:opacity-100 transition-opacity">
                <div className="flex items-center gap-2">
                  <Image src="/images/logos/manus.svg" alt="Manus" width={32} height={32} />
                  <span className="font-semibold text-lg">Manus</span>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Section */}
      <section className="container py-12 md:py-24 space-y-12 px-4 max-w-screen-2xl mx-auto">
        <div className="flex items-center justify-between border-b border-border/40 pb-4">
          <h2 className="text-3xl font-bold tracking-tight">Featured Recipes</h2>
          <Link href="/library" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors flex items-center">
            View all <ArrowRight className="ml-1 h-4 w-4" />
          </Link>
        </div>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {featuredPrompts.map(prompt => (
            <PromptCard key={prompt.id} prompt={prompt} />
          ))}
        </div>
      </section>
    </div>
  );
}
