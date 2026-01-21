# Flowtab.Pro Creator Guide

## Welcome, Creator! 🎨

This guide will help you create high-quality browser automation Flows that users love—and that earn you revenue through Flowtab.Pro's creator revenue sharing program.

## Revenue Model Overview

As a creator on Flowtab.Pro, you earn **$0.07 for every qualifying copy** of your Flows.

### Qualifying Copies

A copy counts toward your earnings when:
1. A premium subscriber ($10/month) copies your Flow
2. They haven't copied this Flow before in the current month
3. They haven't exceeded their 100-copy monthly limit

### Example Earnings

| Monthly Copies | Monthly Earnings | Annual Earnings |
|----------------|------------------|-----------------|
| 50 | $3.50 | $42 |
| 200 | $14.00 | $168 |
| 500 | $35.00 | $420 |
| 1,000 | $70.00 | $840 |
| 5,000 | $350.00 | $4,200 |

**Portfolio Strategy:** Creating 10 popular Flows averaging 200 copies/month = **$140/month** passive income.

## What Makes a Great Flow?

### 1. Solves a Real Problem

**Good:**
- "Extract All LinkedIn Profile Data"
- "Monitor Hacker News Front Page Every Hour"
- "Auto-Apply to Remote Jobs on Indeed"

**Avoid:**
- "Click a Button" (too simple, no value)
- "Do Stuff on Website" (too vague)
- "My Custom Workflow" (not generalizable)

### 2. Clear, Actionable Prompt

Your `promptText` should be copy-paste ready for AI agents:

**Good Example:**
```
Navigate to https://news.ycombinator.com and extract the following data from the front page:
- Article title
- Article URL
- Points (upvotes)
- Author username
- Number of comments
- Post age

Return the data as a JSON array of objects with these fields: {title, url, points, author, comments, age}.

Handle pagination by clicking "More" until you've collected 100 articles or reached the end.

Error handling: If the page fails to load, retry up to 3 times with 5-second delays. If an article is missing data (e.g., no comments yet), use null for that field.
```

**Bad Example:**
```
Scrape Hacker News
```

### 3. Complete Metadata

#### Required Fields
- **Title:** Clear, descriptive (e.g., "Scrape LinkedIn Profiles to CSV")
- **Summary:** 1-2 sentence value proposition (what problem it solves)
- **Works With:** List compatible tools (e.g., ["Playwright", "ChatGPT", "Claude"])
- **Tags:** Relevant categories (e.g., ["scraping", "linkedin", "data-extraction"])
- **Target Sites:** Domains this Flow operates on (e.g., ["linkedin.com"])

#### Optional but Recommended
- **Steps:** Numbered list of what the Flow does (improves discoverability)
- **Notes:** Tips, limitations, or prerequisites (e.g., "Requires LinkedIn login")

### 4. Tested and Verified

Before submitting, verify your Flow:
- [ ] Run it in the target environment (Playwright, ChatGPT browser, etc.)
- [ ] Test edge cases (missing data, network errors, pagination)
- [ ] Confirm output format matches description
- [ ] Check that all target sites are accessible

## Flow Structure Template

Use this template when creating new Flows:

```json
{
  "title": "[Action] [Source] to [Format/Destination]",
  "summary": "One-sentence description of what this Flow does and why it's useful.",
  "type": "prompt",
  "worksWith": ["Playwright", "ChatGPT", "Atlas"],
  "tags": ["scraping", "automation", "data-extraction"],
  "targetSites": ["example.com"],
  "promptText": "Detailed step-by-step prompt for AI agent...",
  "steps": [
    "Navigate to target URL",
    "Extract data using selectors",
    "Format output as JSON/CSV",
    "Save to file or return to user"
  ],
  "notes": "Prerequisites: Login required. Rate limit: 100 requests/hour."
}
```

## Best Practices

### Writing Effective Prompts

**1. Be Specific About Data Structure**
```
Return data as JSON: {name: string, email: string, title: string}
```

**2. Handle Errors Gracefully**
```
If login fails, return error message: {error: "Authentication required"}
```

**3. Specify Rate Limits**
```
Wait 2 seconds between requests to avoid triggering anti-bot detection.
```

**4. Include Success Criteria**
```
Success: Extracted at least 10 profiles. Failure: Less than 5 profiles or HTTP errors.
```

### Naming Conventions

**Titles:**
- Use active verbs: "Extract", "Monitor", "Scrape", "Automate"
- Include source and destination: "Scrape LinkedIn to CSV"
- Keep under 60 characters

**Tags:**
- Use lowercase, hyphen-separated: "web-scraping", "data-extraction"
- Include tool names: "playwright", "puppeteer"
- Add use case: "lead-generation", "market-research"

### Optimization for Discoverability

**1. Use Popular Tags**
- Check trending tags in the community
- Include both broad ("automation") and specific ("linkedin-scraper") tags

**2. Target High-Value Use Cases**
- Lead generation
- Competitive intelligence
- Data aggregation
- Workflow automation
- Testing/QA

**3. Create Series**
- "LinkedIn Scraper - Basic"
- "LinkedIn Scraper - Advanced with Pagination"
- "LinkedIn Scraper - Company Pages"

## Monetization Strategies

### Strategy 1: Build a Portfolio

Create 20-30 Flows covering different use cases. Even if each gets 50 copies/month:
- 25 Flows × 50 copies × $0.07 = **$87.50/month**

### Strategy 2: Focus on High-Value Niches

Research what tools and sites have high demand but low Flow availability:
- E-commerce platforms (Shopify, Amazon)
- Social media (Twitter, Instagram, TikTok)
- Job boards (LinkedIn, Indeed, Glassdoor)
- Real estate (Zillow, Redfin)
- B2B tools (Salesforce, HubSpot)

### Strategy 3: Iterate Based on Analytics

Once you have Flows published, check your creator dashboard:
- Which Flows get the most copies?
- What tags are driving traffic?
- What tools are most popular?

Double down on what works—create variations and improvements.

### Strategy 4: Provide Comprehensive Coverage

Be the "go-to" creator for a specific domain:
- **Example:** All major LinkedIn automation tasks
  - Profile scraping
  - Connection requests
  - Message automation
  - Job search
  - Company research

Users will copy multiple Flows from trusted creators.

## Payout Information

### How Payouts Work

1. **Monthly Calculation:** On the 1st of each month, we calculate your earnings for the previous month
2. **Minimum Payout:** $10.00 (earnings below this roll over to next month)
3. **Payment Method:** Stripe Connect transfer to your bank account
4. **Timeline:** Payouts processed within 5 business days of month-end

### Setting Up Payouts

1. Go to Creator Dashboard → Payouts
2. Click "Connect Stripe Account"
3. Complete Stripe onboarding (requires bank details and tax info)
4. Once verified, payouts are automatic

### Tax Considerations

- You'll receive a 1099-MISC form if you earn $600+ annually (US creators)
- International creators: Check local tax requirements
- Keep records of your earnings for tax purposes

## Content Guidelines

### What's Allowed
- Browser automation workflows
- Data extraction scripts
- Testing/QA automation
- Workflow automation
- Research and monitoring tools

### What's Not Allowed
- Illegal activities (fraud, unauthorized access, DDoS)
- Violates terms of service of target websites
- Scrapes personal data without consent (GDPR violations)
- Spam or mass messaging
- Bypasses paywalls or DRM
- Malicious code or exploits

**Important:** Creators are responsible for ensuring their Flows comply with applicable laws and website terms of service. Flowtab.Pro reserves the right to remove Flows that violate these guidelines.

## Quality Standards

To maintain library quality, Flows may be marked as "not featured" or removed if:
- They don't work as described
- They're duplicate/low-effort copies of existing Flows
- They receive multiple user reports
- They violate content guidelines

**Tip:** High-quality, unique Flows are more likely to be featured on the homepage and in marketing materials.

## Getting Started Checklist

- [ ] Read this guide thoroughly
- [ ] Set up Stripe Connect for payouts
- [ ] Create your first Flow using the template
- [ ] Test your Flow in the target environment
- [ ] Submit your Flow for review
- [ ] Share your Flow on social media (tag @FlowtabPro)
- [ ] Monitor your creator dashboard for analytics
- [ ] Iterate based on user feedback

## Support & Community

### Resources
- **Discord:** Join our creator community at discord.gg/flowtab (coming soon)
- **Email:** creators@flowtab.pro
- **Documentation:** docs.flowtab.pro

### Creator Program Tiers

As your earnings grow, you'll unlock perks:

**Bronze** (0-100 copies/month)
- Creator badge on profile
- Basic analytics

**Silver** (100-500 copies/month)
- Featured creator badge
- Priority support
- Early access to new features

**Gold** (500+ copies/month)
- Verified creator badge
- Revenue share bonus (+5%)
- Co-marketing opportunities

## Frequently Asked Questions

### Can I publish the same Flow on other platforms?
Yes! We don't require exclusivity. However, Flows must be original content you have the right to publish.

### How do I update a published Flow?
Go to Creator Dashboard → My Flows → Edit. Updates are instant but don't affect existing copies.

### What if someone copies my Flow without using the button?
Our protection is based on convenience, not DRM. Users pay for the ease of one-click copy. Manual recreation is tedious and not scalable.

### Can I see who copied my Flows?
For privacy reasons, no. You can see aggregate stats (total copies, earnings) but not individual users.

### What happens if a user copies my Flow 101 times in a month?
The first 100 copies pay you $0.07 each. Copies 101+ are free for the user and don't generate revenue for you (or any creator).

### Can I promote my Flows outside Flowtab.Pro?
Absolutely! Share your Flow URLs on social media, blogs, YouTube, etc. More visibility = more copies = more revenue.

### What if I want to remove a Flow?
You can unpublish anytime from your dashboard. Existing copies remain functional, but new users can't copy it.

---

## Ready to Start Creating?

1. **Sign Up:** Create your creator account at flowtab.pro/creator
2. **Set Up Payouts:** Connect your Stripe account
3. **Create Your First Flow:** Use our web interface or API
4. **Share & Earn:** Promote your Flows and watch your earnings grow

**Welcome to the Flowtab.Pro creator community!** We're excited to see what you build. 🚀
