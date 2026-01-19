import {
  type AuthResponse,
  type Comment,
  type CommentListResponse,
  type LikeStatusResponse,
  type Prompt,
  type PromptListResponse,
  type TagsResponse,
  type User,
} from "./apiTypes";
import { MOCK_PROMPTS, MOCK_TAGS } from "./mockData";

export type {
  AuthResponse,
  Comment,
  CommentListResponse,
  LikeStatusResponse,
  Prompt,
  PromptListResponse,
  TagsResponse,
  User,
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
const IS_PROD = process.env.NODE_ENV === "production";

if (IS_PROD && (!process.env.NEXT_PUBLIC_API_BASE || API_BASE.includes("localhost"))) {
  console.warn(
    "[Flowtab] NEXT_PUBLIC_API_BASE is missing or points at localhost; production pages may render with mock data."
  );
}

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const readFetchInit: RequestInit & { next?: { revalidate?: number } } = IS_PROD
  ? { next: { revalidate: 60 } }
  : { cache: "no-store" };

const getToken = () => {
  if (typeof window !== "undefined") {
    return localStorage.getItem("token");
  }
  return null;
};

const authHeaders = () => {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : null;
};

export async function fetchPrompts(
  params: Record<string, string | number | undefined>
): Promise<PromptListResponse> {
  try {
    const url = new URL(`${API_BASE}/v1/prompts`);
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.append(key, String(value));
      }
    });

    const res = await fetch(url.toString(), {
      ...readFetchInit,
      headers: { Accept: "application/json" },
    });

    if (!res.ok) throw new Error(`API returned ${res.status}`);
    return await res.json();
  } catch (error) {
    console.warn("API unavailable for prompts, using mock.", error);
    await delay(150);

    let filtered = [...MOCK_PROMPTS];

    const q = (params.q ? String(params.q) : "").trim().toLowerCase();
    if (q) {
      filtered = filtered.filter(
        (p) =>
          p.title.toLowerCase().includes(q) ||
          p.summary.toLowerCase().includes(q) ||
          p.promptText.toLowerCase().includes(q)
      );
    }

    if (params.tags) {
      const tags = String(params.tags)
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);
      if (tags.length > 0) {
        filtered = filtered.filter((p) => tags.some((t) => p.tags.includes(t)));
      }
    }

    return {
      items: filtered,
      page: 1,
      pageSize: filtered.length,
      total: filtered.length,
    };
  }
}

export async function fetchPrompt(slug: string): Promise<Prompt | null> {
  try {
    const res = await fetch(`${API_BASE}/v1/prompts/${slug}`, readFetchInit);
    if (!res.ok) throw new Error("Failed to fetch prompt");
    return await res.json();
  } catch (error) {
    console.warn(`API unavailable for slug ${slug}, using mock.`, error);
    await delay(150);
    return MOCK_PROMPTS.find((p) => p.slug === slug) || null;
  }
}

export async function fetchTags(): Promise<string[]> {
  try {
    const res = await fetch(`${API_BASE}/v1/tags`, readFetchInit);
    if (!res.ok) throw new Error("Failed to fetch tags");
    const data: TagsResponse = await res.json();
    return data.items;
  } catch (error) {
    console.warn("API unavailable for tags, using mock.", error);
    return MOCK_TAGS;
  }
}

export async function submitPrompt(data: unknown): Promise<boolean> {
  try {
    const tokenHeaders = authHeaders();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(tokenHeaders || {}),
    };

    const res = await fetch(`${API_BASE}/v1/prompts`, {
      method: "POST",
      headers,
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      console.error("Submission failed:", res.status, errorData);
      return false;
    }

    return true;
  } catch (error) {
    console.warn("Submission failed.", error);
    return false;
  }
}

export async function deletePrompt(slug: string): Promise<boolean> {
  try {
    const tokenHeaders = authHeaders();
    if (!tokenHeaders) return false;

    const res = await fetch(`${API_BASE}/v1/prompts/${slug}`, {
      method: "DELETE",
      headers: tokenHeaders,
    });

    return res.ok;
  } catch (error) {
    console.error("Delete failed", error);
    return false;
  }
}

// Comments
export async function fetchComments(slug: string): Promise<CommentListResponse> {
  try {
    const res = await fetch(`${API_BASE}/v1/prompts/${slug}/comments`, readFetchInit);
    if (!res.ok) throw new Error("Failed to fetch comments");
    return await res.json();
  } catch (error) {
    // Return empty comments array as fallback when API is unavailable
    console.warn("Comments API unavailable, returning empty list");
    return { items: [] };
  }
}

export async function createComment(slug: string, body: string): Promise<Comment> {
  const tokenHeaders = authHeaders();
  if (!tokenHeaders) throw new Error("Not authenticated");

  const res = await fetch(`${API_BASE}/v1/prompts/${slug}/comments`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...tokenHeaders,
    },
    body: JSON.stringify({ body }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || "Failed to create comment");
  }

  return await res.json();
}

export async function deleteComment(commentId: string): Promise<boolean> {
  const tokenHeaders = authHeaders();
  if (!tokenHeaders) return false;

  const res = await fetch(`${API_BASE}/v1/comments/${commentId}`, {
    method: "DELETE",
    headers: tokenHeaders,
  });

  return res.ok;
}

// Likes
export async function likePrompt(slug: string): Promise<LikeStatusResponse> {
  const tokenHeaders = authHeaders();
  if (!tokenHeaders) throw new Error("Not authenticated");

  const res = await fetch(`${API_BASE}/v1/prompts/${slug}/like`, {
    method: "PUT",
    headers: tokenHeaders,
  });

  if (!res.ok) throw new Error("Failed to like flow");
  return await res.json();
}

export async function unlikePrompt(slug: string): Promise<LikeStatusResponse> {
  const tokenHeaders = authHeaders();
  if (!tokenHeaders) throw new Error("Not authenticated");

  const res = await fetch(`${API_BASE}/v1/prompts/${slug}/like`, {
    method: "DELETE",
    headers: tokenHeaders,
  });

  if (!res.ok) throw new Error("Failed to unlike flow");
  return await res.json();
}

export async function likeComment(commentId: string): Promise<LikeStatusResponse> {
  const tokenHeaders = authHeaders();
  if (!tokenHeaders) throw new Error("Not authenticated");

  const res = await fetch(`${API_BASE}/v1/comments/${commentId}/like`, {
    method: "PUT",
    headers: tokenHeaders,
  });

  if (!res.ok) throw new Error("Failed to like comment");
  return await res.json();
}

export async function unlikeComment(
  commentId: string
): Promise<LikeStatusResponse> {
  const tokenHeaders = authHeaders();
  if (!tokenHeaders) throw new Error("Not authenticated");

  const res = await fetch(`${API_BASE}/v1/comments/${commentId}/like`, {
    method: "DELETE",
    headers: tokenHeaders,
  });

  if (!res.ok) throw new Error("Failed to unlike comment");
  return await res.json();
}

// Auth
export async function login(email: string, password: string): Promise<AuthResponse> {
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);

  const res = await fetch(`${API_BASE}/v1/auth/token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData,
  });

  if (!res.ok) {
    throw new Error("Login failed");
  }

  return await res.json();
}

export async function register(email: string, username: string, password: string): Promise<User> {
  const res = await fetch(`${API_BASE}/v1/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, username, password }),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.message || "Registration failed");
  }

  return await res.json();
}

export async function getMe(token: string): Promise<User> {
  const res = await fetch(`${API_BASE}/v1/users/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch user");
  }

  return await res.json();
}

// OAuth
export type OAuthProvider = "google" | "github" | "facebook";

export async function startOAuth(provider: OAuthProvider, redirect_uri: string) {
  const url = new URL(`${API_BASE}/v1/auth/oauth/${provider}/start`);
  url.searchParams.set("redirect_uri", redirect_uri);

  const res = await fetch(url.toString(), {
    method: "POST",
    headers: {
      Accept: "application/json",
    },
    cache: "no-store",
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || "Failed to start OAuth");
  }

  return await res.json() as {
    authorize_url: string;
    state: string;
    code_verifier: string;
    code_challenge: string;
  };
}

export async function exchangeOAuthCode(
  provider: OAuthProvider,
  payload: {
    code: string;
    redirect_uri: string;
    state: string;
    code_verifier: string;
  }
): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/v1/auth/oauth/${provider}/exchange`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(payload),
    cache: "no-store",
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || "OAuth exchange failed");
  }

  return await res.json();
}
