import Link from "next/link";
import { Github, Twitter, Mail } from "lucide-react";

export function SiteFooter() {
    return (
        <footer className="border-t border-border/60 bg-muted/20">
            <div className="container max-w-screen-2xl px-6 py-16">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
                    {/* Brand */}
                    <div className="space-y-4">
                        <div className="flex items-center space-x-2.5">
                            <div className="w-4 h-4 bg-primary rounded-sm" />
                            <h3 className="font-semibold text-base tracking-tight text-foreground">
                                Flowtab.Pro
                            </h3>
                        </div>
                        <p className="text-sm text-muted-foreground leading-relaxed max-w-xs font-medium">
                            The repository for high-precision browser automation.
                            Built for the next generation of web agents.
                        </p>
                    </div>

                    {/* Quick Links */}
                    <div className="space-y-4">
                        <h4 className="text-sm font-semibold text-foreground tracking-tight">
                            Platform
                        </h4>
                        <ul className="space-y-3 text-sm font-medium text-muted-foreground">
                            <li>
                                <Link href="/library" className="hover:text-foreground transition-colors">
                                    Library
                                </Link>
                            </li>
                            <li>
                                <Link href="/submit" className="hover:text-foreground transition-colors">
                                    Submit
                                </Link>
                            </li>
                            <li>
                                <Link href="/library?difficulty=beginner" className="hover:text-foreground transition-colors">
                                    Tutorials
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* Categories */}
                    <div className="space-y-4">
                        <h4 className="text-sm font-semibold text-foreground tracking-tight">
                            Collections
                        </h4>
                        <ul className="space-y-3 text-sm font-medium text-muted-foreground">
                            <li>
                                <Link href="/library?tags=automation" className="hover:text-foreground transition-colors">
                                    Automation
                                </Link>
                            </li>
                            <li>
                                <Link href="/library?tags=playwright" className="hover:text-foreground transition-colors">
                                    Playwright
                                </Link>
                            </li>
                            <li>
                                <Link href="/library?tags=testing" className="hover:text-foreground transition-colors">
                                    Testing
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* Connect */}
                    <div className="space-y-4">
                        <h4 className="text-sm font-semibold text-foreground tracking-tight">
                            Connect
                        </h4>
                        <div className="flex gap-4">
                            <a
                                href="https://github.com/coldshalamov/Flowtab.Pro"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="w-10 h-10 flex items-center justify-center rounded-md border border-border bg-background hover:bg-secondary hover:border-foreground/20 text-muted-foreground hover:text-foreground transition-all"
                                aria-label="GitHub"
                            >
                                <Github className="h-4 w-4" />
                            </a>
                            <a
                                href="https://twitter.com/flowtabpro"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="w-10 h-10 flex items-center justify-center rounded-md border border-border bg-background hover:bg-secondary hover:border-foreground/20 text-muted-foreground hover:text-foreground transition-all"
                                aria-label="Twitter"
                            >
                                <Twitter className="h-4 w-4" />
                            </a>
                            <a
                                href="mailto:hello@flowtab.pro"
                                className="w-10 h-10 flex items-center justify-center rounded-md border border-border bg-background hover:bg-secondary hover:border-foreground/20 text-muted-foreground hover:text-foreground transition-all"
                                aria-label="Email"
                            >
                                <Mail className="h-4 w-4" />
                            </a>
                        </div>
                    </div>
                </div>

                {/* Bottom bar */}
                <div className="mt-16 pt-8 border-t border-border/40 flex flex-col md:flex-row justify-between items-center gap-6 text-sm font-medium text-muted-foreground/60">
                    <p>
                        © {new Date().getFullYear()} Flowtab.Pro Inc.
                    </p>
                    <div className="flex gap-8">
                        <Link href="/privacy" className="hover:text-foreground transition-colors">
                            Privacy
                        </Link>
                        <Link href="/terms" className="hover:text-foreground transition-colors">
                            Terms
                        </Link>
                    </div>
                </div>
            </div>
        </footer>
    );
}
