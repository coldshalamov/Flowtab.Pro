import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Plus, Heart } from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";

export function SiteHeader() {
    return (
        <header className="sticky top-0 z-50 w-full glass-panel border-b border-border/60">
            <div className="container flex h-14 max-w-screen-2xl items-center justify-between px-6">
                <div className="flex items-center gap-8">
                    <Link href="/" className="flex items-center space-x-2.5">
                        <div className="w-5 h-5 bg-primary rounded-sm" />
                        <span className="font-medium text-lg tracking-tight text-foreground">
                            Flowtab<span className="text-muted-foreground/60">.Pro</span>
                        </span>
                    </Link>
                    <nav className="hidden md:flex gap-6 text-[13px] font-medium text-muted-foreground">
                        <Link href="/library" className="hover:text-foreground transition-colors">Library</Link>
                        <Link href="/submit" className="hover:text-foreground transition-colors">Submit</Link>
                    </nav>
                </div>
                <div className="flex items-center gap-3">
                    <ThemeToggle />
                    <div className="h-4 w-px bg-border/60 mx-1" />
                    <Link href="https://github.com/sponsors/coldshalamov" target="_blank" rel="noopener noreferrer">
                        <Button variant="ghost" size="sm" className="hidden sm:flex h-8 px-3 text-muted-foreground hover:text-foreground gap-2 text-xs font-medium">
                            <Heart className="h-3.5 w-3.5 text-muted-foreground group-hover:text-red-500 transition-colors" />
                            <span>Sponsor</span>
                        </Button>
                    </Link>
                    <Link href="/submit">
                        <Button size="sm" className="h-8 px-4 bg-primary text-primary-foreground hover:bg-primary/90 rounded-md text-xs font-medium shadow-sm">
                            <Plus className="h-3.5 w-3.5 mr-1.5" />
                            <span className="hidden sm:inline">Add Recipe</span>
                        </Button>
                    </Link>
                </div>
            </div>
        </header>
    );
}


