import Link from "next/link";
import { Prompt } from "@/lib/apiTypes";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface PromptCardProps {
    prompt: Prompt;
}

export function PromptCard({ prompt }: PromptCardProps) {
    const difficultyColor = {
        beginner: "bg-green-500/10 text-green-500 hover:bg-green-500/20 border-green-500/20",
        intermediate: "bg-yellow-500/10 text-yellow-500 hover:bg-yellow-500/20 border-yellow-500/20",
        advanced: "bg-red-500/10 text-red-500 hover:bg-red-500/20 border-red-500/20",
    }[prompt.difficulty] || "bg-secondary text-secondary-foreground";

    return (
        <Link href={`/p/${prompt.slug}`} className="block transition-all hover:scale-[1.02] group">
            <Card className="relative h-full border-muted-foreground/10 bg-card/50 backdrop-blur-sm hover:border-primary/50 transition-all duration-300 dark:bg-card/40 overflow-hidden">
                {/* CSS Gradient Accent (works better than image) */}
                <div className="absolute -top-20 -right-20 w-40 h-40 rounded-full bg-gradient-to-br from-purple-500/20 via-cyan-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-2xl" />

                <CardHeader className="relative z-10">
                    <div className="flex justify-between items-start gap-4">
                        <CardTitle className="text-xl font-bold tracking-tight text-foreground/90">
                            {prompt.title}
                        </CardTitle>
                        <Badge variant="outline" className={cn("capitalize border shrink-0", difficultyColor)}>
                            {prompt.difficulty}
                        </Badge>
                    </div>
                    <CardDescription className="line-clamp-2 text-muted-foreground">
                        {prompt.summary}
                    </CardDescription>
                </CardHeader>
                <CardContent className="relative z-10">
                    <div className="flex flex-wrap gap-2 mb-4">
                        {prompt.worksWith.map((tool) => (
                            <Badge key={tool} variant="secondary" className="bg-gradient-to-r from-primary/5 to-primary/10 text-primary border-primary/10 hover:from-primary/10 hover:to-primary/15 transition-all">
                                {tool}
                            </Badge>
                        ))}
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                        {prompt.tags.slice(0, 3).map((tag) => (
                            <span key={tag} className="text-xs text-muted-foreground/70 bg-muted/50 px-2 py-1 rounded-full hover:bg-muted transition-colors">
                                #{tag}
                            </span>
                        ))}
                        {prompt.tags.length > 3 && (
                            <span className="text-xs text-muted-foreground/70 px-1 py-1">
                                +{prompt.tags.length - 3}
                            </span>
                        )}
                    </div>
                </CardContent>

                {/* Bottom accent line */}
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-primary/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            </Card>
        </Link>
    );
}
