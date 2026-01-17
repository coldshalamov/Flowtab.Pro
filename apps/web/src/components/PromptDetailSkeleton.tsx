import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function PromptDetailSkeleton() {
    return (
        <div className="container py-12 max-w-4xl mx-auto px-4 min-h-screen">
            {/* Header skeleton */}
            <div className="space-y-6 mb-10">
                <div className="flex flex-wrap items-center gap-2">
                    <Skeleton className="h-6 w-24 rounded-full" />
                    <Skeleton className="h-6 w-20 rounded-full" />
                    <Skeleton className="h-6 w-28 rounded-full" />
                </div>

                <Skeleton className="h-12 w-3/4" />
                <Skeleton className="h-6 w-full" />
                <Skeleton className="h-6 w-2/3" />

                <div className="flex gap-4 pt-2">
                    <Skeleton className="h-4 w-40" />
                    <Skeleton className="h-4 w-32" />
                </div>
            </div>

            <div className="grid gap-8">
                {/* Actions skeleton */}
                <div className="flex gap-4 p-4 rounded-xl border border-border/40">
                    <Skeleton className="h-10 w-32" />
                    <Skeleton className="h-10 w-28" />
                </div>

                {/* Content skeleton */}
                <Card className="border-border/50">
                    <CardHeader>
                        <Skeleton className="h-6 w-32" />
                    </CardHeader>
                    <CardContent className="p-6 space-y-2">
                        <Skeleton className="h-4 w-full" />
                        <Skeleton className="h-4 w-full" />
                        <Skeleton className="h-4 w-3/4" />
                        <Skeleton className="h-4 w-full" />
                        <Skeleton className="h-4 w-2/3" />
                    </CardContent>
                </Card>

                {/* Steps skeleton */}
                <Card className="border-border/50">
                    <CardHeader>
                        <Skeleton className="h-6 w-24" />
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {Array.from({ length: 4 }).map((_, i) => (
                            <div key={i} className="flex gap-2">
                                <Skeleton className="h-4 w-4 rounded-full shrink-0 mt-0.5" />
                                <Skeleton className="h-4 flex-1" />
                            </div>
                        ))}
                    </CardContent>
                </Card>

                {/* Notes skeleton */}
                <Card className="border-yellow-500/20">
                    <CardHeader>
                        <Skeleton className="h-6 w-32" />
                    </CardHeader>
                    <CardContent>
                        <Skeleton className="h-4 w-full" />
                        <Skeleton className="h-4 w-4/5 mt-2" />
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
