import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Plus, Heart } from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";

export function SiteHeader() {
    return (
        <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container flex h-16 max-w-screen-2xl items-center justify-between px-4">
                <div className="flex items-center gap-6">
                    <Link href="/" className="mr-6 flex items-center space-x-2">
                        <span className="font-bold text-xl bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-500">Flowtab.Pro</span>
                    </Link>
                    <nav className="hidden md:flex gap-6 text-sm font-medium">
                        <Link href="/library" className="transition-colors hover:text-primary text-muted-foreground">Library</Link>
                        <Link href="/submit" className="transition-colors hover:text-primary text-muted-foreground">Submit</Link>
                    </nav>
                </div>
                <div className="flex items-center gap-2">
                    <ThemeToggle />
                    <Link href="https://github.com/sponsors/flowtab" target="_blank" rel="noopener noreferrer">
                        <Button variant="ghost" size="sm" className="hidden sm:flex text-muted-foreground hover:text-red-500 hover:bg-red-500/10 gap-2">
                            <Heart className="h-4 w-4" />
                            <span>Sponsor</span>
                        </Button>
                    </Link>
                    <Link href="/submit">
                        <Button size="sm" className="h-8 gap-1">
                            <Plus className="h-3.5 w-3.5" />
                            <span className="hidden sm:inline">Submit Prompt</span>
                        </Button>
                    </Link>
                </div>
            </div>
        </header>
    );
}
