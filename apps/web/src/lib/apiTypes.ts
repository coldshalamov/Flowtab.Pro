
export interface Prompt {
  id: string;
  slug: string;
  title: string;
  summary: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  worksWith: string[];
  tags: string[];
  targetSites: string[];
  promptText: string;
  steps: string[];
  notes: string;
  createdAt: string; // ISO
  updatedAt: string; // ISO
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
