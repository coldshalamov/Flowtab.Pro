import Link from "next/link";
import { fetchPrompt } from "@/lib/api";
import { notFound } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CopyButton } from "@/components/CopyButton";
import { Layers, ChevronLeft, Clock, Globe } from "lucide-react";
import type { Metadata } from "next";

export async function generateMetadata(props: {
    params: Promise<{ slug: string }> | { slug: string };
}): Promise<Metadata> {
    const params = await Promise.resolve(props.params);
    const prompt = await fetchPrompt(params.slug);
    if (!prompt) return { title: "Prompt Not Found" };
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
                <div className="space-y-8 mb-16 animate-in fade-in slide-in-from-bottom-8 duration-700">
                    <h1 className="text-5xl md:text-7xl font-bold tracking-tighter text-foreground uppercase leading-[0.9]">
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
                        <div className="flex items-center gap-2">
                            <Globe className="h-3.5 w-3.5" />
                            Target // {prompt.targetSites.join(", ") || "Agnostic"}
                        </div>
                    </div>
                </div>

                <div className="grid gap-12 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-200">
                    {/* Actions Panel */}
                    <div className="grid sm:grid-cols-2 gap-4 sticky top-20 z-20 bg-background/80 backdrop-blur-md p-4 -mx-4 rounded-lg border border-border/40 shadow-sm">
                        <CopyButton
                            text={prompt.promptText}
                            label="Copy Prompt"
                            variant="default"
                            className="h-12 bg-foreground text-background hover:bg-foreground/90 font-bold uppercase tracking-widest text-xs"
                        />
                        <CopyButton
                            text={jsonString}
                            label="Copy Metadata"
                            variant="outline"
                            className="h-12 border-border font-bold uppercase tracking-widest text-xs"
                        />
                    </div>

                    <div className="grid gap-12">
                        {/* Source Payload */}
                        <Card className="rounded-lg border-border bg-card overflow-hidden">
                            <CardHeader className="border-b border-border bg-muted/30 py-4">
                                <CardTitle className="text-[10px] font-bold uppercase tracking-[0.3em] text-muted-foreground flex items-center gap-3">
                                    <Layers className="h-3.5 w-3.5" />
                                    Source Payload
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="p-0">
                                <pre className="whitespace-pre-wrap break-words p-8 font-mono text-sm text-foreground/80 overflow-x-auto leading-relaxed selection:bg-primary/20 bg-muted/10">
                                    {prompt.promptText}
                                </pre>
                            </CardContent>
                        </Card>

                        <div className="grid lg:grid-cols-5 gap-12">
                            {/* Execution Steps */}
                            <div className="lg:col-span-3 space-y-8">
                                <h3 className="text-xs font-bold uppercase tracking-[0.3em] text-foreground">Operational sequence</h3>
                                <ol className="space-y-6">
                                    {prompt.steps.map((step: string, i: number) => (
                                        <li key={i} className="flex gap-6 group">
                                            <span className="flex-shrink-0 w-8 h-8 rounded-md bg-secondary border border-border flex items-center justify-center font-bold text-xs text-muted-foreground group-hover:bg-foreground group-hover:text-background transition-all">
                                                {i + 1}
                                            </span>
                                            <p className="text-muted-foreground font-medium pt-1.5 leading-relaxed">{step}</p>
                                        </li>
                                    ))}
                                </ol>
                            </div>

                            {/* Tags and Notes */}
                            <div className="lg:col-span-2 space-y-12">
                                <div className="space-y-6">
                                    <h3 className="text-xs font-bold uppercase tracking-[0.3em] text-foreground">Keywords</h3>
                                    <div className="flex flex-wrap gap-2">
                                        {prompt.tags.map((tag: string) => (
                                            <div key={tag} className="px-3 py-1.5 rounded-md bg-secondary border border-border text-[11px] font-bold uppercase tracking-widest text-muted-foreground">
                                                #{tag}
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {prompt.notes && (
                                    <div className="space-y-6">
                                        <h3 className="text-xs font-bold uppercase tracking-[0.3em] text-foreground">Operational Anomalies</h3>
                                        <div className="p-6 rounded-lg border border-border bg-muted/20 italic text-muted-foreground font-medium text-sm leading-relaxed border-l-4 border-l-primary">
                                            &quot;{prompt.notes}&quot;
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
