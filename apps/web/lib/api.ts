const getApiBaseUrl = (): string => {
  let url = process.env.NEXT_PUBLIC_API_URL || "";

  if (!url) {
    if (
      typeof window !== "undefined" &&
      !window.location.hostname.includes("localhost") &&
      !window.location.hostname.includes("127.0.0.1")
    ) {
      url = "https://college-rag-backend-64ny.onrender.com/api/v1";
    } else {
      url = "http://localhost:8000/api/v1";
    }
  }

  // Remove trailing slashes
  url = url.replace(/\/+$/, "");

  // CRITICAL: Auto-upgrade http:// to https:// for cloud/production domains
  // Browsers block unencrypted HTTP requests from HTTPS pages (Mixed Content security error)
  if (url.startsWith("http://") && !url.includes("localhost") && !url.includes("127.0.0.1")) {
    url = url.replace("http://", "https://");
  }

  return url;
};

export interface User {
  id: string;
  email: string;
  full_name?: string;
  role: "student" | "admin";
  is_active: boolean;
  created_at: string;
}

export interface Citation {
  id?: string;
  document_id?: string;
  document_name: string;
  chunk_id?: string;
  page_number?: number;
  similarity_score: number;
  citation_order: number;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  status: "PENDING" | "STREAMING" | "COMPLETED" | "FAILED";
  created_at: string;
  citations?: Citation[];
}

export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages?: Message[];
}

export interface DocumentItem {
  id: string;
  collection_id?: string;
  uploaded_by?: string;
  title: string;
  original_filename: string;
  mime_type: string;
  file_size: number;
  status: "UPLOADED" | "PROCESSING" | "READY" | "FAILED" | "ARCHIVED" | "SUPERSEDED";
  version: number;
  page_count?: number;
  chunk_count: number;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface CollectionItem {
  id: string;
  name: string;
  slug: string;
  description?: string;
  department?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface JobItem {
  id: string;
  type: string;
  status: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED" | "CANCELLED";
  entity_id?: string;
  progress: number;
  message?: string;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

export interface AnalyticsOverview {
  users: number;
  documents: number;
  ready_documents: number;
  processing_documents: number;
  failed_documents: number;
  questions: number;
  failed_jobs: number;
  average_retrieval_score: number;
}

class ApiClient {
  private get baseUrl(): string {
    return getApiBaseUrl();
  }

  private getHeaders(isJson: boolean = true): HeadersInit {
    const headers: Record<string, string> = {};
    if (isJson) {
      headers["Content-Type"] = "application/json";
    }
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("token");
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }
    }
    return headers;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const isFormData = options.body instanceof FormData;
    const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
    const url = `${this.baseUrl}${cleanEndpoint}`;
    let res: Response;

    try {
      res = await fetch(url, {
        ...options,
        credentials: "include",
        headers: {
          ...this.getHeaders(!isFormData),
          ...options.headers,
        },
      });
    } catch (netErr: any) {
      const isRender = this.baseUrl.includes("onrender.com");
      const hint = isRender
        ? " (Note: Render free services may take ~30-50s to wake up on the first request. Please wait a moment and try again)."
        : "";
      throw new Error(
        `Could not connect to backend API at ${url}. Please verify that the backend server is active and reachable${hint}`
      );
    }

    if (!res.ok) {
      let errorMsg = `Error ${res.status}: ${res.statusText}`;
      try {
        const errorData = await res.json();
        if (errorData.detail) errorMsg = errorData.detail;
        else if (errorData.error?.message) errorMsg = errorData.error.message;
      } catch {}
      throw new Error(errorMsg);
    }

    if (res.status === 204) {
      return {} as T;
    }

    return res.json();
  }

  // Auth
  async register(data: { email: string; password: string; full_name?: string }): Promise<User> {
    return this.request<User>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async login(data: { email: string; password: string }): Promise<{ access_token: string; user: User }> {
    const res = await this.request<{ access_token: string; user: User }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
    if (typeof window !== "undefined" && res.access_token) {
      localStorage.setItem("token", res.access_token);
    }
    return res;
  }

  async logout(): Promise<void> {
    try {
      await this.request("/auth/logout", { method: "POST" });
    } finally {
      if (typeof window !== "undefined") {
        localStorage.removeItem("token");
      }
    }
  }

  async getMe(): Promise<User> {
    return this.request<User>("/auth/me");
  }

  // Conversations
  async listConversations(): Promise<Conversation[]> {
    return this.request<Conversation[]>("/conversations");
  }

  async createConversation(title?: string): Promise<Conversation> {
    return this.request<Conversation>("/conversations", {
      method: "POST",
      body: JSON.stringify({ title }),
    });
  }

  async getConversation(id: string): Promise<Conversation> {
    return this.request<Conversation>(`/conversations/${id}`);
  }

  async updateConversationTitle(id: string, title: string): Promise<Conversation> {
    return this.request<Conversation>(`/conversations/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ title }),
    });
  }

  async deleteConversation(id: string): Promise<void> {
    return this.request(`/conversations/${id}`, { method: "DELETE" });
  }

  async sendMessage(conversationId: string, content: string, collectionId?: string): Promise<Message> {
    return this.request<Message>(`/conversations/${conversationId}/messages`, {
      method: "POST",
      body: JSON.stringify({ content, collection_id: collectionId }),
    });
  }

  async submitFeedback(messageId: string, rating: "positive" | "negative", comment?: string) {
    return this.request(`/messages/${messageId}/feedback`, {
      method: "POST",
      body: JSON.stringify({ rating, comment }),
    });
  }

  // Admin
  async listDocuments(params?: { status?: string; search?: string; page?: number }): Promise<{ items: DocumentItem[]; total: number }> {
    const query = new URLSearchParams();
    if (params?.status) query.set("status", params.status);
    if (params?.search) query.set("search", params.search);
    if (params?.page) query.set("page", params.page.toString());
    return this.request(`/admin/documents?${query.toString()}`);
  }

  async uploadDocument(formData: FormData): Promise<DocumentItem> {
    return this.request<DocumentItem>("/admin/documents", {
      method: "POST",
      body: formData,
    });
  }

  async deleteDocument(id: string): Promise<void> {
    return this.request(`/admin/documents/${id}`, { method: "DELETE" });
  }

  async reindexDocument(id: string): Promise<DocumentItem> {
    return this.request<DocumentItem>(`/admin/documents/${id}/reindex`, { method: "POST" });
  }

  async listCollections(): Promise<CollectionItem[]> {
    return this.request<CollectionItem[]>("/admin/collections");
  }

  async createCollection(data: { name: string; description?: string; department?: string }): Promise<CollectionItem> {
    return this.request<CollectionItem>("/admin/collections", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async deleteCollection(id: string): Promise<void> {
    return this.request(`/admin/collections/${id}`, { method: "DELETE" });
  }

  async listJobs(): Promise<JobItem[]> {
    return this.request<JobItem[]>("/admin/jobs");
  }

  async getAnalytics(): Promise<AnalyticsOverview> {
    return this.request<AnalyticsOverview>("/admin/analytics/overview");
  }
}

export const api = new ApiClient();
