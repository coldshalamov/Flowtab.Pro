import { type Prompt, type PromptListResponse, type TagsResponse, type User, type AuthResponse } from "./apiTypes";
import { MOCK_PROMPTS, MOCK_TAGS } from "./mockData";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
const IS_PROD = process.env.NODE_ENV === "production";

if (IS_PROD && (!process.env.NEXT_PUBLIC_API_BASE || API_BASE.includes("localhost"))) {
    console.warn(
        "[Flowtab] NEXT_PUBLIC_API_BASE is missing or points at localhost; production pages may render with mock data."
    );
}

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const readFetchInit: RequestInit & { next?: { revalidate?: number } } =
    IS_PROD
        ? { next: { revalidate: 60 } }
        : { cache: "no-store" };

// Helper to get token from localStorage (client-side only)
const getToken = () => {
    if (typeof window !== 'undefined') {
        return localStorage.getItem('token');
    }
    return null;
};

export async function fetchPrompts(params: Record<string, string | number | undefined>) {
    try {
        const url = new URL(`${API_BASE}/v1/prompts`);
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null && value !== "") {
                url.searchParams.append(key, String(value));
            }
        });

        const res = await fetch(url.toString(), {
            ...readFetchInit,
            headers: { "Accept": "application/json" }
        });
        if (!res.ok) throw new Error(`API returned ${res.status}`);
    return await res.json();
}

export async function deletePrompt(slug: string): Promise<boolean> {
    try {
        const token = getToken();
        if (!token) return false;

        const res = await fetch(`${API_BASE}/v1/prompts/${slug}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!res.ok) return false;
        return true;
    } catch (error) {
        console.error("Delete failed", error);
        return false;
    }
}


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

export async function fetchPrompt(slug: string) {
    try {
        const res = await fetch(`${API_BASE}/v1/prompts/${slug}`, readFetchInit);
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
        const res = await fetch(`${API_BASE}/v1/tags`, readFetchInit);
        if (!res.ok) throw new Error("Failed to fetch tags");
        const data = await res.json();
        return data.items;
    } catch (error) {
        console.warn("API unavailable for tags, using mock.", error);
        return MOCK_TAGS;
    }
}

export async function submitPrompt(data: unknown): Promise<boolean> {
    try {
        const token = getToken();
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
        };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const res = await fetch(`${API_BASE}/v1/prompts`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(data)
        });

        if (!res.ok) {
            const errorData = await res.json().catch(() => ({}));
            console.error("Submission failed:", res.status, errorData);
            throw new Error("API submission failed");
        }
        return true;
    } catch (error) {
        console.warn("Submission failed.", error);
        return false;
    }
}

// Auth API
export async function login(email: string, password: string): Promise<AuthResponse> {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const res = await fetch(`${API_BASE}/v1/auth/token`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
    });

    if (!res.ok) {
        throw new Error('Login failed');
    }

    return await res.json();
}

export async function register(email: string, password: string): Promise<User> {
    const res = await fetch(`${API_BASE}/v1/auth/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.message || 'Registration failed');
    }

    return await res.json();
}

export async function getMe(token: string): Promise<User> {
    const res = await fetch(`${API_BASE}/v1/users/me`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    });

    if (!res.ok) {
        throw new Error('Failed to fetch user');
    }

    return await res.json();
}

