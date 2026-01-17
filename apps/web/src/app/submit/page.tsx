"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { submitPrompt } from "@/lib/api";
import { ChevronLeft, Share2 } from "lucide-react";
import Link from "next/link";

export default function SubmitPage() {
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        title: "",
        summary: "",
        targetSites: "",
        tags: "",
        promptText: "",
        steps: "",
        notes: ""
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        if (!formData.title || !formData.promptText) {
            toast.error("Required fields missing.");
            setLoading(false);
            return;
        }

        try {
            const ok = await submitPrompt({
                ...formData,
                worksWith: [],
                tags: formData.tags.split(",").map(t => t.trim()).filter(Boolean),
                targetSites: formData.targetSites.split(",").map(t => t.trim()).filter(Boolean),
                steps: formData.steps.split("\n").filter(Boolean),
            });

            if (!ok) throw new Error("Submit failed");

            toast.success("Deployment successful. Awaiting synchronization.");
            setFormData({
                title: "",
                summary: "",
                targetSites: "",
                tags: "",
                promptText: "",
                steps: "",
                notes: ""
            });
        } catch {
            toast.error("Synchronization failed. Please retry.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="relative min-h-screen bg-background">
            {/* Structural Grid Background */}
            <div className="absolute inset-0 z-0 opacity-40">
                <div className="absolute inset-0 bg-[linear-gradient(to_right,oklch(var(--border)/0.5)_1px,transparent_1px),linear-gradient(to_bottom,oklch(var(--border)/0.5)_1px,transparent_1px)] bg-[size:6rem_6rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none" />
            </div>

            <div className="container relative z-10 py-16 md:py-24 max-w-3xl mx-auto px-6">
                <div className="mb-12 space-y-6">
                    <Link href="/library" className="group inline-flex items-center text-xs font-bold uppercase tracking-widest text-muted-foreground hover:text-foreground transition-colors">
                        <ChevronLeft className="mr-1.5 h-4 w-4 group-hover:-translate-x-0.5 transition-transform" />
                        Return to Archive
                    </Link>

                    <div className="space-y-2">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-primary rounded-md">
                                <Share2 className="h-5 w-5 text-primary-foreground" />
                            </div>
                            <h1 className="text-4xl font-bold tracking-tight text-foreground uppercase">
                                Deploy Recipe
                            </h1>
                        </div>
                        <p className="text-muted-foreground font-medium uppercase tracking-widest text-xs opacity-60 ml-12">
                            Contribute to the Global Automation Repository
                        </p>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-12 animate-in fade-in slide-in-from-bottom-8 duration-700 bg-secondary/30 p-8 md:p-12 rounded-lg border border-border/40">
                    <div className="space-y-8">
                        <div className="grid gap-3">
                            <Label htmlFor="title" className="text-xs uppercase tracking-widest font-bold opacity-60">Recipe Title *</Label>
                            <Input
                                id="title"
                                placeholder="e.g. LinkedIn Reachout Automator"
                                value={formData.title}
                                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                className="h-11 bg-background border-border font-medium"
                                required
                            />
                        </div>

                        <div className="grid gap-3">
                            <Label htmlFor="summary" className="text-xs uppercase tracking-widest font-bold opacity-60">Objective Summary</Label>
                            <Textarea
                                id="summary"
                                placeholder="Define the primary operational goal..."
                                value={formData.summary}
                                onChange={(e) => setFormData({ ...formData, summary: e.target.value })}
                                className="min-h-[80px] bg-background border-border font-medium resize-none"
                            />
                        </div>

                        <div className="grid md:grid-cols-2 gap-8">
                            <div className="grid gap-3">
                                <Label htmlFor="targetSites" className="text-xs uppercase tracking-widest font-bold opacity-60">Target Domains</Label>
                                <Input
                                    id="targetSites"
                                    placeholder="linkedin.com, github.com"
                                    value={formData.targetSites}
                                    onChange={(e) => setFormData({ ...formData, targetSites: e.target.value })}
                                    className="h-11 bg-background border-border font-medium"
                                />
                            </div>

                            <div className="grid gap-3">
                                <Label htmlFor="tags" className="text-xs uppercase tracking-widest font-bold opacity-60">Cluster Tags</Label>
                                <Input
                                    id="tags"
                                    placeholder="social, marketing, sync"
                                    value={formData.tags}
                                    onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                                    className="h-11 bg-background border-border font-medium"
                                />
                            </div>
                        </div>

                        <div className="grid gap-3">
                            <Label htmlFor="promptText" className="text-xs uppercase tracking-widest font-bold opacity-60">Core Prompt Payload *</Label>
                            <Textarea
                                id="promptText"
                                className="min-h-[250px] font-mono text-sm bg-background border-border p-6"
                                placeholder="Primary command sequence..."
                                value={formData.promptText}
                                onChange={(e) => setFormData({ ...formData, promptText: e.target.value })}
                                required
                            />
                        </div>

                        <div className="grid gap-3">
                            <Label htmlFor="steps" className="text-xs uppercase tracking-widest font-bold opacity-60">Execution Steps (New line per step)</Label>
                            <Textarea
                                id="steps"
                                placeholder="1. Initialize synchronization...&#10;2. Execute protocol..."
                                value={formData.steps}
                                onChange={(e) => setFormData({ ...formData, steps: e.target.value })}
                                className="min-h-[120px] bg-background border-border font-medium"
                            />
                        </div>

                        <div className="grid gap-3">
                            <Label htmlFor="notes" className="text-xs uppercase tracking-widest font-bold opacity-60">Anomalies & Pitfalls</Label>
                            <Textarea
                                id="notes"
                                placeholder="Critical failure modes or edge cases..."
                                value={formData.notes}
                                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                                className="min-h-[100px] bg-background border-border font-medium"
                            />
                        </div>
                    </div>

                    <Button type="submit" size="lg" className="w-full h-14 bg-foreground text-background hover:bg-foreground/90 font-bold uppercase tracking-widest text-sm shadow-xl shadow-foreground/5 rounded-md transition-all active:scale-[0.98]" disabled={loading}>
                        {loading ? "Synchronizing..." : "Initiate Deployment"}
                    </Button>
                </form>
            </div>
        </div>
    );
}
