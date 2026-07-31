import type { DashboardSummary, DemoCompany, ImportStatus, Recall, RecallDetail, RecallMatch, InventoryItem } from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    cache: "no-store",
    headers: init?.body instanceof FormData ? init.headers : { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function getDashboard(): Promise<DashboardSummary> {
  return request<DashboardSummary>("/dashboard/summary");
}

export async function getRecalls(filters?: { source?: string; classification?: string; has_matches?: string }): Promise<{ items: Recall[]; total: number }> {
  const params = new URLSearchParams({ page_size: "100" });
  if (filters?.source && filters.source !== "all") params.set("source", filters.source);
  if (filters?.classification && filters.classification !== "all") params.set("classification", filters.classification);
  if (filters?.has_matches === "with") params.set("has_matches", "true");
  if (filters?.has_matches === "none") params.set("has_matches", "false");
  return request<{ items: Recall[]; total: number }>(`/recalls?${params.toString()}`);
}

export async function getRecall(id: string): Promise<RecallDetail> {
  return request<RecallDetail>(`/recalls/${id}`);
}

export async function getRecallMatches(id: string): Promise<{ items: RecallMatch[] }> {
  return request<{ items: RecallMatch[] }>(`/recalls/${id}/matches`);
}

export async function getMatches(status?: string): Promise<{ items: RecallMatch[]; total: number }> {
  const query = status ? `?status=${status}` : "";
  return request<{ items: RecallMatch[]; total: number }>(`/matches${query}`);
}

export async function getInventory(): Promise<{ items: InventoryItem[]; total: number }> {
  return request<{ items: InventoryItem[]; total: number }>("/inventory?page_size=100");
}

export async function getDemoCompanies(): Promise<DemoCompany[]> {
  return request<DemoCompany[]>("/inventory/demo-companies");
}

export async function getImportStatus(): Promise<ImportStatus> {
  try {
    return await request<ImportStatus>("/recalls/imports/status");
  } catch {
    // Import status is supplemental; a cold or temporarily unavailable API
    // should not replace the recruiter-facing page with the error boundary.
    return {
      source: "openfda",
      status: "idle",
      imported: 0,
      updated: 0,
      skipped: 0,
      error: "Live refresh status is temporarily unavailable.",
      last_attempt_at: null,
      last_success_at: null,
      refresh_after_minutes: 30,
      should_refresh: false,
    };
  }
}

export async function postJson<T>(path: string, body: Record<string, unknown> = {}): Promise<T> {
  return request<T>(path, { method: "POST", body: JSON.stringify(body) });
}

export async function patchJson<T>(path: string, body: Record<string, unknown>): Promise<T> {
  return request<T>(path, { method: "PATCH", body: JSON.stringify(body) });
}

export { API_BASE_URL };
