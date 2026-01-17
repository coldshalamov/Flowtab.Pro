import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Home, Search as SearchIcon } from "lucide-react";

export default function NotFound() {
    return (
        <div className="container flex flex-col items-center justify-center min-h-[calc(100vh-8rem)] px-4 text-center">
            <div className="space-y-8 max-w-2xl">
                <div className="space-y-4">
                    <h1 className="text-9xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-red-500 via-purple-500 to-blue-500 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        404
                    </h1>
                    <h2 className="text-3xl font-bold tracking-tight animate-in fade-in slide-in-from-bottom-6 duration-700 delay-100">
                        Prompt Not Found
                    </h2>
                    <p className="text-lg text-muted-foreground animate-in fade-in slide-in-from-bottom-8 duration-700 delay-200">
                        Looks like this prompt escaped into the void. Don&apos;t worry, we have plenty more automation recipes to explore!
                    </p>
                </div>

                <div className="flex flex-col sm:flex-row gap-4 justify-center animate-in fade-in slide-in-from-bottom-10 duration-700 delay-300">
                    <Link href="/">
                        <Button size="lg" className="gap-2">
                            <Home className="h-5 w-5" />
                            Back to Home
                        </Button>
                    </Link>
                    <Link href="/library">
                        <Button size="lg" variant="outline" className="gap-2">
                            <SearchIcon className="h-5 w-5" />
                            Browse Library
                        </Button>
                    </Link>
                </div>

                <div className="pt-8 border-t border-border/40 animate-in fade-in duration-1000 delay-500">
                    <p className="text-sm text-muted-foreground mb-4">
                        Popular prompts you might be interested in:
                    </p>
                    <div className="flex flex-wrap gap-2 justify-center">
                        {["automation", "browser", "playwright", "comet", "testing"].map((tag) => (
                            <Link key={tag} href={`/library?tags=${tag}`}>
                                <span className="text-xs bg-primary/10 text-primary px-3 py-1.5 rounded-full hover:bg-primary/20 transition-colors cursor-pointer">
                                    #{tag}
                                </span>
                            </Link>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
