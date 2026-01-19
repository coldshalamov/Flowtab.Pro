import Link from "next/link";
import { Mail, Github } from "lucide-react";

export function SiteFooter() {
    return (
        <footer className="border-t border-border/60 bg-muted/20">
            {/* Step 9: Activity Strip */}
            <div className="border-b border-border/40 bg-background/50 backdrop-blur-sm">
                <div className="container max-w-screen-2xl px-6 py-3 flex gap-8 items-center text-[10px] font-bold uppercase tracking-widest text-muted-foreground/60 overflow-x-auto whitespace-nowrap">
                    <span className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-primary/50"></span>
                        Activity
                    </span>
                    <span className="text-foreground/80">New Flows: —</span>
                    <span className="text-foreground/80">Featured: 5</span>
                    <span className="text-foreground/80">Community: — likes</span>
                </div>
            </div>

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
                            A prompt-first library for web automation playbooks.
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
                        </ul>
                    </div>

                    {/* Step 8: Collections */}
                    <div className="space-y-6">
                        <div className="space-y-4">
                            <h4 className="text-sm font-semibold text-foreground tracking-tight">
                                Collections
                            </h4>
                            <ul className="space-y-3 text-sm font-medium text-muted-foreground">
                                <li><Link href="/library?tags=dev,github" className="hover:text-foreground transition-colors">Dev / GitHub</Link></li>
                                <li><Link href="/library?tags=research" className="hover:text-foreground transition-colors">Research</Link></li>
                                <li><Link href="/library?tags=scraping" className="hover:text-foreground transition-colors">Scraping / Extraction</Link></li>
                                <li><Link href="/library?tags=ops" className="hover:text-foreground transition-colors">Ops / Admin</Link></li>
                                <li><Link href="/library?tags=outreach" className="hover:text-foreground transition-colors">Outreach / CRM</Link></li>
                                <li><Link href="/library?tags=shopping" className="hover:text-foreground transition-colors">Shopping / Monitoring</Link></li>
                                <li><Link href="/library?tags=social-media" className="hover:text-foreground transition-colors">Social Media</Link></li>
                            </ul>
                        </div>

                        {/* Step 8: Sidebar CTA (Placed here as requested "in sidebar" context implies navigation column) */}
                        <div className="p-4 rounded-lg bg-secondary/50 border border-border/50 space-y-2">
                            <p className="text-xs font-semibold text-foreground leading-snug">
                                Want a Flow for a task you can’t automate yet?
                            </p>
                            <a href="mailto:request@flowtab.pro" className="text-xs font-bold text-primary hover:underline block">
                                Request a Flow →
                            </a>
                        </div>
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
                                href="mailto:devteamrob.helix@gmail.com"
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
