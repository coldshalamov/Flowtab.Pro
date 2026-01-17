import { Prompt } from "./apiTypes";

export const MOCK_PROMPTS: Prompt[] = [
    {
        id: "1",
        slug: "linkedin-outreach",
        title: "LinkedIn Automated Outreach",
        summary: "Navigates LinkedIn to send connection requests with personalized notes to a list of profiles.",
        difficulty: "intermediate",
        worksWith: ["Comet", "Playwright MCP"],
        tags: ["social", "automation", "outreach"],
        targetSites: ["linkedin.com"],
        promptText: "Go to linkedin.com and search for 'CTO'. For the first 5 results, visit their profile, click Connect, and add a note saying 'Hi, I found your profile interesting...'",
        steps: [
            "Login to LinkedIn",
            "Search for target role",
            "Iterate through results",
            "Send connection request with note"
        ],
        notes: "Watch out for daily limits aggressively enforced by LinkedIn.",
        createdAt: "2025-11-15T10:00:00Z",
        updatedAt: "2025-12-01T14:30:00Z"
    },
    {
        id: "2",
        slug: "flight-price-monitor",
        title: "Daily Flight Price Monitor",
        summary: "Checks Google Flights for round-trip tickets from NYC to London and screenshots the price matrix.",
        difficulty: "beginner",
        worksWith: ["Opera Neon", "Generic"],
        tags: ["travel", "monitoring", "saving"],
        targetSites: ["google.com/flights"],
        promptText: "Open Google Flights. Select round trip from JFK to LHR. Set dates for next month. Capture a screenshot of the price graph.",
        steps: [
            "Navigate to Google Flights",
            "Input NYC and London",
            "Select dates",
            "Take screenshot"
        ],
        notes: "Google Flights classes change frequently, rely on visual selectors if possible or accessible ARIA labels.",
        createdAt: "2025-10-20T09:00:00Z",
        updatedAt: "2025-10-20T09:00:00Z"
    },
    {
        id: "3",
        slug: "github-repo-summarizer",
        title: "GitHub Repo Deep Summary",
        summary: "Navigates a GitHub repository, reading the README, issues, and recent commits to generate a summary.",
        difficulty: "advanced",
        worksWith: ["Comet", "LLM Native"],
        tags: ["dev", "summary", "research"],
        targetSites: ["github.com"],
        promptText: "Visit the provided GitHub repository. Read the README.md. detailedly. Then go to the Issues tab and summarize the top 3 open issues. Finally check the last commit message.",
        steps: [
            "Read README",
            "Analyze Issues",
            "Check Commits",
            "Synthesize Report"
        ],
        notes: "Requires authenticated session if the repo is private or to avoid rate limits.",
        createdAt: "2026-01-05T08:15:00Z",
        updatedAt: "2026-01-10T11:20:00Z"
    }
];

export const MOCK_TAGS = ["social", "automation", "outreach", "travel", "monitoring", "saving", "dev", "summary", "research"];
