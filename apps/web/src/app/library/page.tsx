import { Suspense } from "react";
import { fetchPrompts, fetchTags, type Prompt } from "@/lib/api";
import { PromptCard } from "@/components/PromptCard";
import { SearchAndFilters } from "@/components/SearchAndFilters";
import { SearchFiltersSkeleton } from "@/components/SearchFiltersSkeleton";
import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "Archive // Flowtab.Pro",
    description: "Browse the archive of high-precision automation prompts and workflows.",
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

    const availableTags = await fetchTags();

    return (
        <div className="relative min-h-screen bg-background">
            <div className="container relative z-10 py-16 md:py-24 max-w-screen-2xl mx-auto px-6">
                <div className="flex flex-col gap-4 mb-16 animate-in fade-in slide-in-from-top-4 duration-700">
                    <div className="flex items-center gap-3">
                        <div className="w-1.5 h-8 bg-primary" />
                        <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-foreground uppercase">
                            Archive // <span className="text-muted-foreground/40">{total}</span>
                        </h1>
                    </div>
                    <p className="text-sm font-semibold text-muted-foreground/60 tracking-widest uppercase ml-5">
                        Prompt Repositories Synchronized
                    </p>
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
                            <div className="col-span-full py-40 text-center border-2 border-dashed border-border/40 rounded-xl flex flex-col items-center gap-6">
                                <div className="space-y-4">
                                    <p className="text-2xl font-bold tracking-tight text-foreground/40 uppercase">Null Result</p>
                                    <p className="text-sm font-medium text-muted-foreground/40 max-w-md mx-auto leading-relaxed">
                                        No prompts matched your current search parameters.
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
