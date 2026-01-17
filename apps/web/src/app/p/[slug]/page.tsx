import Link from "next/link";
import { fetchPrompt } from "@/lib/api";
import { notFound } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CopyButton } from "@/components/CopyButton";
import { Calendar, Layers, ArrowLeft } from "lucide-react";
import type { Metadata } from "next";

export async function generateMetadata(props: {
    params: { slug: string };
}): Promise<Metadata> {
    const prompt = await fetchPrompt(props.params.slug);

    if (!prompt) {
        return { title: "Prompt Not Found" };
    }

    return {
        title: prompt.title,
        description: prompt.summary,
    };
}

export default async function PromptDetailPage(props: { params: { slug: string } }) {
    const prompt = await fetchPrompt(props.params.slug);

    if (!prompt) {
        notFound();
    }

    const jsonString = JSON.stringify(prompt, null, 2);

    return (
        <div className="container py-12 max-w-4xl mx-auto px-4 min-h-screen">
            {/* Header */}
            <div className="space-y-6 mb-10 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <Link href="/library" className="inline-flex items-center text-sm text-muted-foreground hover:text-primary transition-colors mb-2">
                    <ArrowLeft className="mr-2 h-4 w-4" />
                    Back to Library
                </Link>
                <div className="flex flex-wrap items-center gap-2">
                    <Badge variant="outline" className="capitalize px-3 py-1 text-sm">{prompt.difficulty}</Badge>
                    {prompt.worksWith.map(w => (
                        <Badge key={w} variant="secondary" className="bg-primary/10 text-primary hover:bg-primary/20 border-primary/10 px-3 py-1 text-sm">
                            {w}
                        </Badge>
                    ))}
                </div>

                <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70 pb-2">
                    {prompt.title}
                </h1>

                <p className="text-xl text-muted-foreground max-w-2xl text-balance">
                    {prompt.summary}
                </p>

                <div className="flex flex-wrap gap-4 items-center text-sm text-muted-foreground pt-2">
                    <div className="flex items-center gap-1">
                        <Layers className="h-4 w-4" />
                        {prompt.tags.map(t => `#${t}`).join(", ")}
                    </div>
                    <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        Updated {new Date(prompt.updatedAt).toLocaleDateString()}
                    </div>
                </div>
            </div>

            <div className="grid gap-8 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-100">
                {/* Actions */}
                <div className="flex gap-4 sticky top-20 z-10 bg-background/80 backdrop-blur-md p-4 rounded-xl border border-border/40 shadow-sm -mx-4 px-4 md:mx-0 md:px-4">
                    <CopyButton text={prompt.promptText} label="Copy Prompt" variant="default" />
                    <CopyButton text={jsonString} label="Copy JSON" variant="outline" />
                </div>

                {/* Content */}
                <div className="grid gap-6">
                    <Card className="border-border/50 bg-card/60 backdrop-blur-sm overflow-hidden">
                        <CardHeader className="bg-muted/30 border-b border-border/40">
                            <CardTitle className="font-mono text-sm uppercase tracking-wider text-muted-foreground">Prompt Content</CardTitle>
                        </CardHeader>
                        <CardContent className="p-0">
                            <pre className="whitespace-pre-wrap break-words p-6 font-mono text-sm text-foreground/90 bg-muted/10 overflow-x-auto leading-relaxed">
                                {prompt.promptText}
                            </pre>
                        </CardContent>
                    </Card>

                    {prompt.steps && prompt.steps.length > 0 && (
                        <Card className="border-border/50 bg-card/60 backdrop-blur-sm">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    Steps
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <ol className="relative space-y-4 ml-2">
                                    {prompt.steps.map((step, i) => (
                                        <li key={i} className="pl-6 relative border-l-2 border-primary/20 hover:border-primary/50 transition-colors">
                                            <span className="absolute -left-[9px] top-0 h-4 w-4 rounded-full bg-background border-2 border-primary/50 text-[10px] flex items-center justify-center font-bold text-primary">
                                                {i + 1}
                                            </span>
                                            <p className="text-foreground/90">{step}</p>
                                        </li>
                                    ))}
                                </ol>
                            </CardContent>
                        </Card>
                    )}

                    {prompt.notes && (
                        <Card className="border-yellow-500/20 bg-yellow-500/5 dark:bg-yellow-500/10">
                            <CardHeader>
                                <CardTitle className="text-yellow-600 dark:text-yellow-400">Notes & Pitfalls</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-muted-foreground">{prompt.notes}</p>
                            </CardContent>
                        </Card>
                    )}
                </div>
            </div>
        </div>
    );
}
