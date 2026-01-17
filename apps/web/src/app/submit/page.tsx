"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { toast } from "sonner";
import { submitPrompt } from "@/lib/api";

export default function SubmitPage() {
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        title: "",
        summary: "",
        difficulty: "beginner" as "beginner" | "intermediate" | "advanced",
        worksWith: [] as string[],
        targetSites: "",
        tags: "",
        promptText: "",
        steps: "",
        notes: ""
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        // Basic validation
        if (!formData.title || !formData.promptText) {
            toast.error("Please fill in required fields.");
            setLoading(false);
            return;
        }

        try {
            const ok = await submitPrompt({
                ...formData,
                tags: formData.tags.split(",").map(t => t.trim()).filter(Boolean),
                targetSites: formData.targetSites.split(",").map(t => t.trim()).filter(Boolean),
                steps: formData.steps.split("\n").filter(Boolean),
            });

            if (!ok) {
                throw new Error("Submit failed");
            }
            toast.success("Thanks for your submission! It will be reviewed shortly.");
            setFormData({
                title: "",
                summary: "",
                difficulty: "beginner",
                worksWith: [],
                targetSites: "",
                tags: "",
                promptText: "",
                steps: "",
                notes: ""
            });
        } catch {
            toast.error("Failed to submit prompt. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container py-8 max-w-2xl mx-auto px-4 min-h-screen">
            <div className="mb-8 space-y-4">
                <h1 className="text-3xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
                    Contribute a Prompt
                </h1>
                <p className="text-muted-foreground text-lg">
                    Share your automation recipes with the community.
                </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="space-y-4">
                    <div className="grid gap-2">
                        <Label htmlFor="title">Title *</Label>
                        <Input
                            id="title"
                            placeholder="e.g. LinkedIn Connection Automation"
                            value={formData.title}
                            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                            required
                        />
                    </div>

                    <div className="grid gap-2">
                        <Label htmlFor="summary">Short Summary</Label>
                        <Textarea
                            id="summary"
                            placeholder="What does this prompt do?"
                            value={formData.summary}
                            onChange={(e) => setFormData({ ...formData, summary: e.target.value })}
                        />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="grid gap-2">
                            <Label htmlFor="difficulty">Difficulty</Label>
                            <Select
                                value={formData.difficulty}
                                onValueChange={(v) => setFormData({ ...formData, difficulty: v as "beginner" | "intermediate" | "advanced" })}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select difficulty" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="beginner">Beginner</SelectItem>
                                    <SelectItem value="intermediate">Intermediate</SelectItem>
                                    <SelectItem value="advanced">Advanced</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="grid gap-2">
                            <Label>Works With</Label>
                            <ToggleGroup type="multiple" value={formData.worksWith} onValueChange={(v) => setFormData({ ...formData, worksWith: v })} className="justify-start flex-wrap">
                                <ToggleGroupItem value="Comet" aria-label="Comet" className="border border-input data-[state=on]:bg-primary data-[state=on]:text-primary-foreground">Comet</ToggleGroupItem>
                                <ToggleGroupItem value="Playwright MCP" aria-label="Playwright" className="border border-input data-[state=on]:bg-primary data-[state=on]:text-primary-foreground">Playwright</ToggleGroupItem>
                                <ToggleGroupItem value="Opera Neon" aria-label="Opera" className="border border-input data-[state=on]:bg-primary data-[state=on]:text-primary-foreground">Opera</ToggleGroupItem>
                            </ToggleGroup>
                        </div>
                    </div>

                    <div className="grid gap-2">
                        <Label htmlFor="targetSites">Target Sites (comma separated)</Label>
                        <Input
                            id="targetSites"
                            placeholder="linkedin.com, github.com"
                            value={formData.targetSites}
                            onChange={(e) => setFormData({ ...formData, targetSites: e.target.value })}
                        />
                    </div>

                    <div className="grid gap-2">
                        <Label htmlFor="tags">Tags (comma separated)</Label>
                        <Input
                            id="tags"
                            placeholder="social, automation, scraping"
                            value={formData.tags}
                            onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                        />
                    </div>

                    <div className="grid gap-2">
                        <Label htmlFor="promptText">Prompt Text *</Label>
                        <Textarea
                            id="promptText"
                            className="min-h-[200px] font-mono text-sm"
                            placeholder="Paste the full prompt here..."
                            value={formData.promptText}
                            onChange={(e) => setFormData({ ...formData, promptText: e.target.value })}
                            required
                        />
                    </div>

                    <div className="grid gap-2">
                        <Label htmlFor="steps">Steps (one per line)</Label>
                        <Textarea
                            id="steps"
                            placeholder="1. Login...&#10;2. Navigate..."
                            value={formData.steps}
                            onChange={(e) => setFormData({ ...formData, steps: e.target.value })}
                        />
                    </div>

                    <div className="grid gap-2">
                        <Label htmlFor="notes">Notes / Pitfalls</Label>
                        <Textarea
                            id="notes"
                            placeholder="Any warnings or tips?"
                            value={formData.notes}
                            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                        />
                    </div>
                </div>

                <Button type="submit" size="lg" className="w-full" disabled={loading}>
                    {loading ? "Submitting..." : "Submit Prompt"}
                </Button>
            </form>
        </div>
    );
}
