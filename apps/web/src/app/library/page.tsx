import { Suspense } from "react";
import { fetchPrompts, fetchTags, type Prompt } from "@/lib/api";
import { PromptCard } from "@/components/PromptCard";
import { SearchAndFilters } from "@/components/SearchAndFilters";
import { SearchFiltersSkeleton } from "@/components/SearchFiltersSkeleton";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "Library // Flowtab.Pro",
    description: "Browse the library of high-precision automation prompts and workflows.",
};

export default async function LibraryPage(props: {
    searchParams: Promise<{ [key: string]: string | string[] | undefined }> | { [key: string]: string | string[] | undefined };
}) {
    const searchParams = await Promise.resolve(props.searchParams);

    const q = typeof searchParams.q === "string" ? searchParams.q : undefined;
    const tags = typeof searchParams.tags === "string" ? searchParams.tags : undefined;

    const { items: prompts, total } = await fetchPrompts({
        q, tags,
        page: 1, pageSize: 20
    });

    const { items: featuredPrompts } = await fetchPrompts({
        page: 1, pageSize: 3, tags: 'featured'
    });

    const availableTags = await fetchTags();

    return (
        <div className="relative min-h-screen bg-background">
            <div className="container relative z-10 py-16 md:py-24 max-w-screen-2xl mx-auto px-6">
                <div className="flex flex-col gap-6 mb-12 animate-in fade-in slide-in-from-top-4 duration-700">
                    <div className="flex flex-col gap-2">
                        <div className="flex items-center gap-3">
                            <div className="w-1.5 h-8 bg-primary" />
                            <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-foreground uppercase">
                                LIBRARY
                            </h1>
                        </div>
                        <p className="text-xl md:text-2xl font-medium text-foreground/90 ml-5">
                            Browse Flows. Copy. Run. Iterate.
                        </p>
                        <p className="text-sm font-medium text-muted-foreground/60 ml-5">
                            Runner-agnostic workflows for browser-based agents.
                        </p>
                    </div>
                </div>

                {/* Featured Flows Strip */}
                <div className="mb-16 space-y-6">
                    <div className="flex items-center justify-between border-b border-border/40 pb-4">
                        <h2 className="text-lg font-semibold tracking-tight text-foreground">Featured Flows</h2>
                        <Link href="/library?tags=featured" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
                            View all
                        </Link>
                    </div>
                    <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
                        {featuredPrompts.map((p: Prompt) => (
                            <PromptCard key={`featured-${p.id}`} prompt={p} />
                        ))}
                        {/* Fallback if no featured prompts found, to ensure strip exists as requested */}
                        {featuredPrompts.length === 0 && (
                            <div className="col-span-full py-8 text-center text-muted-foreground text-sm">
                                Loading featured flows...
                            </div>
                        )}
                    </div>
                </div>

                <div className="flex flex-col gap-12">
                    <div className="animate-in fade-in slide-in-from-top-6 duration-700 delay-100 bg-secondary/30 p-8 rounded-lg border border-border/40">
                        <Suspense fallback={<SearchFiltersSkeleton />}>
                            <SearchAndFilters availableTags={availableTags} />
                        </Suspense>
                    </div>

                    <div className="grid gap-8 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-300">
                        {prompts.length > 0 ? (
                            prompts.map((p: Prompt) => (
                                <PromptCard key={p.id} prompt={p} />
                            ))
                        ) : (
                            <div className="col-span-full py-12 md:py-20 text-center border-2 border-dashed border-border/40 rounded-xl flex flex-col items-center gap-6">
                                <div className="space-y-4">
                                    <p className="text-2xl font-bold tracking-tight text-foreground/40 uppercase">NULL RESULT</p>
                                    <div className="w-12 h-1 bg-border/40 mx-auto" />
                                    <p className="text-sm font-medium text-muted-foreground/40 max-w-md mx-auto leading-relaxed">
                                        No Flows match your current filters.
                                    </p>
                                </div>

                                <div className="flex items-center gap-4">
                                    <Link href="/library">
                                        <Button variant="secondary" className="bg-secondary/50">
                                            Clear filters
                                        </Button>
                                    </Link>
                                    <Link href="/library?tags=featured">
                                        <Button variant="default">
                                            Browse Featured
                                        </Button>
                                    </Link>
                                </div>

                                <Link href="/submit" className="text-sm font-semibold text-primary hover:underline">
                                    Or submit a Flow →
                                </Link>

                                <p className="text-xs text-muted-foreground/40 uppercase tracking-widest font-bold pt-4">
                                    Try: GitHub · scraping · forms · research
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
