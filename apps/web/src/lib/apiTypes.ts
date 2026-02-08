
export interface Prompt {
  id: string;
  slug: string;
  title: string;
  summary: string;

  worksWith: string[];
  tags: string[];
  targetSites: string[];
  promptText: string;
  steps: string[];
  notes: string;
  author_id?: string;
  createdAt: string; // ISO
  updatedAt: string; // ISO
  like_count?: number;
  saves_count?: number;
  comment_count?: number;
  type: "prompt" | "discussion";
  price: number;
  currency: string;
}

export interface Comment {
  id: string;
  prompt_id: string;
  author_id: string;
  author?: UserPublic;
  body: string;
  createdAt: string; // ISO
  like_count?: number;
}

export interface UserPublic {
  id: string;
  username: string;
}

export interface CommentListResponse {
  items: Comment[];
}

export interface LikeStatusResponse {
  liked: boolean;
  likeCount: number;
}


export interface PromptListResponse {
  items: Prompt[];
  page: number;
  pageSize: number;
  total: number;
}

export interface TagsResponse {
  items: string[];
}

export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
  createdAt: string;
  stripe_connect_id?: string;
  is_seller?: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

