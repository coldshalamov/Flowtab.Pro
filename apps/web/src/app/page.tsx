import { fetchPrompts, type Prompt } from "@/lib/api";
import { PromptCard } from "@/components/PromptCard";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import Image from "next/image";
import { HeroBackground } from "@/components/HeroBackground";
import { FeaturedRotator } from "@/components/FeaturedRotator";

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
      <section className="relative flex flex-col items-center justify-center pt-32 pb-32 overflow-hidden bg-black border-b border-white/10 text-white">

        {/* Dynamic Space Background */}
        <HeroBackground />

        {/* Structural Grid Background - Overlaying the stars slightly or behind? 
            Let's keep the grid behind content but maybe integrate with stars. 
            Putting stars BEHIND grid: Grid opacity is 100 currently but has transparent parts.
        */}
        <div className="absolute inset-0 z-0 opacity-20 pointer-events-none">
          {/* Reduced opacity of grid to let stars shine through better, or keep it subtle */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff20_1px,transparent_1px),linear-gradient(to_bottom,#ffffff20_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />
        </div>

        <div className="relative z-10 max-w-4xl px-4 text-center space-y-8">
          <h1 className="text-6xl sm:text-7xl md:text-8xl font-bold tracking-tight text-white text-balance animate-in fade-in slide-in-from-bottom-8 duration-700 delay-100">
            Operate With Autonomy
          </h1>

          <p className="max-w-xl mx-auto text-lg sm:text-xl text-zinc-400 font-medium leading-relaxed animate-in fade-in slide-in-from-bottom-6 duration-700 delay-200">
            Reusable workflows for browser-based AI agents.
          </p>

          <div className="flex flex-col items-center gap-2 animate-in fade-in slide-in-from-bottom-6 duration-700 delay-300">
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link href="/library">
                <Button
                  size="lg"
                  className="h-12 px-8 rounded-md bg-white text-black hover:bg-white/90 font-semibold text-base shadow-lg shadow-white/10 transition-all hover:scale-105"
                >
                  Browse Flows
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>

              <Link href="/submit">
                <Button
                  variant="outline"
                  size="lg"
                  className="h-12 px-8 rounded-md border-white/20 bg-transparent text-white hover:bg-white/10 font-semibold text-base transition-all"
                >
                  Submit a Flow
                </Button>
              </Link>
            </div>
            <p className="text-xs text-zinc-500 pt-2">Browse for free.</p>
          </div>

          <FeaturedRotator flows={featuredPrompts.map(p => ({ title: p.title, slug: p.slug, like_count: p.like_count || 0 }))} />
        </div>

        {/* Minimal Tech Stack */}
        <div className="mt-24 w-full relative z-10 animate-in fade-in duration-1000 delay-500">
          <div className="flex flex-col items-center gap-4 text-center px-4">
            <div className="flex flex-col gap-24">
              <span className="text-3xl font-bold tracking-tight text-white">Pick your Flowbot.</span>
              <p className="text-xl md:text-2xl font-bold uppercase tracking-widest text-zinc-300">Works with:</p>
            </div>

            <div className="w-full max-w-5xl mx-auto border-white/10">
              <div className="grid grid-cols-2 md:grid-cols-4">
                <a href="https://www.perplexity.ai/comet" target="_blank" rel="noopener noreferrer" className="group p-8 flex justify-center items-center transition-colors">
                  <div className="flex items-center gap-3 grayscale group-hover:grayscale-0 opacity-50 group-hover:opacity-100 transition-all duration-300">
                    <Image src="/images/logos/comet.webp" alt="Comet" width={60} height={60} className="object-contain invert dark:invert-0" />
                    <span className="text-lg font-semibold text-white">Comet</span>
                  </div>
                </a>
                <a href="https://manus.im/features/manus-browser-operator" target="_blank" rel="noopener noreferrer" className="group p-8 flex justify-center items-center transition-colors">
                  <div className="flex items-center gap-3 grayscale group-hover:grayscale-0 opacity-50 group-hover:opacity-100 transition-all duration-300">
                    <Image src="/images/logos/manus.png" alt="Manus" width={60} height={60} className="object-contain invert dark:invert-0" />
                    <span className="text-lg font-semibold text-white">Manus</span>
                  </div>
                </a>
                <a href="https://www.opera.com/browsers/neon" target="_blank" rel="noopener noreferrer" className="group p-8 flex justify-center items-center transition-colors">
                  <div className="flex items-center gap-3 grayscale group-hover:grayscale-0 opacity-50 group-hover:opacity-100 transition-all duration-300">
                    <Image src="/images/logos/neon.jpg" alt="Neon" width={70} height={70} className="object-contain rounded-full" />
                    <span className="text-lg font-semibold text-white">Neon</span>
                  </div>
                </a>
                <a href="https://chatgpt.com/atlas/" target="_blank" rel="noopener noreferrer" className="group p-8 flex justify-center items-center transition-colors">
                  <div className="flex items-center gap-3 grayscale group-hover:grayscale-0 opacity-50 group-hover:opacity-100 transition-all duration-300">
                    <Image src="/images/logos/atlas.png" alt="Atlas" width={60} height={60} className="object-contain invert dark:invert-0" />
                    <span className="text-lg font-semibold text-white">Atlas</span>
                  </div>
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Section */}
      <section className="container py-20 md:py-32 space-y-12 px-4 max-w-screen-2xl mx-auto">
        <div className="flex items-end justify-between border-b-2 border-border/60 pb-6">
          <div className="space-y-1">
            <h2 className="text-3xl font-bold tracking-tight text-foreground">Featured Flows</h2>
            <p className="text-muted-foreground font-medium">Curated high-performance workflows.</p>
          </div>
          <Link href="/library" className="group text-sm font-semibold text-foreground hover:text-primary transition-colors flex items-center gap-1">
            View Library <ArrowRight className="ml-1 h-4 w-4 group-hover:translate-x-1 transition-transform" />
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
