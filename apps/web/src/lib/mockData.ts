import { Prompt } from "./apiTypes";

export const MOCK_PROMPTS: Prompt[] = [
    {
        id: "1",
        slug: "resolve-github-merge-conflicts",
        title: "GitHub Conflict Resolution Shortcut",
        summary: "Resolve all merge conflicts in one file as fast as possible by reading the full text via DOM, resolving intelligently, and pasting back the complete solution.",
        difficulty: "advanced",
        worksWith: [],
        tags: ["featured", "dev", "github"],
        targetSites: ["github.com"],
        promptText: `## **GitHub Conflict Resolution Shortcut - Optimized for Speed**

**Objective:** Resolve all merge conflicts in one file as fast as possible by reading the full text via DOM, resolving intelligently, and pasting back the complete solution.

***

### **Step 1: Extract the full conflicting file**

1. Locate the GitHub conflict editor (the editable code area showing the file \`frontend/src/components/Bank.jsx\` or similar).
2. Use \`get_page_text\` or \`read_page\` to extract the **entire file content** including all conflict markers (\`<<<<<<<\`, \`=======\`, \`>>>>>>>\`).
3. **Do NOT scroll, screenshot, or click individual "Accept current/incoming change" buttons.** Work entirely from the extracted text.

***

### **Step 2: Understand the codebase context**

This is a **React + wagmi + viem** project (AlphaHelix). The conflicts typically occur in:
- React hooks (\`useState\`, \`useEffect\`, \`useMemo\`)
- wagmi hooks (\`useAccount\`, \`useBalance\`, \`useReadContract\`, \`useWriteContract\`, \`useWaitForTransactionReceipt\`, \`usePublicClient\`)
- State variable declarations
- Comments explaining types or functionality

**Key principle:** Both branches usually add valid functionality. Your job is to **combine compatible changes** rather than discarding one side unless they're mutually exclusive.

***

### **Step 3: Resolve each conflict region intelligently**

For each conflict block:

\`\`\`
<<<<<<< palette-bank-ux-17692309166053110063 (or similar branch)
urrent version>
=======
<incoming version>
>>>>>>> main (or other branch)
\`\`\`

**Resolution rules:**

1. **Identical lines with different comments:** Keep the line once, preserve the more descriptive comment.
   - Example: If current has \`const [activeAction, setActiveAction] = useState(null);\` and incoming adds \`// 'buy' | 'sell'\`, the resolved version is:
     \`\`\`javascript
     const [activeAction, setActiveAction] = useState(null); // 'buy' | 'sell'
     \`\`\`

2. **New state variables or hooks:** If one branch adds a new \`useState\` or hook that doesn't conflict with existing code, **keep it**.

3. **Import changes:** Merge all unique imports from both sides. Remove duplicates.

4. **Logic changes:** If both sides modify the same function or JSX, analyze which change is more complete or combines both intents. Prefer the version that:
   - Adds more functionality without breaking existing features
   - Includes better error handling or type annotations
   - Has more descriptive variable names or comments

5. **Type annotations and comments:** Always preserve inline comments like \`// 'buy' | 'sell'\` as they document expected values.

***

### **Step 4: Construct the resolved file**

- Remove **all** conflict markers (\`<<<<<<<\`, \`=======\`, \`>>>>>>>\`).
- Ensure the file is valid JavaScript/TypeScript with correct syntax.
- Maintain consistent style:
  - 2-space indentation (based on the screenshot)
  - Single quotes for strings
  - Semicolons at statement ends
- Verify all imports at the top are deduplicated and used.
- Confirm all React hooks follow Rules of Hooks (correct order, no conditionals).

### **Example Scenario**

\`\`\`javascript
<<<<<<< palette-bank-ux-17692309166053110063
const [activeAction, setActiveAction] = useState(null);
=======
const [activeAction, setActiveAction] = useState(null); // 'buy' | 'sell'
>>>>>>> main
\`\`\`

**Resolved:**

\`\`\`javascript
const [activeAction, setActiveAction] = useState(null); // 'buy' | 'sell'
\`\`\`

**Reasoning:** Both versions declare the same state. The \`main\` branch adds a helpful comment documenting the expected values. Keep both the declaration and the comment.

***

### **Step 5: Replace editor content in one shot**

1. Select all text in the GitHub conflict editor (via DOM manipulation or \`ctrl+a\`).
2. Paste the **entire resolved file** content.
3. **Self-check:**
   - No \`<<<<<<<\`, \`=======\`, \`>>>>>>>\` remain.
   - File starts with imports and ends with \`export default function Bank() { ... }\` (or equivalent).
   - No syntax errors visible.

***

### **Step 6: Mark as resolved and complete the merge**

1. Click **"Mark as resolved"** button (top right above the editor).
2. You'll be returned to the PR page automatically.
3. If the PR shows a **"Ready for review"** button (draft PR), click it.
4. Click **"Merge PR"** or **"Squash and merge"** to complete.

**Do NOT commit prematurely.** Ensure all conflicts in all files are resolved first.

***

### **Performance constraints**

- **No scrolling** to hunt for conflicts.
- **No screenshots** unless something fails.
- **One extract → one transform → one paste** per file.
- If a conflict is ambiguous (business logic unclear), leave it with a comment:
  \`\`\`javascript
  // TODO: Unclear which version is correct - please review:
  // Option A: urrent code>
  // Option B: <incoming code>
  \`\`\`
  But this should be **rare**. Most conflicts in this repo are hook declarations or state additions that can be safely combined.

***

### **Example resolution for the current conflict**

From the screenshot, the conflict is:[1]

\`\`\`javascript
<<<<<<< palette-bank-ux-17692309166053110063
const [activeAction, setActiveAction] = useState(null);
=======
const [activeAction, setActiveAction] = useState(null); // 'buy' | 'sell'
>>>>>>> main
\`\`\`

**Resolved:**

\`\`\`javascript
const [activeAction, setActiveAction] = useState(null); // 'buy' | 'sell'
\`\`\`

**Reasoning:** Both versions declare the same state. The \`main\` branch adds a helpful comment documenting the expected values. Keep both the declaration and the comment.

***

### **Final output**

After pasting the resolved code, the editor should show clean code with **zero conflict markers**. You can then proceed immediately to mark as resolved and merge.`,
        steps: [
            "Extract full conflicting file via DOM",
            "Contextualize & resolve regions",
            "Construct resolved file in memory",
            "Replace editor content & mark resolved"
        ],
        notes: "Both branches usually add valid functionality. Combine compatible changes rather than discarding one side.",
        createdAt: "2026-01-15T10:00:00Z",
        updatedAt: "2026-01-18T14:40:00Z",
        like_count: 19,
        savesCount: 8
    },
    {
        id: "2",
        slug: "amazon-price-tracker",
        title: "Amazon Price Drop Alert",
        summary: "Monitor any Amazon product page and get notified when the price drops below your target threshold.",
        difficulty: "beginner",
        worksWith: [],
        tags: ["featured", "shopping", "monitoring"],
        targetSites: ["amazon.com"],
        promptText: `## Amazon Price Drop Alert

**Objective:** Continuously monitor a product's price and trigger an alert when it drops.

### Steps:
1. Navigate to the Amazon product URL provided
2. Extract the current price from the buy box
3. Compare against the target threshold
4. If below threshold: Send notification via webhook
5. If above: Log the price and schedule next check

### Exit Condition:
Price drops below target OR monitoring period expires.`,
        steps: [
            "Open product page",
            "Extract current price",
            "Compare to threshold",
            "Send alert if triggered"
        ],
        notes: "Set up a webhook endpoint to receive price alerts. Works with Slack, Discord, or email integrations.",
        createdAt: "2026-01-10T09:00:00Z",
        updatedAt: "2026-01-18T08:00:00Z",
        like_count: 14,
        savesCount: 5
    },
    {
        id: "3",
        slug: "linkedin-auto-apply",
        title: "LinkedIn Easy Apply Automation",
        summary: "Automatically apply to jobs matching your criteria using LinkedIn's Easy Apply feature.",
        difficulty: "intermediate",
        worksWith: [],
        tags: ["featured", "outreach", "jobs"],
        targetSites: ["linkedin.com"],
        promptText: `## LinkedIn Easy Apply Automation

**Objective:** Streamline job applications by automating Easy Apply submissions.

### Pre-requisites:
- Logged into LinkedIn
- Resume uploaded to profile
- Search filters pre-configured

### Steps:
1. Navigate to Jobs with Easy Apply filter
2. For each job listing:
   - Click "Easy Apply"
   - Fill any required fields from profile data
   - Submit application
   - Log the job title and company
3. Move to next listing
4. Stop after N applications or end of results

### Safety:
- Add 5-10 second delays between applications
- Skip listings requiring additional questions`,
        steps: [
            "Search for matching jobs",
            "Click Easy Apply",
            "Auto-fill application",
            "Submit and log",
            "Move to next"
        ],
        notes: "Use responsibly. LinkedIn may rate-limit or flag automated activity.",
        createdAt: "2026-01-08T14:00:00Z",
        updatedAt: "2026-01-17T16:00:00Z",
        like_count: 18,
        savesCount: 12
    },
    {
        id: "4",
        slug: "google-sheets-web-scraper",
        title: "Web Scrape to Google Sheets",
        summary: "Extract structured data from any webpage and append it directly to a Google Sheet.",
        difficulty: "intermediate",
        worksWith: [],
        tags: ["featured", "scraping", "automation"],
        targetSites: ["sheets.google.com"],
        promptText: `## Web Scrape to Google Sheets

**Objective:** Scrape data from a target page and write it to Google Sheets.

### Inputs:
- Target URL to scrape
- CSS selectors for data points
- Google Sheet URL

### Steps:
1. Navigate to target URL
2. Extract data using provided selectors
3. Format as row data
4. Navigate to Google Sheet
5. Append row to sheet
6. Confirm write successful

### Tips:
- Use browser DevTools to find selectors
- Test selectors on a single item first`,
        steps: [
            "Load target page",
            "Query selectors",
            "Extract text content",
            "Open Google Sheet",
            "Append new row"
        ],
        notes: "Requires Google login. Sheet must be editable by your account.",
        createdAt: "2026-01-05T11:00:00Z",
        updatedAt: "2026-01-16T09:30:00Z",
        like_count: 16,
        savesCount: 9
    },
    {
        id: "5",
        slug: "twitter-thread-unroller",
        title: "Twitter Thread to Markdown",
        summary: "Convert any Twitter/X thread into a clean, readable Markdown document.",
        difficulty: "beginner",
        worksWith: [],
        tags: ["featured", "social", "productivity"],
        targetSites: ["twitter.com", "x.com"],
        promptText: `## Twitter Thread to Markdown

**Objective:** Capture an entire thread and format it as Markdown.

### Steps:
1. Navigate to the first tweet in the thread
2. Scroll to load all replies from the author
3. Extract tweet text, images, and timestamps
4. Format as Markdown with proper headings
5. Copy to clipboard or save to file

### Output Format:
# Thread by @username

> Tweet 1 content

> Tweet 2 content

...`,
        steps: [
            "Open thread URL",
            "Scroll to load all tweets",
            "Filter author's tweets only",
            "Format as Markdown",
            "Output to clipboard"
        ],
        notes: "Works best on public threads. May need login for protected accounts.",
        createdAt: "2026-01-12T16:00:00Z",
        updatedAt: "2026-01-18T10:00:00Z",
        like_count: 7,
        savesCount: 3
    }
];

export const MOCK_TAGS = ["social", "automation", "outreach", "travel", "monitoring", "saving", "dev", "summary", "research"];
