import { fetchPrompts, type Prompt } from "@/lib/api";
import { PromptCard } from "@/components/PromptCard";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import Image from "next/image";

// Revalidate every hour
export const revalidate = 3600;

export default async function Home() {
  const { items: featuredPrompts } = await fetchPrompts({
    page: 1,
    pageSize: 6,
    tags: 'featured'
  });

  return (
    <div className="flex flex-col min-h-[calc(100vh-4rem)]">
      {/* Hero Section */}
      <section className="relative flex flex-col items-center justify-center pt-32 pb-32 overflow-hidden bg-background border-b border-border/40">
        {/* Structural Grid Background */}
        <div className="absolute inset-0 z-0 opacity-100">
          <div className="absolute inset-0 bg-[linear-gradient(to_right,oklch(var(--border)/0.3)_1px,transparent_1px),linear-gradient(to_bottom,oklch(var(--border)/0.3)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none" />
        </div>

        <div className="relative z-10 max-w-4xl px-6 text-center space-y-10">
          <h1 className="text-6xl sm:text-7xl md:text-8xl font-bold tracking-tight text-foreground text-balance animate-in fade-in slide-in-from-bottom-8 duration-700 delay-100">
            Operate <br className="hidden md:block" />
            <span className="text-muted-foreground">With Autonomy</span>
          </h1>

          <p className="max-w-xl mx-auto text-lg sm:text-xl text-muted-foreground/90 font-medium leading-relaxed animate-in fade-in slide-in-from-bottom-6 duration-700 delay-200">
            The definitive repository of browser automation recipes.
            Optimized for Comet, Playwright, and Opera Neon.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-8 animate-in fade-in slide-in-from-bottom-6 duration-700 delay-300">
            <Link href="/library">
              <Button
                size="lg"
                className="h-12 px-8 rounded-md bg-foreground text-background hover:bg-foreground/90 font-semibold text-base shadow-lg shadow-foreground/5 transition-all hover:scale-105"
              >
                Browse Library
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>

            <Link href="/submit">
              <Button
                variant="outline"
                size="lg"
                className="h-12 px-8 rounded-md border-border bg-background hover:bg-secondary font-semibold text-base transition-all"
              >
                Submit Recipe
              </Button>
            </Link>
          </div>
        </div>

        {/* Minimal Tech Stack */}
        <div className="mt-32 w-full animate-in fade-in duration-1000 delay-500">
          <div className="container max-w-5xl px-6 flex flex-col md:flex-row items-center justify-center gap-12 sm:gap-16 opacity-50 hover:opacity-100 transition-opacity duration-500">
            <a href="https://checkcomet.com" target="_blank" rel="noopener noreferrer" className="group">
              <div className="flex items-center gap-3 grayscale group-hover:grayscale-0 transition-all">
                <Image src="/images/logos/comet.svg" alt="Comet" width={24} height={24} />
                <span className="font-semibold text-foreground/80">Comet</span>
              </div>
            </a>
            <a href="https://playwright.dev" target="_blank" rel="noopener noreferrer" className="group">
              <div className="flex items-center gap-3 grayscale group-hover:grayscale-0 transition-all">
                <Image src="/images/logos/playwright.svg" alt="Playwright" width={24} height={24} />
                <span className="font-semibold text-foreground/80">Playwright</span>
              </div>
            </a>
            <a href="https://www.opera.com/browsers/neon" target="_blank" rel="noopener noreferrer" className="group">
              <div className="flex items-center gap-3 grayscale group-hover:grayscale-0 transition-all">
                <Image src="/images/logos/neon.svg" alt="Neon" width={24} height={24} />
                <span className="font-semibold text-foreground/80">Neon</span>
              </div>
            </a>
          </div>
        </div>
      </section>

      {/* Featured Section */}
      <section className="container py-20 md:py-32 space-y-12 px-4 max-w-screen-2xl mx-auto">
        <div className="flex items-end justify-between border-b-2 border-border/60 pb-6">
          <div className="space-y-1">
            <h2 className="text-3xl font-bold tracking-tight text-foreground">Featured Recipes</h2>
            <p className="text-muted-foreground font-medium">Curated high-performance workflows.</p>
          </div>
          <Link href="/library" className="group text-sm font-semibold text-foreground hover:text-primary transition-colors flex items-center gap-1">
            View Archive <ArrowRight className="ml-1 h-4 w-4 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>

        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {featuredPrompts.map((prompt: Prompt) => (
            <PromptCard key={prompt.id} prompt={prompt} />
          ))}
        </div>
      </section>
    </div>
  );
}