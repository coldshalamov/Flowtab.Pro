import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { type Prompt } from "@/lib/api";
import { Heart, Bookmark, BarChart } from "lucide-react"; // Using BarChart as placeholder for difficulty or just text
import Image from "next/image";

const WORKS_WITH_MAP: Record<string, string> = {
    "comet": "/images/logos/comet.webp",
    "manus": "/images/logos/manus.png",
    "neon": "/images/logos/neon.jpg",
    "playwright": "/images/logos/playwright.png",
    "atlas": "/images/logos/atlas.png",
};

export function PromptCard({ prompt }: { prompt: Prompt }) {
    const isDraft = prompt.tags.includes("Draft") || prompt.title.includes("Draft");
    const creatorName = prompt.author_id || "Flowtab";
    const lastUpdated = prompt.updatedAt
        ? new Date(prompt.updatedAt).toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
            year: "numeric",
        })
        : "Unknown";
    const stepsCount = prompt.steps?.length || 0;
    const estimatedMinutes = stepsCount > 0 ? Math.max(1, Math.round(stepsCount * 2)) : null;

    // Normalize worksWith to lowercase for mapping
    const worksWithLogos = (prompt.worksWith || []).map(w => ({
        name: w,
        src: WORKS_WITH_MAP[w.toLowerCase()]
    })).filter(w => w.src); // Only show if we have a logo? Or show text? User said "Works with icons (small)"

    return (
        <Link href={`/p/${prompt.slug}`} className="group block h-full">
            <Card className="h-full transition-all duration-200 bg-card border-border hover:border-primary/50 hover:shadow-lg rounded-xl overflow-hidden flex flex-col relative group-hover:-translate-y-1">
                {isDraft && (
                    <div className="absolute top-3 right-3 z-10">
                        <Badge variant="outline" className="bg-background/80 backdrop-blur text-[10px] uppercase tracking-widest text-muted-foreground border-border">
                            Draft
                        </Badge>
                    </div>
                )}

                <CardHeader className="space-y-1.5 pb-3">
                    <CardTitle className="text-lg font-bold tracking-tight text-foreground group-hover:text-primary transition-colors line-clamp-1">
                        {prompt.title}
                    </CardTitle>
                    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-muted-foreground/80 sm:text-xs">
                        <span className="truncate">By {creatorName}</span>
                        <span>Updated {lastUpdated}</span>
                        <span>
                            {estimatedMinutes ? `Est. ${estimatedMinutes} min` : "Est. —"} · {stepsCount}{" "}
                            {stepsCount === 1 ? "step" : "steps"}
                        </span>
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-1 font-medium">
                        {prompt.summary}
                    </p>
                </CardHeader>

                <CardContent className="space-y-6 flex-1 flex flex-col justify-between">
                    {/* Tags */}
                    <div className="flex flex-wrap gap-1.5">
                        {prompt.tags.filter(t => t !== 'Draft').slice(0, 3).map((tag: string) => (
                            <Badge key={tag} variant="secondary" className="bg-secondary text-secondary-foreground/80 hover:bg-secondary-foreground/10 rounded-md font-medium text-[10px] px-2 h-6">
                                {tag}
                            </Badge>
                        ))}
                        {prompt.tags.filter(t => t !== 'Draft').length > 3 && (
                            <Badge variant="secondary" className="bg-secondary text-muted-foreground rounded-md font-medium text-[10px] px-2 h-6">
                                +{prompt.tags.filter(t => t !== 'Draft').length - 3}
                            </Badge>
                        )}
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-border/40 mt-auto">
                        <div className="flex items-center gap-2">
                            {/* Works With logos removed as per request */}
                        </div>

                        <div className="flex items-center gap-3 text-xs font-medium text-muted-foreground/60">

                            <div className="flex items-center gap-1">
                                <Heart className="h-3 w-3" /> {prompt.like_count || 0}
                            </div>
                            <div className="flex items-center gap-1">
                                <Bookmark className="h-3 w-3" /> {prompt.savesCount || 0}
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </Link>
    );
}
