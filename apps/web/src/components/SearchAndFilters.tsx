"use client";

import * as React from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { Search, X } from "lucide-react";
import { cn } from "@/lib/utils";

export function SearchAndFilters({ availableTags }: { availableTags: string[] }) {
    const router = useRouter();
    const searchParams = useSearchParams();

    // Local state
    const [q, setQ] = React.useState(searchParams.get("q") || "");
    const [worksWith, setWorksWith] = React.useState(searchParams.get("worksWith") || "");
    const [selectedTags, setSelectedTags] = React.useState<string[]>(
        searchParams.get("tags") ? searchParams.get("tags")!.split(",") : []
    );

    // Debounce search and sync logic
    React.useEffect(() => {
        const timer = setTimeout(() => {
            const params = new URLSearchParams();
            if (q) params.set("q", q);
            if (worksWith) params.set("worksWith", worksWith);
            if (selectedTags.length > 0) params.set("tags", selectedTags.join(","));

            const currentString = searchParams.toString();
            const newString = params.toString();
            if (currentString !== newString) {
                router.push(`/library?${newString}`);
            }
        }, 300);
        return () => clearTimeout(timer);
    }, [q, worksWith, selectedTags, router, searchParams]);


    const toggleTag = (tag: string) => {
        setSelectedTags(prev =>
            prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]
        );
    };

    return (
        <div className="space-y-6">
            <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                    placeholder="Search for prompts..."
                    value={q}
                    onChange={(e) => setQ(e.target.value)}
                    className="pl-10 h-11 bg-background border-border focus:ring-1 focus:ring-primary/20 transition-all rounded-md"
                />
            </div>

            <div className="flex flex-col md:flex-row gap-8">
                <div className="space-y-3 flex-1">
                    <Label className="text-foreground text-xs uppercase tracking-widest font-bold opacity-60">System Context</Label>
                    <ToggleGroup type="single" value={worksWith} onValueChange={(v) => setWorksWith(v || "")} className="justify-start gap-2">
                        <ToggleGroupItem value="Comet" className="h-9 px-4 border border-border data-[state=on]:bg-foreground data-[state=on]:text-background data-[state=on]:border-foreground rounded-md text-xs font-semibold transition-all">Comet</ToggleGroupItem>
                        <ToggleGroupItem value="Playwright MCP" className="h-9 px-4 border border-border data-[state=on]:bg-foreground data-[state=on]:text-background data-[state=on]:border-foreground rounded-md text-xs font-semibold transition-all">Playwright</ToggleGroupItem>
                        <ToggleGroupItem value="Opera Neon" className="h-9 px-4 border border-border data-[state=on]:bg-foreground data-[state=on]:text-background data-[state=on]:border-foreground rounded-md text-xs font-semibold transition-all">Neon</ToggleGroupItem>
                        <ToggleGroupItem value="Generic" className="h-9 px-4 border border-border data-[state=on]:bg-foreground data-[state=on]:text-background data-[state=on]:border-foreground rounded-md text-xs font-semibold transition-all">Generic</ToggleGroupItem>
                    </ToggleGroup>
                </div>
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
                            Clear Filters <X className="ml-1.5 h-3 w-3" />
                        </Button>
                    )}
                </div>
            </div>
        </div>
    );
}
