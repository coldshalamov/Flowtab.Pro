"use client";

import * as React from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Search, X } from "lucide-react";
import { cn } from "@/lib/utils";

export function SearchAndFilters({ availableTags }: { availableTags: string[] }) {
    const router = useRouter();
    const searchParams = useSearchParams();

    // Local state
    const [q, setQ] = React.useState(searchParams.get("q") || "");
    const [selectedTags, setSelectedTags] = React.useState<string[]>(
        searchParams.get("tags") ? searchParams.get("tags")!.split(",") : []
    );

    // Keep local state in sync with back/forward navigation.
    React.useEffect(() => {
        setQ(searchParams.get("q") || "");
        setSelectedTags(searchParams.get("tags") ? searchParams.get("tags")!.split(",") : []);
    }, [searchParams]);

    // Debounce search and sync logic
    React.useEffect(() => {
        const timer = setTimeout(() => {
            const params = new URLSearchParams();
            const trimmedQ = q.trim();
            if (trimmedQ) params.set("q", trimmedQ);
            const tagsForUrl = [...selectedTags].sort();
            if (tagsForUrl.length > 0) params.set("tags", tagsForUrl.join(","));

            const currentString = searchParams.toString();
            const newString = params.toString();
            if (currentString !== newString) {
                router.replace(newString ? `/library?${newString}` : "/library");
            }
        }, 250);
        return () => clearTimeout(timer);
    }, [q, selectedTags, router, searchParams]);


    const toggleTag = (tag: string) => {
        setSelectedTags(prev =>
            prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]
        );
    };

    const clearAll = () => {
        setQ("");
        setSelectedTags([]);
        router.replace("/library");
    };

    // Hardcoded default tags as requested
    const defaultTags = [
        "GitHub", "Scraping", "Forms", "Research", "Outreach",
        "Shopping", "Dashboards", "Data Extract", "QA / Review", "DevOps"
    ];

    // Merge available tags with defaults, deduping
    const allTags = Array.from(new Set([...defaultTags, ...availableTags]));

    return (
        <div className="space-y-8">
            <div className="flex flex-col gap-2">
                <div className="relative w-full">
                    <Search className="absolute left-3 top-3.5 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder="Search Flows…"
                        value={q}
                        onChange={(e) => setQ(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === "Escape") clearAll();
                        }}
                        className="pl-10 h-12 bg-background border-border focus:ring-1 focus:ring-primary/20 transition-all rounded-md text-base"
                    />
                    {(q.trim().length > 0 || selectedTags.length > 0) && (
                        <div className="absolute right-2 top-2">
                            <Button
                                type="button"
                                variant="ghost"
                                onClick={clearAll}
                                className="h-8 px-3 text-[10px] uppercase tracking-widest font-bold text-muted-foreground hover:text-foreground"
                            >
                                Clear <X className="ml-2 h-3 w-3" />
                            </Button>
                        </div>
                    )}
                </div>
                <p className="text-xs font-medium text-muted-foreground/60 pl-1">
                    Try: GitHub, scraping, forms, research, outreach
                </p>
            </div>

            <div className="space-y-4">
                <Label className="text-foreground text-xs uppercase tracking-widest font-bold opacity-60">Keywords</Label>
                <div className="flex flex-wrap gap-2.5">
                    {allTags.map(tag => (
                        <Badge
                            key={tag}
                            variant="outline"
                            className={cn(
                                "cursor-pointer h-9 px-4 text-xs font-semibold transition-all rounded-full touch-target",
                                selectedTags.includes(tag)
                                    ? "bg-primary/20 border-primary text-primary hover:bg-primary/30 shadow-[0_0_10px_rgba(var(--primary-rgb),0.2)]"
                                    : "bg-background border-border text-muted-foreground hover:border-foreground/30 hover:text-foreground hover:bg-secondary/50"
                            )}
                            onClick={() => toggleTag(tag)}
                        >
                            {tag}
                        </Badge>
                    ))}
                </div>
            </div>
        </div>
    );
}
