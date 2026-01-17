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
    const [difficulty, setDifficulty] = React.useState(searchParams.get("difficulty") || "");
    const [worksWith, setWorksWith] = React.useState(searchParams.get("worksWith") || "");
    const [selectedTags, setSelectedTags] = React.useState<string[]>(
        searchParams.get("tags") ? searchParams.get("tags")!.split(",") : []
    );

    // Debounce search and sync logic
    React.useEffect(() => {
        const timer = setTimeout(() => {
            const params = new URLSearchParams();
            if (q) params.set("q", q);
            if (difficulty) params.set("difficulty", difficulty);
            if (worksWith) params.set("worksWith", worksWith);
            if (selectedTags.length > 0) params.set("tags", selectedTags.join(","));

            const currentString = searchParams.toString();
            const newString = params.toString();
            if (currentString !== newString) {
                router.push(`/library?${newString}`);
            }
        }, 300);
        return () => clearTimeout(timer);
    }, [q, difficulty, worksWith, selectedTags, router, searchParams]);


    const toggleTag = (tag: string) => {
        setSelectedTags(prev =>
            prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]
        );
    };

    return (
        <div className="space-y-6 bg-card/50 p-6 rounded-xl border border-border/50 backdrop-blur-sm">
            <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                    placeholder="Search for prompts..."
                    value={q}
                    onChange={(e) => setQ(e.target.value)}
                    className="pl-9 bg-background/50 border-primary/20 focus:border-primary transition-colors"
                />
            </div>

            <div className="flex flex-col md:flex-row gap-8">
                <div className="space-y-3 flex-1">
                    <Label className="text-muted-foreground text-xs uppercase tracking-wider font-semibold">Difficulty</Label>
                    <ToggleGroup type="single" value={difficulty} onValueChange={(v) => setDifficulty(v || "")} className="justify-start">
                        <ToggleGroupItem value="beginner" aria-label="Beginner" className="data-[state=on]:bg-green-500/20 data-[state=on]:text-green-500 border border-transparent data-[state=on]:border-green-500/30">Beginner</ToggleGroupItem>
                        <ToggleGroupItem value="intermediate" aria-label="Intermediate" className="data-[state=on]:bg-yellow-500/20 data-[state=on]:text-yellow-500 border border-transparent data-[state=on]:border-yellow-500/30">Intermediate</ToggleGroupItem>
                        <ToggleGroupItem value="advanced" aria-label="Advanced" className="data-[state=on]:bg-red-500/20 data-[state=on]:text-red-500 border border-transparent data-[state=on]:border-red-500/30">Advanced</ToggleGroupItem>
                    </ToggleGroup>
                </div>

                <div className="space-y-3 flex-1">
                    <Label className="text-muted-foreground text-xs uppercase tracking-wider font-semibold">Works With</Label>
                    <ToggleGroup type="single" value={worksWith} onValueChange={(v) => setWorksWith(v || "")} className="justify-start">
                        <ToggleGroupItem value="Comet" className="data-[state=on]:bg-primary/20 data-[state=on]:text-primary">Comet</ToggleGroupItem>
                        <ToggleGroupItem value="Playwright MCP" className="data-[state=on]:bg-primary/20 data-[state=on]:text-primary">Playwright</ToggleGroupItem>
                        <ToggleGroupItem value="Opera Neon" className="data-[state=on]:bg-primary/20 data-[state=on]:text-primary">Opera</ToggleGroupItem>
                        <ToggleGroupItem value="Generic" className="data-[state=on]:bg-primary/20 data-[state=on]:text-primary">Generic</ToggleGroupItem>
                    </ToggleGroup>
                </div>
            </div>

            <div className="space-y-3">
                <Label className="text-muted-foreground text-xs uppercase tracking-wider font-semibold">Popular Tags</Label>
                <div className="flex flex-wrap gap-2">
                    {availableTags.map(tag => (
                        <Badge
                            key={tag}
                            variant={selectedTags.includes(tag) ? "default" : "outline"}
                            className={cn(
                                "cursor-pointer hover:bg-primary/80 transition-colors",
                                selectedTags.includes(tag) ? "bg-primary text-primary-foreground" : "text-muted-foreground bg-background hover:text-foreground"
                            )}
                            onClick={() => toggleTag(tag)}
                        >
                            {tag}
                        </Badge>
                    ))}
                    {selectedTags.length > 0 && (
                        <Button variant="ghost" size="sm" onClick={() => setSelectedTags([])} className="h-6 px-2 text-xs text-muted-foreground hover:text-destructive">
                            Clear Tags <X className="ml-1 h-3 w-3" />
                        </Button>
                    )}
                </div>
            </div>
        </div>
    );
}
