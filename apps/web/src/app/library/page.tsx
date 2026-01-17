import { Suspense } from "react";
import { fetchPrompts, fetchTags } from "@/lib/api";
import { PromptCard } from "@/components/PromptCard";
import { SearchAndFilters } from "@/components/SearchAndFilters";
import { SearchFiltersSkeleton } from "@/components/SearchFiltersSkeleton";
import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "Library - Flowtab.Pro",
    description: "Browse our collection of automated browser prompt recipes for Comet, Playwright, and Opera Neon.",
};
import Image from "next/image";

export default async function LibraryPage(props: {
    searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
    const searchParams = await props.searchParams;

    const q = typeof searchParams.q === "string" ? searchParams.q : undefined;
    const difficulty = typeof searchParams.difficulty === "string" ? searchParams.difficulty : undefined;
    const worksWith = typeof searchParams.worksWith === "string" ? searchParams.worksWith : undefined;
    const tags = typeof searchParams.tags === "string" ? searchParams.tags : undefined;

    const { items: prompts, total } = await fetchPrompts({
        q, difficulty, worksWith, tags,
        page: 1, pageSize: 20
    });

    const availableTags = await fetchTags();

    return (
        <div className="container py-6 md:py-8 max-w-screen-2xl mx-auto px-4 min-h-screen">
            <div className="flex flex-col gap-2 mb-6 md:mb-8 animate-in fade-in slide-in-from-top-4 duration-500">
                <h1 className="text-2xl md:text-3xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
                    Prompt Library
                </h1>
                <p className="text-sm md:text-base text-muted-foreground">
                    Browse our collection of {total > 0 ? total : ''} automated browser workflows.
                </p>
            </div>

            <div className="flex flex-col gap-8">
                <div className="animate-in fade-in slide-in-from-top-6 duration-700 delay-100">
                    <Suspense fallback={<SearchFiltersSkeleton />}>
                        <SearchAndFilters availableTags={availableTags} />
                    </Suspense>
                </div>

                <div className="grid gap-4 sm:gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 animate-in fade-in slide-in-from-top-8 duration-700 delay-200">
                    {prompts.length > 0 ? (
                        prompts.map(p => (
                            <PromptCard key={p.id} prompt={p} />
                        ))
                    ) : (
                        <div className="col-span-full py-20 text-center text-muted-foreground bg-muted/5 rounded-xl border border-dashed border-muted/50 flex flex-col items-center gap-6">
                            <div className="relative w-64 h-64">
                                <Image
                                    src="/images/empty-search.png"
                                    alt="No results"
                                    fill
                                    className="object-contain opacity-60"
                                />
                            </div>
                            <div className="space-y-2">
                                <p className="text-xl font-semibold text-foreground/80">No prompts found</p>
                                <p className="text-sm text-muted-foreground max-w-md">
                                    Try adjusting your filters or search terms to find what you&apos;re looking for.
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
