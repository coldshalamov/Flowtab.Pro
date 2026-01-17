import { Prompt, PromptListResponse, TagsResponse } from "./apiTypes";
import { MOCK_PROMPTS, MOCK_TAGS } from "./mockData";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export async function fetchPrompts(params: Record<string, string | number | undefined>): Promise<PromptListResponse> {
    try {
        // Attempt real API fetch
        const url = new URL(`${API_BASE}/v1/prompts`);
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null && value !== "") {
                url.searchParams.append(key, String(value));
            }
        });

        const res = await fetch(url.toString(), {
            cache: "no-store",
            headers: { "Content-Type": "application/json" }
        });
        if (!res.ok) throw new Error(`API returned ${res.status}`);
        return await res.json();
    } catch (error) {
        console.warn("API unavailable or failed, falling back to mock data.", error);
        await delay(600); // Simulate network latency

        let filtered = [...MOCK_PROMPTS];

        // Helper to normalize strings
        const lower = (s: string) => s.toLowerCase();

        // 1. Text Search
        if (params.q) {
            const q = lower(String(params.q));
            filtered = filtered.filter(p =>
                lower(p.title).includes(q) ||
                lower(p.summary).includes(q) ||
                lower(p.promptText).includes(q)
            );
        }

        // 2. Difficulty
        if (params.difficulty && params.difficulty !== "all") {
            filtered = filtered.filter(p => p.difficulty === params.difficulty);
        }

        // 3. Works With (partial match or exact)
        if (params.worksWith && params.worksWith !== "all") {
            const ww = String(params.worksWith);
            filtered = filtered.filter(p => p.worksWith.includes(ww));
        }

        // 4. Tags (comma separated)
        if (params.tags) {
            const tags = String(params.tags).split(',').map(t => t.trim());
            if (tags.length > 0 && tags[0] !== "") {
                filtered = filtered.filter(p => tags.some(t => p.tags.includes(t)));
            }
        }

        return {
            items: filtered,
            page: 1,
            pageSize: filtered.length,
            total: filtered.length
        };
    }
}

export async function fetchPrompt(slug: string): Promise<Prompt | null> {
    try {
        const res = await fetch(`${API_BASE}/v1/prompts/${slug}`, { cache: "no-store" });
        if (!res.ok) throw new Error("Failed to fetch prompt");
        return await res.json();
    } catch (error) {
        console.warn(`API unavailable for slug ${slug}, using mock.`, error);
        await delay(300);
        return MOCK_PROMPTS.find(p => p.slug === slug) || null;
    }
}

export async function fetchTags(): Promise<string[]> {
    try {
        const res = await fetch(`${API_BASE}/v1/tags`, { cache: "no-store" });
        if (!res.ok) throw new Error("Failed to fetch tags");
        const data: TagsResponse = await res.json();
        return data.items;
    } catch (error) {
        console.warn("API unavailable for tags, using mock.", error);
        return MOCK_TAGS;
    }
}

export async function submitPrompt(data: Partial<Prompt>): Promise<boolean> {
    // In production, we want to try the real API first
    if (process.env.NODE_ENV === 'production' && API_BASE.includes('localhost')) {
        console.warn("⚠️ API_BASE is still pointing to localhost in production!");
    }

    try {
        const adminKey = process.env.NEXT_PUBLIC_ADMIN_KEY || "demo-key";
        const res = await fetch(`${API_BASE}/v1/prompts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Admin-Key': adminKey
            },
            body: JSON.stringify(data)
        });

        if (!res.ok) {
            const errorData = await res.json().catch(() => ({}));
            console.error("Submission failed:", res.status, errorData);
            throw new Error("API submission failed");
        }
        return true;
    } catch (error) {
        console.warn("Real submission failed (likely no admin/backend auth setup yet). Mocking success for demo.", error);
    }

    // Mock submission fallthrough for demo purposes
    await delay(1000);
    return true;
}
