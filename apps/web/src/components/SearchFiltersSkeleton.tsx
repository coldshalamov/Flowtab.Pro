import { Skeleton } from "@/components/ui/skeleton";

export function SearchFiltersSkeleton() {
    return (
        <div className="space-y-6 bg-card/50 p-6 rounded-xl border border-border/50 backdrop-blur-sm">
            <Skeleton className="h-10 w-full rounded-lg" />

            <div className="flex flex-col md:flex-row gap-8">
                <div className="space-y-3 flex-1">
                    <Skeleton className="h-4 w-20" />
                    <div className="flex gap-2">
                        <Skeleton className="h-9 w-24 rounded-md" />
                        <Skeleton className="h-9 w-28 rounded-md" />
                        <Skeleton className="h-9 w-24 rounded-md" />
                    </div>
                </div>

                <div className="space-y-3 flex-1">
                    <Skeleton className="h-4 w-24" />
                    <div className="flex gap-2">
                        <Skeleton className="h-9 w-20 rounded-md" />
                        <Skeleton className="h-9 w-28 rounded-md" />
                        <Skeleton className="h-9 w-20 rounded-md" />
                        <Skeleton className="h-9 w-24 rounded-md" />
                    </div>
                </div>
            </div>

            <div className="space-y-3">
                <Skeleton className="h-4 w-28" />
                <div className="flex flex-wrap gap-2">
                    {Array.from({ length: 8 }).map((_, i) => (
                        <Skeleton key={i} className="h-7 w-20 rounded-full" />
                    ))}
                </div>
            </div>
        </div>
    );
}
