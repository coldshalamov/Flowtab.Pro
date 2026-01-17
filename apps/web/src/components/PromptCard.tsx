import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { type Prompt } from "@/lib/api";
import { cn } from "@/lib/utils";

export function PromptCard({ prompt }: { prompt: Prompt }) {
    const worksWith = prompt.worksWith.map(w => w.toLowerCase());

    return (
        <Link href={`/p/${prompt.slug}`} className="group block h-full">
            <Card className="h-full transition-all duration-300 bg-card border-border hover:border-foreground/20 hover:shadow-md rounded-lg overflow-hidden flex flex-col">
                <CardHeader className="space-y-4 pb-4">
                    <div className="flex justify-between items-start gap-4">
                        <div className="flex -space-x-1.5 overflow-hidden">
                            {worksWith.some(w => w.includes('comet')) && (
                                <div className="h-6 w-6 rounded-full bg-secondary border border-background flex items-center justify-center text-[10px] font-bold text-muted-foreground" title="Comet">C</div>
                            )}
                            {worksWith.some(w => w.includes('playwright')) && (
                                <div className="h-6 w-6 rounded-full bg-secondary border border-background flex items-center justify-center text-[10px] font-bold text-muted-foreground" title="Playwright">P</div>
                            )}
                            {worksWith.some(w => w.includes('neon')) && (
                                <div className="h-6 w-6 rounded-full bg-secondary border border-background flex items-center justify-center text-[10px] font-bold text-muted-foreground" title="Neon">N</div>
                            )}
                        </div>
                    </div>

                    <CardTitle className="text-xl font-bold tracking-tight text-foreground group-hover:text-primary transition-colors line-clamp-2">
                        {prompt.title}
                    </CardTitle>
                </CardHeader>

                <CardContent className="space-y-6 flex-1 flex flex-col">
                    <CardDescription className="text-muted-foreground font-medium leading-relaxed line-clamp-3">
                        {prompt.summary}
                    </CardDescription>

                    <div className="mt-auto pt-4 flex flex-wrap gap-2 text-xs">
                        {prompt.tags.slice(0, 3).map((tag: string) => (
                            <Badge key={tag} variant="secondary" className="bg-secondary/50 text-secondary-foreground hover:bg-secondary rounded-md font-medium px-2 py-0.5">
                                #{tag}
                            </Badge>
                        ))}
                        {prompt.tags.length > 3 && (
                            <span className="text-xs text-muted-foreground font-medium flex items-center pl-1">
                                +{prompt.tags.length - 3}
                            </span>
                        )}
                    </div>
                </CardContent>
            </Card>
        </Link>
    );
}
