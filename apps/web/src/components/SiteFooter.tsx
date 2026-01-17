import Link from "next/link";
import { Github, Twitter, Mail } from "lucide-react";

export function SiteFooter() {
    return (
        <footer className="border-t border-border/40 bg-background/80 backdrop-blur-sm mt-auto">
            <div className="container max-w-screen-2xl px-4 py-12">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                    {/* Brand */}
                    <div className="space-y-4">
                        <h3 className="font-bold text-lg bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-500">
                            Flowtab.Pro
                        </h3>
                        <p className="text-sm text-muted-foreground">
                            Automated browser prompt recipes for modern workflows
                        </p>
                    </div>

                    {/* Quick Links */}
                    <div className="space-y-4">
                        <h4 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground">
                            Explore
                        </h4>
                        <ul className="space-y-2 text-sm">
                            <li>
                                <Link href="/library" className="hover:text-primary transition-colors">
                                    Library
                                </Link>
                            </li>
                            <li>
                                <Link href="/submit" className="hover:text-primary transition-colors">
                                    Submit Prompt
                                </Link>
                            </li>
                            <li>
                                <Link href="/library?difficulty=beginner" className="hover:text-primary transition-colors">
                                    Beginner Prompts
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* Categories */}
                    <div className="space-y-4">
                        <h4 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground">
                            Popular Tags
                        </h4>
                        <ul className="space-y-2 text-sm">
                            <li>
                                <Link href="/library?tags=automation" className="hover:text-primary transition-colors">
                                    Automation
                                </Link>
                            </li>
                            <li>
                                <Link href="/library?tags=playwright" className="hover:text-primary transition-colors">
                                    Playwright
                                </Link>
                            </li>
                            <li>
                                <Link href="/library?tags=testing" className="hover:text-primary transition-colors">
                                    Testing
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* Connect */}
                    <div className="space-y-4">
                        <h4 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground">
                            Connect
                        </h4>
                        <div className="flex gap-4">
                            <a
                                href="https://github.com/flowtab/flowtab.pro"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-muted-foreground hover:text-primary transition-colors"
                                aria-label="GitHub"
                            >
                                <Github className="h-5 w-5" />
                            </a>
                            <a
                                href="https://twitter.com/flowtabpro"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-muted-foreground hover:text-primary transition-colors"
                                aria-label="Twitter"
                            >
                                <Twitter className="h-5 w-5" />
                            </a>
                            <a
                                href="mailto:hello@flowtab.pro"
                                className="text-muted-foreground hover:text-primary transition-colors"
                                aria-label="Email"
                            >
                                <Mail className="h-5 w-5" />
                            </a>
                        </div>
                    </div>
                </div>

                {/* Bottom bar */}
                <div className="mt-12 pt-8 border-t border-border/40 flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-muted-foreground">
                    <p>
                        © {new Date().getFullYear()} Flowtab.Pro. Built for the browser automation community.
                    </p>
                    <div className="flex gap-6">
                        <Link href="/privacy" className="hover:text-primary transition-colors">
                            Privacy
                        </Link>
                        <Link href="/terms" className="hover:text-primary transition-colors">
                            Terms
                        </Link>
                    </div>
                </div>
            </div>
        </footer>
    );
}
