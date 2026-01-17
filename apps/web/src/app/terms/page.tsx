import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms",
  description: "Terms of service for Flowtab.Pro.",
};

export default function TermsPage() {
  return (
    <div className="container py-10 max-w-3xl mx-auto px-4">
      <h1 className="text-3xl font-bold tracking-tight mb-4">Terms of Service</h1>
      <p className="text-muted-foreground mb-6">
        This page is a placeholder terms of service. Replace it with your
        actual terms before launching publicly.
      </p>
      <div className="space-y-4 text-sm leading-relaxed text-foreground/90">
        <p>
          By using Flowtab.Pro you agree not to use the site for unlawful or
          harmful automation.
        </p>
        <p>
          Content submitted may be moderated, edited, or removed at our
          discretion.
        </p>
        <p>
          Contact:{" "}
          <a
            className="underline underline-offset-4"
            href="mailto:hello@flowtab.pro"
          >
            hello@flowtab.pro
          </a>
        </p>
      </div>
    </div>
  );
}
