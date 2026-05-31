# Flowtab.Pro Product + Browser Extension Production Spec

Date: 2026-05-31
Status: Product/engineering spec for MVP through full product
Scope: Flowtab.Pro web app, API, community marketplace, and first-party browser extension

---

## 1. Executive Direction

Flowtab.Pro should become the procedure layer for browser agents.

The core product should not be merely a website that stores prompts. It should be a system for capturing, organizing, publishing, rating, monetizing, and exporting repeatable browser workflows.

The browser extension is the missing ingestion layer. The website is the library and marketplace. The API is the registry and account system. The deterministic recorder/compiler is the core engine.

### Strategic decisions

1. Build the extension as a first-party Flowtab product.
2. Keep it in the Flowtab.Pro monorepo for now under `apps/extension`.
3. Keep the website and extension on the same account/auth system.
4. Use the existing backend as the source of truth.
5. Rename user-facing “Prompts” to “Flows” wherever possible.
6. Keep internal `/v1/prompts` compatibility initially to avoid unnecessary migration risk.
7. Store canonical structured Flow JSON as the source of truth.
8. Deterministically render Markdown/browser-agent prompts from that JSON.
9. Do not require an LLM between recording and prompt generation.
10. Default every recorded Flow to private draft until the creator reviews and publishes it.

### One-sentence product thesis

Record a browser task once; Flowtab turns it into a reusable browser-agent Flow that can be copied, saved, forked, published, rated, verified, monetized, and exported.

---

## 2. Current Repo Context

The repo already describes Flowtab.Pro as a community-driven marketplace for browser automation Flows with creator revenue sharing. That is exactly the right foundation for this extension.

Current known structure:

```text
Flowtab.Pro/
├── apps/
│   ├── web/              # Next.js frontend
│   └── api/              # FastAPI backend
├── contracts/
│   └── openapi.yaml
├── docs/
├── render.yaml
└── vercel.json
```

Current backend concepts already present:

- `Prompt` model with `title`, `summary`, `worksWith`, `tags`, `targetSites`, `promptText`, `steps`, `notes`, `author_id`, counts, premium flags, and marketplace fields.
- `User` model with email/password auth, superuser flag, creator/seller fields, Stripe customer/connect fields.
- `OAuthAccount` model for linked provider identities.
- `Subscription`, `FlowCopy`, and `CreatorPayout` models for usage-based creator payouts.
- Comments, likes, saves, purchases, providers, account connections, credential vault items, and manual overrides.

Current backend endpoints already support:

- Email/password registration and JWT login.
- OAuth start/exchange/link for Google, GitHub, and Facebook.
- `/v1/users/me`.
- Prompt list/search/filter/pagination.
- Authenticated prompt creation.
- Comments and likes.

This means the extension does not need a separate identity layer. It should plug into the existing account system.

---

## 3. Product Definition

### Product name

Flowtab Extension, first-party extension for Flowtab.Pro.

### Primary users

1. Browser-agent users who want reusable prompts for sites they use often.
2. Creators who know how to configure tools and want to publish useful browser workflows.
3. Automation engineers who want deterministic, inspectable flows rather than opaque AI guesses.
4. Teams that want private libraries for onboarding, ops, support, sales, QA, marketing, or internal tools.

### Primary use cases

- Find a Flow for the site currently open in the browser.
- Copy a browser-agent prompt for the current site.
- Record a task on a site.
- Convert the recorded actions into a deterministic prompt.
- Save the Flow privately.
- Publish the Flow to the Flowtab marketplace/community library.
- Fork/improve an existing Flow.
- Rate whether a Flow works.
- Report broken/dangerous/outdated Flows.
- Track creator usage and payouts.

### Core value proposition

Browser agents waste time because humans give vague instructions. Flowtab lets humans demonstrate the path once, then converts that path into reusable instructions that agents can follow.

The extension should feel like:

```text
Open site → Flowtab side panel shows useful Flows → copy one or record your own.
```

---

## 4. Terminology

### Flow

The durable unit of value. A Flow is a reusable browser procedure for a site or class of sites.

A Flow may contain:

- Title
- Summary
- Target domains/sites
- Variables
- Canonical structured steps
- Rendered Markdown prompt
- Safety rules
- Risk level
- Creator attribution
- Version history
- Usage/copy analytics
- Comments, likes, saves, reports

### Prompt

A rendered export of a Flow. The prompt is not the source of truth. The source of truth is the structured Flow recipe.

### Recipe

Canonical structured JSON representation of a Flow.

### Recording

A raw event trace captured by the extension while a user performs a task.

### Compiler

Deterministic logic that converts normalized action steps into structured recipe JSON and Markdown prompt text using phrase templates.

### Renderer

Deterministic logic that turns a structured Flow recipe into Markdown, JSON, Playwright, Puppeteer, or checklist output.

---

## 5. Recommended Repo Architecture

Add the extension and shared packages inside the current repo.

```text
Flowtab.Pro/
├── apps/
│   ├── web/
│   ├── api/
│   └── extension/
│       ├── manifest.json
│       ├── package.json
│       ├── src/
│       │   ├── background/
│       │   │   └── service-worker.ts
│       │   ├── content/
│       │   │   └── recorder-content-script.ts
│       │   ├── sidepanel/
│       │   │   ├── App.tsx
│       │   │   └── sidepanel.html
│       │   ├── popup/
│       │   │   ├── Popup.tsx
│       │   │   └── popup.html
│       │   ├── auth/
│       │   ├── api/
│       │   ├── storage/
│       │   └── styles/
│       └── vite.config.ts
│
├── packages/
│   ├── flow-schema/
│   │   └── src/index.ts
│   ├── recorder-core/
│   │   └── src/index.ts
│   ├── prompt-renderer/
│   │   └── src/index.ts
│   └── flowtab-api-client/
│       └── src/index.ts
│
├── contracts/
│   └── openapi.yaml
└── docs/
```

### Why monorepo first

The extension, web app, backend, schema, and renderer will evolve together. Separate repos would create needless versioning friction. Split only if the extension develops a separate release process, outside contributors, or open-source/private-source tension.

---

## 6. Browser Extension Architecture

### Platform target

Start with Chrome Manifest V3. Later support Edge and other Chromium browsers. Firefox can come later through WebExtensions adaptation.

### Extension UI surfaces

1. Side panel: primary product UI.
2. Toolbar popup: lightweight login/status/quick actions.
3. Content script overlay: recording indicator and minimal page-level controls.
4. Optional context menu: “Record Flow from this page” and “Find Flowtab Flows for this site.”

### Primary extension screens

1. Logged out screen
   - “Sign in to Flowtab”
   - Email/password login
   - OAuth buttons
   - Link to create account on Flowtab.Pro

2. Current-site library screen
   - Current domain shown at top
   - Matching Flows
   - Search within current domain
   - Global search
   - Copy prompt button
   - Save/favorite button
   - Open on Flowtab.Pro
   - Record new Flow button

3. Recorder screen
   - Start recording
   - Recording state
   - Step count
   - Current URL
   - Pause/resume
   - Stop recording
   - Privacy warning: “Do not record secrets. Sensitive fields are redacted.”

4. Review generated Flow screen
   - Title
   - Summary
   - Target domain(s)
   - Variables
   - Generated Markdown prompt
   - Step list
   - Risk level selector
   - Visibility: private draft / unlisted / public
   - Save draft
   - Publish

5. Account screen
   - Logged-in user
   - Subscription/plan
   - Creator status
   - My Flows
   - Settings
   - Logout

### Minimum permissions

MVP manifest should avoid broad persistent permissions where possible.

Recommended initial permissions:

```json
{
  "manifest_version": 3,
  "permissions": [
    "activeTab",
    "scripting",
    "storage",
    "identity",
    "sidePanel"
  ],
  "host_permissions": [
    "https://flowtab.pro/*",
    "https://api.flowtab.pro/*",
    "http://localhost:3000/*",
    "http://localhost:8000/*"
  ]
}
```

Notes:

- Use `activeTab` so page access is user-invoked rather than broad all-sites access.
- Use `scripting` to inject the recorder only after the user starts recording.
- Use `storage` for auth token and extension state.
- Use `identity` for OAuth flows.
- Use `sidePanel` for the persistent library/recorder UI.
- Avoid `debugger`, `cookies`, `history`, and `webRequest` in the MVP unless absolutely necessary.
- Avoid `<all_urls>` in MVP.

---

## 7. Authentication Spec

### Goal

The extension must use the same Flowtab account as the website.

### Current foundation

The API already supports JWT login and `/v1/users/me`. OAuth start/exchange already exists. The extension should reuse those endpoints.

### Email/password login

Extension login form:

1. User enters email/username and password.
2. Extension posts `application/x-www-form-urlencoded` to `/v1/auth/token`.
3. API returns `{ access_token, token_type }`.
4. Extension stores token in `chrome.storage.local` for MVP.
5. Extension calls `/v1/users/me` to hydrate user state.

### OAuth login

Use Chrome Identity API.

Flow:

1. Extension computes redirect URI with `chrome.identity.getRedirectURL("auth")`.
2. Extension calls `/v1/auth/oauth/{provider}/start?redirect_uri=<redirect_uri>`.
3. API returns `authorize_url`, `state`, `code_verifier`, and `code_challenge`.
4. Extension calls `chrome.identity.launchWebAuthFlow({ url: authorize_url, interactive: true })`.
5. Provider redirects to `https://<extension-id>.chromiumapp.org/auth?...`.
6. Extension parses `code` and `state`.
7. Extension calls `/v1/auth/oauth/{provider}/exchange` with `{ code, redirect_uri, state, code_verifier }`.
8. API returns Flowtab JWT.
9. Extension stores token and fetches `/v1/users/me`.

Backend production requirement:

- Add the extension redirect URI to `OAUTH_REDIRECT_ALLOWLIST`.
- Because extension IDs differ between dev and production, keep separate dev/prod redirect entries.

### Token storage

MVP:

- Store JWT in `chrome.storage.local`.
- Store user profile cache in `chrome.storage.local`.
- Clear both on logout.

Hardening:

- Add refresh tokens with rotation.
- Use shorter access-token lifetime.
- Track extension sessions server-side.
- Add revoke/logout endpoint.
- Add device/session management on the website.

### Auth acceptance criteria

- User can log into the extension with email/password.
- User can log into the extension with at least Google and GitHub OAuth.
- Extension and website show the same user identity.
- Authenticated extension calls can create private draft Flows.
- Logout clears extension token and user state.

---

## 8. Flow Data Model

### Guiding principle

Do not store Markdown as the only representation. Store canonical Flow JSON, then render Markdown deterministically.

### MVP-compatible backend approach

Keep the existing `prompts` table and add fields rather than renaming everything immediately.

Add nullable fields to `Prompt`:

```python
recipe_json: dict | None           # canonical Flow recipe
recording_trace: dict | None       # optional raw/sanitized recording trace
rendered_markdown: str | None      # deterministic Markdown export
schema_version: str = "flowtab.recipe.v1"
source: str = "manual"             # manual | extension_recording | imported
visibility: str = "public"         # private | unlisted | public
status: str = "draft"              # draft | published | archived | flagged | removed
risk_level: str = "normal"         # safe | normal | sensitive | destructive
primary_domain: str | None
last_verified_at: datetime | None
broken_count: int = 0
works_count: int = 0
forked_from_id: str | None
current_version: int = 1
```

Eventually add dedicated tables:

```text
flow_versions
flow_reports
flow_verifications
flow_runs
flow_exports
flow_domain_stats
flow_variable_schemas
```

### Canonical Flow recipe schema

```json
{
  "schemaVersion": "flowtab.recipe.v1",
  "title": "Add a webhook endpoint",
  "summary": "Creates a webhook endpoint from a dashboard settings page.",
  "domains": ["example.com"],
  "startUrl": "https://example.com/dashboard",
  "variables": [
    {
      "name": "WEBHOOK_URL",
      "type": "url",
      "required": true,
      "description": "The destination URL for the webhook."
    }
  ],
  "risk": {
    "level": "normal",
    "requiresLogin": true,
    "stopOnPayment": true,
    "stopOnPassword": true,
    "stopOn2FA": true,
    "destructive": false
  },
  "steps": [
    {
      "id": "step_001",
      "action": "navigate",
      "url": "https://example.com/dashboard"
    },
    {
      "id": "step_002",
      "action": "click",
      "target": {
        "role": "link",
        "label": "Settings",
        "text": "Settings",
        "selector": "a[href='/settings']"
      }
    },
    {
      "id": "step_003",
      "action": "fill",
      "target": {
        "role": "textbox",
        "label": "Webhook URL",
        "name": "webhook_url"
      },
      "value": "{WEBHOOK_URL}"
    },
    {
      "id": "step_004",
      "action": "click",
      "target": {
        "role": "button",
        "label": "Save"
      }
    }
  ],
  "exportHints": {
    "agentPrompt": true,
    "playwright": true,
    "puppeteer": true,
    "checklist": true
  }
}
```

### Markdown export format

Rendered Markdown should be deterministic and stable.

```markdown
# Add a webhook endpoint

Use this Flow on: example.com

## Goal
Create a webhook endpoint from the dashboard settings page.

## Variables
- `{WEBHOOK_URL}`: The destination URL for the webhook.

## Steps
1. Open `https://example.com/dashboard`.
2. Click the “Settings” link.
3. Find the “Webhook URL” text field and enter `{WEBHOOK_URL}`.
4. Click the “Save” button.

## Safety rules
- Do not change billing, password, security, or unrelated account settings.
- Stop if the site asks for 2FA, re-authentication, payment details, or destructive confirmation.
- If a step cannot be completed, report the failed step and visible page state.
```

---

## 9. Recorder Spec

### Recorder goal

Capture meaningful user actions and convert them into a clean, replayable browser-agent instruction set.

The recorder should capture actions, not screenshots. Screenshots may be optional debugging artifacts later, but they should not be the foundation of the product.

### Event types to capture

MVP:

- Navigation start/current URL
- Click
- Input/fill
- Select/dropdown change
- Checkbox/radio change
- Submit
- SPA route changes
- Page title changes

Later:

- File upload placeholders
- Drag/drop
- Keyboard shortcuts
- Wait-for-visible text
- Modal open/close
- Table row selection
- Multi-tab workflows
- Downloads
- Copy/paste detection without storing clipboard contents

### Events to ignore or compress

- Mouse movement
- Hover unless it reveals a menu needed for the task
- Repeated keypresses inside the same field
- Scroll events unless required to reveal a target
- Duplicate clicks on the same target within a short interval
- Browser chrome actions the extension cannot observe reliably

### Raw event shape

```ts
type RawRecordedEvent = {
  id: string;
  timestamp: number;
  url: string;
  pageTitle?: string;
  type: "click" | "input" | "change" | "submit" | "navigation" | "route_change";
  target?: TargetDescriptor;
  value?: string;
  sanitizedValue?: string;
  sensitive?: boolean;
};
```

### Target descriptor

```ts
type TargetDescriptor = {
  tag?: string;
  role?: string;
  accessibleName?: string;
  label?: string;
  text?: string;
  placeholder?: string;
  name?: string;
  id?: string;
  dataTestId?: string;
  ariaLabel?: string;
  href?: string;
  selector?: string;
  xpath?: string;
  nearbyText?: string[];
  formLabel?: string;
  headingContext?: string;
  boundingClientRect?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
};
```

### Target naming priority

Use this priority when generating human-readable instructions:

1. Explicit label associated with form control
2. Accessible name / ARIA label
3. Button/link visible text
4. Placeholder
5. `data-testid` or similar stable test attribute
6. `name` attribute
7. Stable `id`
8. Nearby heading/context text
9. CSS selector
10. XPath
11. Coordinates as last resort only

### Sensitive value handling

Never publish raw sensitive values by default.

Always redact:

- Password fields
- Credit card fields
- CVV/security code fields
- One-time codes
- API keys/tokens/secrets
- Private keys
- SSNs/tax IDs
- Phone numbers if field context indicates security/identity
- Any field with names like `password`, `token`, `secret`, `api_key`, `authorization`, `bearer`, `card`, `cvv`, `ssn`, `otp`, `mfa`, `2fa`

Variable inference:

- Email-like input -> `{EMAIL}` unless user chooses to keep literal.
- URL-like input -> `{URL}` or more specific `{WEBHOOK_URL}` if label says webhook.
- Date-like input -> `{DATE}` or `{START_DATE}` / `{END_DATE}` based on label.
- Search input -> `{SEARCH_QUERY}`.
- Secret input -> `{SECRET_VALUE}`.

MVP rule: show variables to the creator for review before saving.

---

## 10. Deterministic Compiler Spec

### Goal

Convert normalized steps into browser-agent instructions using a phrase library and deterministic rules.

No LLM is required.

### Pipeline

```text
Raw browser events
↓
Sanitize values
↓
Normalize events into steps
↓
Compress noisy steps
↓
Infer variables
↓
Build Flow recipe JSON
↓
Render Markdown prompt
↓
Save/copy/publish
```

### Normalization rules

```text
keypress sequence in same input       → one fill step
input change in select                → one select option step
click causing URL change              → click step + optional wait/navigation note
click causing modal                   → click step + wait for modal/dialog
SPA route change                      → route_change/navigation step
scroll-only sequences                 → ignore unless required
password/token field                  → fill with placeholder variable
submit button click                   → click button; optionally verify result
```

### Phrase library

```ts
const INSTRUCTION_TEMPLATES = {
  navigate: "Open `{url}`.",
  click_button: "Click the “{label}” button.",
  click_link: "Click the “{label}” link.",
  click_tab: "Click the “{label}” tab.",
  click_menu_item: "Click the “{label}” menu item.",
  fill_text: "Find the “{label}” text field and enter `{value}`.",
  fill_password: "Find the “{label}” password field and enter `{value}`.",
  select_option: "Open the “{label}” dropdown and choose “{value}`.",
  check_checkbox: "Check the “{label}” checkbox.",
  uncheck_checkbox: "Uncheck the “{label}” checkbox.",
  choose_radio: "Choose the “{label}” radio option.",
  submit: "Submit the form.",
  wait_for_navigation: "Wait for the page to finish loading.",
  wait_for_text: "Wait until the page shows “{text}”.”,
  verify_text: "Verify that the page shows “{text}”.”,
  fallback_click: "Click the element described as `{description}`."
};
```

Fix punctuation and quote consistency in implementation. The spec above is conceptual.

### Renderer output sections

Every generated browser-agent prompt should include:

1. Title
2. Target site/domain
3. Goal
4. Variables
5. Steps
6. Safety rules
7. Failure behavior
8. Optional metadata block

### Default safety rules

Append these to every rendered agent prompt:

```text
- Do not change billing, password, security, or unrelated account settings unless explicitly instructed.
- Stop if the site asks for 2FA, re-authentication, payment details, or destructive confirmation.
- If a step cannot be completed, report the failed step and visible page state.
- Do not invent missing values. Ask for required variables.
```

---

## 11. Extension User Flows

### Flow A: Find prompts/Flows for current site

1. User opens a website.
2. User clicks Flowtab extension.
3. Extension gets active tab URL/domain.
4. Extension fetches matching Flows from API.
5. Side panel shows Flows for current domain.
6. User clicks “Copy prompt.”
7. API logs copy/usage event if applicable.
8. Prompt text is copied to clipboard.

Acceptance:

- Works on any standard website after user invokes extension.
- Shows matching domain-specific Flows.
- Copy requires login.
- Copy event attaches to the logged-in user.

### Flow B: Record new Flow

1. User logs into extension.
2. User visits the site they want to record.
3. User clicks “Record new Flow.”
4. Extension injects recorder content script.
5. User performs actions.
6. User clicks “Stop recording.”
7. Extension normalizes trace.
8. Extension renders Markdown prompt.
9. User reviews title, variables, steps, safety, visibility.
10. User saves private draft or publishes.

Acceptance:

- Recorder captures at least navigation, click, fill, select, checkbox, and submit.
- Sensitive fields are redacted.
- Generated prompt is readable and copyable.
- Saved Flow is attached to the logged-in user.
- Private draft is not visible publicly.

### Flow C: Publish community Flow

1. User records or manually creates Flow.
2. User reviews generated prompt and variables.
3. User sets visibility to public.
4. User confirms no secrets are included.
5. API stores Flow with `status=published` and `author_id=current_user.id`.
6. Flow appears in website library and extension library for matching domain.

Acceptance:

- Public publishing requires auth.
- Flow has author attribution.
- Flow has target domain(s).
- Flow has report button and moderation pathway.

### Flow D: Fork/improve existing Flow

1. User opens an existing Flow.
2. User clicks “Fork.”
3. System creates private draft copy with `forked_from_id`.
4. User edits/records additional steps.
5. User publishes fork.

Acceptance:

- Original creator attribution is preserved.
- Fork creator attribution is clear.
- Version/fork lineage is stored.

---

## 12. Backend API Spec

### Existing endpoints to reuse

```text
POST /v1/auth/register
POST /v1/auth/token
POST /v1/auth/oauth/{provider}/start
POST /v1/auth/oauth/{provider}/exchange
POST /v1/auth/oauth/{provider}/link
GET  /v1/users/me
GET  /v1/prompts
GET  /v1/prompts/{slug}
POST /v1/prompts
```

### Add alias endpoints

To professionalize product language without breaking internals:

```text
GET  /v1/flows              -> alias of prompts list with Flow filters
GET  /v1/flows/{slug}       -> alias of prompt detail
POST /v1/flows              -> create Flow
PATCH /v1/flows/{id_or_slug}
DELETE /v1/flows/{id_or_slug}
```

### Add domain filtering

```text
GET /v1/flows?domain=stripe.com
GET /v1/flows?targetSite=stripe.com
GET /v1/flows?domain=stripe.com&q=webhook
```

Matching logic:

- Exact domain match first.
- Then root domain match.
- Then wildcard match if supported.
- Then global search fallback.

### Extension bootstrap endpoint

```text
GET /v1/extension/bootstrap?domain=example.com
```

Response:

```json
{
  "user": {
    "id": "...",
    "username": "...",
    "email": "...",
    "is_creator": true,
    "is_seller": false
  },
  "subscription": {
    "is_subscriber": true,
    "copies_remaining": 93
  },
  "domain": "example.com",
  "matching_flows": [],
  "featured_flows": [],
  "settings": {
    "can_record": true,
    "can_publish": true
  }
}
```

### Draft creation endpoint

```text
POST /v1/flows/drafts
```

Request:

```json
{
  "title": "Recorded Flow for example.com",
  "summary": "...",
  "targetSites": ["example.com"],
  "recipe_json": {},
  "recording_trace": {},
  "rendered_markdown": "...",
  "visibility": "private",
  "source": "extension_recording"
}
```

### Publish endpoint

```text
POST /v1/flows/{id}/publish
```

Rules:

- Only author or admin can publish.
- Flow must have title, summary, targetSites, recipe_json, rendered_markdown or promptText.
- Publish should run server-side validation/safety scanning.

### Copy/use endpoint

```text
POST /v1/flows/{id_or_slug}/copy
```

Response:

```json
{
  "promptText": "...",
  "renderedMarkdown": "...",
  "copy": {
    "counted_for_payout": true,
    "copies_this_month": 12,
    "copies_remaining": 88
  }
}
```

### Report endpoint

```text
POST /v1/flows/{id_or_slug}/report
```

Report reasons:

- broken
- outdated
- unsafe
- spam
- secret_leak
- copyright
- malicious
- other

### Verification endpoint

```text
POST /v1/flows/{id_or_slug}/verify
```

Payload:

```json
{
  "status": "works" | "broken",
  "notes": "optional",
  "site_version": "optional"
}
```

---

## 13. Website Product Spec

### Website role

The website should become the professional public library, marketplace, docs hub, creator dashboard, and account layer.

### Required website areas

1. Landing page
   - Clearly explain Flowtab as “recorded browser-agent workflows.”
   - Show extension as primary call to action.
   - Show examples by site/category.

2. Library
   - Search Flows.
   - Filter by site/domain, tag, risk level, tool compatibility, popularity, latest verified.
   - Strong cards with title, summary, domain, creator, verification status, copy count.

3. Flow detail page
   - Rendered Markdown prompt.
   - Variables.
   - Steps.
   - Target site.
   - Creator attribution.
   - Works/broken votes.
   - Comments.
   - Fork button.
   - Copy button.
   - Open in extension / install extension CTA.

4. Submit/create page
   - Manual Flow editor.
   - Paste recipe JSON.
   - Render preview.
   - Save draft/publish.

5. Creator dashboard
   - My Flows.
   - Copy analytics.
   - Domain/category performance.
   - Earnings.
   - Broken reports.
   - Verification reminders.

6. Account settings
   - Profile.
   - Auth providers.
   - Subscription.
   - API/export settings.
   - Extension session management later.

7. Admin/moderation
   - Flagged Flows.
   - User reports.
   - Secret leakage review.
   - Remove/unpublish tools.
   - Creator fraud monitoring.

### Professional product improvements

- Replace user-facing “Prompt” copy with “Flow.”
- Add clean docs: “How Flowtab works,” “How to record a Flow,” “Publishing guidelines.”
- Add trust/safety pages.
- Add Chrome Web Store install CTA.
- Add status badges.
- Add onboarding checklist for new users.
- Add example packs: Stripe, Cloudflare, GitHub, Shopify, WordPress, Vercel, Notion, Google Workspace.

---

## 14. Community + Marketplace Spec

### Community mechanics

- Public Flow library.
- Private drafts.
- Public publishing.
- Forking.
- Comments.
- Likes.
- Saves.
- Works/broken confirmations.
- Reports.
- Creator profile pages.
- Domain pages.
- Tags/categories.

### Quality signals

Each Flow should show:

- Last verified date.
- Works count.
- Broken count.
- Copy count.
- Creator reputation.
- Risk level.
- Required account level: free account, paid account, admin, organization owner, etc.
- Required login: yes/no.
- Required 2FA/manual step: yes/no.

### Monetization mechanics

Existing subscription + revenue share logic should extend to extension usage.

Copy/use events should include source:

```text
website_copy
extension_copy
extension_recorded_publish
api_export
integration_export
```

Creator payouts should count qualifying copies from both website and extension.

### Bounty/request system

Add a “Request a Flow” feature:

- User requests a Flow for a domain/task.
- Creators can claim/submit.
- Requester can mark accepted.
- Premium users can fund bounties later.

This turns lack of prompt supply into a market signal.

---

## 15. Feature Brainstorm for Full Product

### Extension features

- Current-site Flow recommendations.
- Record new Flow.
- Deterministic prompt generation.
- Private/public save.
- Copy prompt.
- Fork Flow.
- Mark works/broken.
- Quick variable filling.
- Flow preview before copy.
- Recent copied Flows.
- Offline local drafts.
- Team/private library toggle.
- Recording privacy scanner.
- Recording pause/resume.
- Step delete/reorder/edit.
- Add manual step.
- Detect current domain and suggest missing Flow request.
- Context menu: “Record Flowtab Flow here.”
- Keyboard shortcut to start/stop recording.
- Export JSON/Markdown/Playwright/Puppeteer.
- Open Flow detail on Flowtab.Pro.
- Suggested tags based on deterministic domain/category mappings.

### Website features

- Domain landing pages: `/sites/stripe.com`.
- Category pages: “Developer Tools,” “Marketing,” “Ecommerce,” “Cloud,” “CRM,” “Design.”
- Creator profiles.
- Flow packs/bundles.
- Verified creator badge.
- Flow quality score.
- Full-text search.
- Changelog/version history.
- Fork graph.
- Moderation queue.
- Request/bounty board.
- Team workspaces.
- Organization private libraries.
- Enterprise admin controls.
- API access for teams.
- Public docs and examples.
- Blog: “Browser agent workflows that actually work.”

### Agent/integration features

- Copy as generic browser-agent prompt.
- Copy as Browser Use task.
- Copy as Playwright script.
- Copy as Puppeteer script.
- Copy as Selenium IDE JSON later.
- Import from Chrome DevTools Recorder JSON later.
- Import from Playwright codegen later.
- Export to GitHub Gist.
- Webhook/API for programmatic Flow retrieval.
- Integration with cloud browser providers later.
- “Run locally” only after recorder/library are stable.

### Quality/verification features

- “Works for me” voting.
- “Broken” reports.
- Required manual confirmation points.
- Last verified timestamp.
- Automated static checks on recipe JSON.
- Secret scanner.
- Dangerous-action classifier using deterministic rules.
- Site-change alerts based on broken reports.
- Prompt diff viewer.
- Version rollback.
- Community maintainers by domain.

### Business features

- Premium subscription.
- Creator revenue share.
- Paid Flow packs.
- Team plan.
- Private organization libraries.
- Usage analytics.
- Creator earnings dashboard.
- Sponsored/requested Flow bounties.
- Enterprise workflow catalog.
- White-label internal Flow library.

### Trust/safety features

- Privacy-first recording indicators.
- No silent recording.
- Default private drafts.
- Secret redaction.
- Report malicious Flow.
- Disable publishing for risky domains/categories.
- Extra confirmations for payment/security/admin tasks.
- Clear extension permission explanations.
- Public security page.

---

## 16. Security + Privacy Requirements

### Extension security principles

- Never record silently.
- Never inject recorder without user action.
- Never collect cookies.
- Never request `debugger` permission for MVP.
- Never request broad `<all_urls>` unless product value clearly justifies it.
- Never publish raw recording traces without sanitization.
- Never auto-publish recorded Flows.
- Do not store secrets in raw traces.
- Do not include hidden DOM text in prompts unless needed and safe.
- All API calls use HTTPS in production.

### Publishing safety checks

Before publishing, server should validate:

- No obvious secrets in `promptText`, `rendered_markdown`, `recipe_json`, or `recording_trace`.
- Required fields exist.
- Domain values are normalized.
- Risk level is set.
- Visibility is valid.
- User is authenticated.

### Risk levels

```text
safe        Read-only or harmless navigation.
normal      Account configuration but not billing/security/destructive.
sensitive   API keys, webhooks, personal data, admin settings, integrations.
destructive Deletes, payments, irreversible changes, security changes.
```

Destructive Flows should either be disallowed in MVP or forced into unlisted/private review.

### Production hardening needed in existing app

- Move OAuth state from in-memory to Redis.
- Move rate limiting from in-memory to Redis.
- Add brute-force protection to `/auth/token`.
- Add server-side audit logs.
- Add security headers.
- Consider replacing web localStorage JWT with HttpOnly cookie later.
- Add session revocation.

---

## 17. Implementation Roadmap

### Phase 0 — Product alignment and repo setup

Goal: prepare the repo for extension development without disturbing the current web/API app.

Tasks:

- Add `apps/extension`.
- Add shared packages: `flow-schema`, `recorder-core`, `prompt-renderer`, `flowtab-api-client`.
- Add root workspace config if not already present.
- Add README section for extension development.
- Add user-facing terminology decision: Flow externally, Prompt internals allowed short-term.

Acceptance:

- Existing web app still builds.
- Existing API tests still pass.
- Extension app can build a placeholder MV3 extension.

### Phase 1 — Flow schema + deterministic renderer

Goal: prove the compiler independent of browser complexity.

Tasks:

- Implement TypeScript Flow recipe schema.
- Implement target descriptor schema.
- Implement normalized step schema.
- Implement Markdown renderer.
- Implement phrase library.
- Implement unit tests for all step types.
- Add example recipe fixtures.

Acceptance:

- Given recipe JSON, renderer produces stable Markdown.
- Snapshot tests pass.
- No LLM or network call required.

### Phase 2 — Local recorder MVP

Goal: capture real browser actions and render a prompt locally.

Tasks:

- Build extension side panel.
- Implement start/stop recording.
- Inject content script using `activeTab` + `scripting`.
- Capture click/input/change/submit/navigation/route changes.
- Normalize raw events into steps.
- Sanitize sensitive values.
- Render prompt locally.
- Allow copy to clipboard.

Acceptance:

- User can record a 5–10 step task.
- Generated prompt is readable.
- Password/token fields are redacted.
- User can copy Markdown without saving to backend.

### Phase 3 — Extension auth + current-site library

Goal: make the extension a real Flowtab client.

Tasks:

- Implement email/password login.
- Implement OAuth login using Chrome Identity API.
- Store JWT in `chrome.storage.local`.
- Fetch `/v1/users/me`.
- Add domain detection from active tab.
- Add `/v1/flows?domain=...` or equivalent backend support.
- Show current-site matching Flows.
- Implement copy Flow with usage tracking.

Acceptance:

- Logged-out users see login screen.
- Logged-in users see current-site library.
- Copying a Flow logs usage to backend.
- Extension and website share same user account.

### Phase 4 — Save/publish recorded Flows

Goal: feed the marketplace.

Tasks:

- Add backend fields for recipe JSON / rendered Markdown / visibility / status / source.
- Add draft creation endpoint.
- Add publish endpoint.
- Add extension review screen.
- Save recorded Flow as private draft by default.
- Publish public Flow after confirmation.
- Attach author_id automatically.

Acceptance:

- Recorded Flow can be saved privately.
- Public Flow appears on Flowtab.Pro and in extension current-site library.
- Author attribution is correct.
- Public Flow contains no obvious secrets.

### Phase 5 — Website polish and creator loop

Goal: make Flowtab.Pro feel like a professional product.

Tasks:

- Update public copy from Prompt to Flow.
- Add Flow detail page improvements.
- Add domain pages.
- Add creator dashboard.
- Add works/broken verification.
- Add report flow.
- Add extension install CTA.
- Add docs and publishing guide.

Acceptance:

- A user understands what Flowtab does within 30 seconds.
- A creator can see their published Flows and usage.
- Users can report broken/unsafe Flows.

### Phase 6 — Marketplace and monetization

Goal: connect extension usage to creator payouts.

Tasks:

- Ensure extension copy events count in `FlowCopy`.
- Add copy source field.
- Finish subscription gating if needed.
- Add creator earnings dashboard.
- Add Stripe Connect onboarding.
- Add payout job.
- Add fraud/rate checks.

Acceptance:

- Premium copy behavior works from web and extension.
- Creators can see usage/earnings.
- Payout calculations include extension usage.

### Phase 7 — Advanced exports and integrations

Goal: expand beyond generic prompt copying.

Tasks:

- Export as Playwright.
- Export as Puppeteer.
- Export as JSON recipe.
- Import from DevTools Recorder JSON later.
- Add API client/SDK.
- Add team/private libraries.
- Add optional execution integrations.

Acceptance:

- Flow is no longer only a prompt. It is a reusable recipe with multiple export targets.

---

## 18. MVP Definition

The MVP is not an autonomous browser agent. Do not build that first.

The MVP is:

1. Login-required first-party Chrome extension.
2. Shows Flowtab library for current website.
3. Lets user copy a Flow prompt.
4. Lets user record actions.
5. Converts actions deterministically into Markdown prompt.
6. Lets user save private draft.
7. Lets user publish public Flow.
8. Public Flow appears on website and extension.
9. Creator attribution is stored.
10. Copy/usage is tracked.

### MVP non-goals

- Full autonomous execution.
- Cloud browser running.
- LLM-based prompt generation.
- Screenshot-based task inference.
- Multi-browser support.
- Enterprise teams.
- Sophisticated payout system beyond existing planned model.
- Perfect support for every website behavior.

---

## 19. Testing Plan

### Unit tests

Packages:

- `flow-schema`: validation tests.
- `prompt-renderer`: snapshot tests for every action type.
- `recorder-core`: normalization/compression/sanitization tests.
- `flowtab-api-client`: auth and endpoint wrapper tests.

### Backend tests

- Flow create draft.
- Flow publish.
- Flow domain filtering.
- Flow copy tracking.
- Auth required for extension endpoints.
- Author ownership.
- Secret scanner rejects obvious secrets.
- Private drafts are hidden from public list.

### Extension tests

Manual first, then automated where practical.

Manual fixtures:

- Simple HTML page with buttons/links/forms.
- Form with password/token fields.
- SPA route-change fixture.
- Dropdown/checkbox/radio fixture.
- Modal fixture.

Acceptance recordings:

- Record form fill and submit.
- Record settings navigation.
- Record dropdown selection.
- Confirm generated Markdown.
- Confirm redaction.
- Confirm save/publish.

### Website E2E

- Register/login.
- Create Flow.
- View Flow detail.
- Copy Flow.
- Comment.
- Report Flow.
- Creator views dashboard.

---

## 20. Metrics

### Product metrics

- Extension installs.
- Logged-in extension users.
- Current-site library opens.
- Flow copies from extension.
- Recordings started.
- Recordings completed.
- Drafts saved.
- Public Flows published.
- Published Flows copied.
- Works/broken ratio.
- Creator activation.
- Time from install to first copy.
- Time from install to first recording.

### Quality metrics

- Broken report rate.
- Secret leak report rate.
- Prompt copy success feedback.
- Flows with variables.
- Flows with last verified date.
- Flows per top domain.

### Business metrics

- Free-to-premium conversion.
- Premium copy rate.
- Creator payout volume.
- Creator retention.
- Top domains by demand.
- Request/bounty fulfillment rate.

---

## 21. Launch Plan

### Alpha

Audience: yourself and a few technical users.

Requirements:

- Local/dev extension install.
- Record/copy works.
- Save private drafts.
- Manual publishing.

### Private beta

Audience: creators/automation users.

Requirements:

- Chrome Web Store unlisted or limited release.
- OAuth login works.
- Current-site library works.
- Publishing works.
- Report/flag works.
- Basic docs.

### Public beta

Audience: general Flowtab users.

Requirements:

- Public Chrome Web Store listing.
- Extension CTA on website.
- Creator dashboard.
- Domain pages.
- Subscription/copy tracking coherent.
- Privacy policy and ToS updated for extension data.

---

## 22. Immediate Next Implementation Checklist

1. Add `apps/extension` with MV3 + Vite + React + TypeScript.
2. Add `packages/flow-schema`.
3. Add `packages/prompt-renderer`.
4. Add `packages/recorder-core`.
5. Build deterministic renderer before the recorder.
6. Build recorder against local static fixture pages.
7. Add extension auth with email/password.
8. Add OAuth extension login after email/password works.
9. Add `/v1/flows` alias and domain filter.
10. Add recipe JSON fields to backend.
11. Add private draft save endpoint.
12. Add publish endpoint.
13. Add extension current-site library.
14. Add generated prompt review screen.
15. Add website Flow detail/edit polish.

---

## 23. Product Principle

Flowtab wins if it becomes the place where browser-agent procedures live.

The extension should not feel like a gimmick bolted onto the site. It should feel like the natural way Flows are born.

The best mental model:

```text
GitHub Gists for browser-agent workflows,
with a recorder,
a marketplace,
and deterministic exports.
```

Start with recording, rendering, saving, publishing, and copying. Delay autonomous running until the library and compiler are strong.
