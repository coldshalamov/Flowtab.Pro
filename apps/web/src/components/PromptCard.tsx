import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { type Prompt } from "@/lib/api";
import { Clock, Globe } from "lucide-react";

export function PromptCard({ prompt }: { prompt: Prompt }) {
    const updatedLabel = new Date(prompt.updatedAt).toLocaleDateString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
    });

    const targetsLabel =
        prompt.targetSites && prompt.targetSites.length > 0
            ? prompt.targetSites.length === 1
                ? prompt.targetSites[0]
                : `${prompt.targetSites[0]} +${prompt.targetSites.length - 1}`
            : "Agnostic";

    return (
        <Link href={`/p/${prompt.slug}`} className="group block h-full">
            <Card className="h-full transition-all duration-300 bg-card border-border hover:border-foreground/20 hover:shadow-md rounded-lg overflow-hidden flex flex-col">
                <CardHeader className="space-y-3 pb-4">
                    <CardTitle className="text-xl font-bold tracking-tight text-foreground group-hover:text-primary transition-colors line-clamp-2">
                        {prompt.title}
                    </CardTitle>
                </CardHeader>

                <CardContent className="space-y-6 flex-1 flex flex-col">
                    <CardDescription className="text-muted-foreground font-medium leading-relaxed line-clamp-3">
                        {prompt.summary}
                    </CardDescription>

                    <div className="flex flex-wrap gap-4 text-[10px] font-bold uppercase tracking-widest text-muted-foreground/60">
                        <div className="flex items-center gap-1.5">
                            <Clock className="h-3.5 w-3.5" />
                            Updated {updatedLabel}
                        </div>
                        <div className="flex items-center gap-1.5">
                            <Globe className="h-3.5 w-3.5" />
                            {targetsLabel}
                        </div>
                    </div>

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
