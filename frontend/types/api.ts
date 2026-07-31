export type InventoryItem = {
  id: string;
  product_name: string;
  brand: string | null;
  upc: string | null;
  lot_code: string | null;
  quantity: string | null;
  unit: string | null;
  location: string | null;
  location_type: string | null;
  location_criticality: string | null;
  public_serving: boolean;
  region: string | null;
  supplier: string | null;
  purchase_date: string | null;
  active: boolean;
  inventory_source: string | null;
  demo_company_id: string | null;
  demo_company_name: string | null;
};

export type DemoCompany = {
  id: string;
  name: string;
  company_type: string;
  description: string;
  risk_context: string;
  item_count: number;
  recommended: boolean;
};

export type ImportStatus = {
  source: string;
  status: "idle" | "running" | "succeeded" | "failed" | string;
  imported: number;
  updated: number;
  skipped: number;
  error: string | null;
  last_attempt_at: string | null;
  last_success_at: string | null;
  refresh_after_minutes: number;
  should_refresh: boolean;
};

export type Recall = {
  id: string;
  source: string;
  product_description: string;
  brand_name: string | null;
  recalling_firm: string | null;
  classification: string | null;
  reason_for_recall: string | null;
  recall_initiation_date: string | null;
  match_count: number;
  highest_confidence: string | null;
};

export type RecallDetail = Recall & {
  source_recall_id: string;
  source_url: string | null;
  status: string | null;
  distribution_pattern: string | null;
  report_date: string | null;
  termination_date: string | null;
  summary: string | null;
  audit_events: AuditEvent[];
};

export type RecallMatch = {
  id: string;
  recall_id: string;
  inventory_item_id: string;
  score: string;
  confidence: "high" | "medium" | "low";
  exposure_score: string;
  exposure_level: "critical" | "high" | "medium" | "low";
  exposure_factors: {
    summary?: string;
    weights?: Record<string, number>;
    scores?: Record<string, number>;
  };
  status: "needs_review" | "confirmed" | "dismissed" | "resolved";
  signals: Array<{ name: string; score: number; weight: number; detail: string; matched_values: Record<string, unknown> }>;
  explanation: string;
  matched_fields: Record<string, unknown>;
  reviewed_at: string | null;
  inventory_item: InventoryItem | null;
  recall: Recall | null;
};

export type AuditEvent = {
  id: string;
  entity_type: string;
  entity_id: string;
  event_type: string;
  actor_type: string;
  actor_label: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type DashboardSummary = {
  active_recalls: number;
  inventory_items: number;
  matches_needing_review: number;
  high_confidence_matches: number;
  matches_by_status: Record<string, number>;
  matches_by_confidence: Record<string, number>;
  matches_by_exposure: Record<string, number>;
  recall_source_counts: Record<string, number>;
  current_inventory_company: { id?: string; name?: string; inventory_source?: string; item_count?: number } | null;
  top_exposed_locations: Array<{ label: string; count: number; max_exposure_score: number }>;
  top_exposed_suppliers: Array<{ label: string; count: number; max_exposure_score: number }>;
  recent_activity: AuditEvent[];
  high_risk_matches: RecallMatch[];
};
