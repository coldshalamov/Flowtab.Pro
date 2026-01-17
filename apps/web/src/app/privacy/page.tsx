import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy",
  description: "Privacy policy for Flowtab.Pro.",
};

export default function PrivacyPage() {
  return (
    <div className="container py-10 max-w-3xl mx-auto px-4">
      <h1 className="text-3xl font-bold tracking-tight mb-4">Privacy Policy</h1>
      <p className="text-muted-foreground mb-6">
        This page is a placeholder privacy policy. Replace it with your actual
        policy before launching publicly.
      </p>
      <div className="space-y-4 text-sm leading-relaxed text-foreground/90">
        <p>
          Flowtab.Pro may collect basic usage data (e.g., page views) to improve
          the product. If you add analytics, disclose what you collect and why.
        </p>
        <p>
          Submissions you provide (prompt recipes) may be stored and displayed
          publicly after review.
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
