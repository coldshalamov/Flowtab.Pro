import Link from "next/link";
import { fetchPrompt } from "@/lib/api";
import { notFound } from "next/navigation";
import { CopyButton } from "@/components/CopyButton";
import { SaveButton } from "@/components/SaveButton";
import { AdminControls } from "@/components/AdminControls";
import { LikeButton } from "@/components/LikeButton";
import { CommentsSection } from "@/components/CommentsSection";
import { Button } from "@/components/ui/button";
import { Layers, ChevronLeft, Clock, Globe } from "lucide-react";
import type { Metadata } from "next";
import Image from "next/image";

export async function generateMetadata(props: {
    params: Promise<{ slug: string }> | { slug: string };
}): Promise<Metadata> {
    const params = await Promise.resolve(props.params);
    const prompt = await fetchPrompt(params.slug);
    if (!prompt) return { title: "Flow Not Found" };
    return { title: `${prompt.title} // Flowtab.Pro`, description: prompt.summary };
}

export default async function PromptDetailPage(props: { params: Promise<{ slug: string }> | { slug: string } }) {
    const params = await Promise.resolve(props.params);
    const prompt = await fetchPrompt(params.slug);
    if (!prompt) notFound();

    const jsonString = JSON.stringify(prompt, null, 2);

    return (
        <div className="relative min-h-screen bg-background">
            <div className="container relative z-10 py-16 md:py-24 max-w-5xl mx-auto px-6">
                {/* Navigation */}
                <div className="mb-12 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <Link href="/library" className="group inline-flex items-center text-xs font-bold uppercase tracking-widest text-muted-foreground hover:text-foreground transition-colors">
                        <ChevronLeft className="mr-1.5 h-4 w-4 group-hover:-translate-x-0.5 transition-transform" />
                        Library
                    </Link>
                </div>

                {/* Header Section */}
                <div className="space-y-6 mb-12 animate-in fade-in slide-in-from-bottom-8 duration-700">
                    <h1 className="text-4xl md:text-6xl font-bold tracking-tighter text-foreground uppercase leading-[0.9]">
                        {prompt.title}
                    </h1>

                    <p className="text-xl text-muted-foreground font-medium leading-relaxed max-w-3xl">
                        {prompt.summary}
                    </p>

                    <div className="flex flex-wrap gap-8 items-center text-[10px] font-bold uppercase tracking-widest text-muted-foreground/60 pt-6 border-t border-border">
                        <div className="flex items-center gap-2">
                            <Clock className="h-3.5 w-3.5" />
                            Compiled // {new Date(prompt.updatedAt).toLocaleDateString()}
                        </div>
                        {prompt.worksWith && prompt.worksWith.length > 0 && (
                            <div className="flex items-center gap-2">
                                <span className="text-muted-foreground/60">Works With //</span>
                                <div className="flex gap-2">
                                    {prompt.worksWith.map(w => (
                                        <span key={w} className="bg-secondary px-1.5 py-0.5 rounded text-foreground">{w}</span>
                                    ))}
                                </div>
                            </div>
                        )}
                        <div className="flex items-center gap-2">
                            <Globe className="h-3.5 w-3.5" />
                            Target // {prompt.targetSites.join(", ") || "Agnostic"}
                        </div>
                    </div>
                </div>

                <div className="grid lg:grid-cols-3 gap-12 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-200">
                    {/* Left Column: Actions & Metadata */}
                    <div className="space-y-8 lg:sticky lg:top-24 h-fit">
                        <div className="p-6 rounded-xl border border-border bg-card shadow-sm space-y-4">
                            <div className="grid gap-3">
                                <CopyButton
                                    text={prompt.promptText}
                                    label="Copy Flow"
                                    variant="default"
                                    className="h-12 w-full bg-primary text-primary-foreground hover:bg-primary/90 font-bold uppercase tracking-widest text-xs"
                                />
                                <SaveButton 
                                    slug={prompt.slug}
                                    initialCount={prompt.saves_count ?? 0}
                                    className="h-12 w-full font-bold uppercase tracking-widest text-xs"
                                />
                            </div>

                            <div className="pt-4 border-t border-border flex justify-between items-center">
                                <LikeButton
                                    targetType="prompt"
                                    targetId={prompt.slug}
                                    initialCount={prompt.like_count ?? 0}
                                    size="sm"
                                    className="uppercase font-bold text-[10px]"
                                />
                                <Button variant="link" size="sm" className="h-auto p-0 text-[10px] uppercase font-bold text-muted-foreground hover:text-destructive">
                                    Report Flow
                                </Button>
                            </div>
                        </div>

                        {/* Admin Controls */}
                        <AdminControls slug={prompt.slug} />
                    </div>

                    {/* Right Column: Flow Steps */}
                    <div className="lg:col-span-2 space-y-12">
                        <div className="rounded-xl border border-border bg-card overflow-hidden">
                            <div className="border-b border-border bg-muted/30 px-6 py-4">
                                <h3 className="text-xs font-bold uppercase tracking-[0.3em] text-foreground flex items-center gap-2">
                                    <Layers className="h-3.5 w-3.5" /> Flow Steps
                                </h3>
                            </div>

                            <div className="p-8 space-y-8">
                                {/* Context */}
                                <div className="space-y-3">
                                    <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground/70 bg-secondary/50 px-2 py-1 rounded inline-block">Context</span>
                                    <p className="text-sm font-medium text-muted-foreground leading-relaxed">
                                        {prompt.notes || "No context provided. Run this flow in a compatible browser agent."}
                                    </p>
                                </div>

                                {/* Inputs */}
                                <div className="space-y-3">
                                    <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground/70 bg-secondary/50 px-2 py-1 rounded inline-block">Inputs</span>
                                    <div className="p-4 rounded-lg bg-secondary/20 border border-border/50 text-xs font-mono text-muted-foreground">
                                        {"// Standard inputs inferred"}
                                        <br /> TARGET_URL: &quot;{prompt.targetSites[0] || "Any"}&quot;
                                    </div>
                                </div>

                                {/* Actions */}
                                <div className="space-y-4">
                                    <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground/70 bg-secondary/50 px-2 py-1 rounded inline-block">Actions</span>
                                    <ol className="space-y-4">
                                        {prompt.steps.map((step: string, i: number) => (
                                            <li key={i} className="flex gap-4 group">
                                                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-secondary border border-border flex items-center justify-center font-bold text-[10px] text-muted-foreground">
                                                    {i + 1}
                                                </span>
                                                <p className="text-foreground/90 text-sm font-medium leading-relaxed pt-0.5">{step}</p>
                                            </li>
                                        ))}
                                        {prompt.steps.length === 0 && (
                                            <li className="text-muted-foreground text-sm italic">See prompt text for details.</li>
                                        )}
                                    </ol>
                                </div>

                                {/* Exit & Failure (Mocked/Static for now as per "stub" instruction) */}
                                <div className="grid sm:grid-cols-2 gap-6 pt-6 border-t border-border/40">
                                    <div className="space-y-2">
                                        <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground/70">Exit Condition</span>
                                        <p className="text-xs text-muted-foreground">Flow completes when all steps are verified.</p>
                                    </div>
                                    <div className="space-y-2">
                                        <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground/70">Failure Handling</span>
                                        <p className="text-xs text-muted-foreground">Stop on error. Notify user.</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Full Prompt Text (Hidden or Secondary?) - User didn't ask to hide it, but focused on "Steps Format". I'll keep it as "Raw Source" below */}
                        <div className="space-y-4">
                            <h3 className="text-xs font-bold uppercase tracking-[0.3em] text-muted-foreground">Raw Source</h3>
                            <div className="relative group">
                                <pre className="whitespace-pre-wrap break-words p-6 rounded-lg border border-border bg-muted/10 font-mono text-xs text-muted-foreground overflow-x-auto max-h-[300px] overflow-y-auto">
                                    {prompt.promptText}
                                </pre>
                                <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <CopyButton text={prompt.promptText} variant="secondary" className="h-8 text-[10px] uppercase font-bold" />
                                </div>
                            </div>
                        </div>

                        <CommentsSection promptSlug={prompt.slug} promptId={prompt.id} />
                    </div>
                </div>
            </div>
        </div>
    );
}
