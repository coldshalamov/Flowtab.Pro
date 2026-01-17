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

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row gap-3 sm:items-center">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder="Search prompts…"
                        value={q}
                        onChange={(e) => setQ(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === "Escape") clearAll();
                        }}
                        className="pl-10 h-11 bg-background border-border focus:ring-1 focus:ring-primary/20 transition-all rounded-md"
                    />
                </div>

                {(q.trim().length > 0 || selectedTags.length > 0) && (
                    <Button
                        type="button"
                        variant="ghost"
                        onClick={clearAll}
                        className="h-11 px-4 text-xs uppercase tracking-widest font-bold text-muted-foreground hover:text-foreground"
                    >
                        Clear <X className="ml-2 h-3.5 w-3.5" />
                    </Button>
                )}
            </div>

            <div className="space-y-3">
                <Label className="text-foreground text-xs uppercase tracking-widest font-bold opacity-60">Cluster Tags</Label>
                <div className="flex flex-wrap gap-2">
                    {availableTags.map(tag => (
                        <Badge
                            key={tag}
                            variant={selectedTags.includes(tag) ? "default" : "outline"}
                            className={cn(
                                "cursor-pointer h-7 px-3 text-[11px] font-bold uppercase tracking-wider transition-all",
                                selectedTags.includes(tag)
                                    ? "bg-primary text-primary-foreground border-primary"
                                    : "text-muted-foreground border-border hover:border-foreground/20 bg-background"
                            )}
                            onClick={() => toggleTag(tag)}
                        >
                            #{tag}
                        </Badge>
                    ))}
                    {selectedTags.length > 0 && (
                        <Button variant="ghost" size="sm" onClick={() => setSelectedTags([])} className="h-7 px-3 text-[10px] uppercase tracking-widest font-bold text-muted-foreground hover:text-destructive">
                            Clear Tags <X className="ml-1.5 h-3 w-3" />
                        </Button>
                    )}
                </div>
            </div>
        </div>
    );
}
