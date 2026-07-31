import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ApiError(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class RecallListItem(BaseModel):
    id: uuid.UUID
    source: str
    product_description: str
    brand_name: str | None
    recalling_firm: str | None
    classification: str | None
    reason_for_recall: str | None
    recall_initiation_date: date | None
    match_count: int = 0
    highest_confidence: str | None = None
    model_config = ConfigDict(from_attributes=True)


class PaginatedRecalls(BaseModel):
    items: list[RecallListItem]
    page: int
    page_size: int
    total: int


class AuditEventOut(BaseModel):
    id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID
    event_type: str
    actor_type: str
    actor_label: str | None
    metadata: dict[str, Any] = Field(default_factory=dict, validation_alias="metadata_", serialization_alias="metadata")
    created_at: datetime
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class RecallDetail(BaseModel):
    id: uuid.UUID
    source: str
    source_recall_id: str
    source_url: str | None
    status: str | None
    classification: str | None
    product_description: str
    brand_name: str | None
    recalling_firm: str | None
    reason_for_recall: str | None
    distribution_pattern: str | None
    recall_initiation_date: date | None
    report_date: date | None
    termination_date: date | None
    summary: str | None
    match_count: int = 0
    audit_events: list[AuditEventOut] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class InventoryItemOut(BaseModel):
    id: uuid.UUID
    product_name: str
    brand: str | None
    upc: str | None
    lot_code: str | None
    quantity: Decimal | None
    unit: str | None
    location: str | None
    location_type: str | None
    location_criticality: str | None
    public_serving: bool
    region: str | None
    supplier: str | None
    purchase_date: date | None
    active: bool
    inventory_source: str | None = None
    demo_company_id: str | None = None
    demo_company_name: str | None = None
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def add_safe_inventory_metadata(cls, value: Any) -> Any:
        if isinstance(value, dict):
            data = dict(value)
            raw_row = data.get("raw_row", {})
        else:
            raw_row = getattr(value, "raw_row", {})
            data = {field: getattr(value, field, None) for field in (
                "id", "product_name", "brand", "upc", "lot_code", "quantity", "unit",
                "location", "location_type", "location_criticality", "public_serving", "region",
                "supplier", "purchase_date", "active",
            )}
        if not isinstance(raw_row, dict):
            raw_row = {}
        data["inventory_source"] = data.get("inventory_source") or raw_row.get("inventory_source")
        data["demo_company_id"] = data.get("demo_company_id") or raw_row.get("demo_company_id")
        data["demo_company_name"] = data.get("demo_company_name") or raw_row.get("demo_company_name")
        return data


class DemoCompanyOut(BaseModel):
    id: str
    name: str
    company_type: str
    description: str
    risk_context: str
    item_count: int
    recommended: bool = False


class SeedCompanyRequest(BaseModel):
    company_id: str = Field(min_length=1, max_length=80)


class SeedCompanyResponse(BaseModel):
    created: int
    company: DemoCompanyOut


class RecallMatchOut(BaseModel):
    id: uuid.UUID
    recall_id: uuid.UUID
    inventory_item_id: uuid.UUID
    score: Decimal
    confidence: str
    exposure_score: Decimal
    exposure_level: str
    exposure_factors: dict[str, Any]
    status: str
    signals: list[dict[str, Any]]
    explanation: str
    matched_fields: dict[str, Any]
    reviewed_at: datetime | None
    inventory_item: InventoryItemOut | None = None
    recall: RecallListItem | None = None
    model_config = ConfigDict(from_attributes=True)


class MatchList(BaseModel):
    items: list[RecallMatchOut]
    page: int = 1
    page_size: int = 50
    total: int


class ImportOpenFdaRequest(BaseModel):
    limit: int = Field(default=100, ge=1, le=1000)
    since: date | None = None
    force: bool = False


class ImportSummary(BaseModel):
    imported: int = 0
    updated: int = 0
    skipped: int = 0
    status: str = "succeeded"
    refreshed: bool = True


class ImportStatusOut(BaseModel):
    source: str = "openfda"
    status: str = "idle"
    imported: int = 0
    updated: int = 0
    skipped: int = 0
    error: str | None = None
    last_attempt_at: datetime | None = None
    last_success_at: datetime | None = None
    refresh_after_minutes: int = 30
    should_refresh: bool = True
    model_config = ConfigDict(from_attributes=True)


class SeedSummary(BaseModel):
    created: int


class UploadError(BaseModel):
    row: int
    message: str


class InventoryUploadResponse(BaseModel):
    uploaded_file_id: uuid.UUID
    row_count: int
    valid_row_count: int
    invalid_row_count: int
    errors: list[UploadError]


class MatchRunRequest(BaseModel):
    recall_id: uuid.UUID | None = None
    inventory_upload_id: uuid.UUID | None = None
    min_score: float = Field(default=0.35, ge=0, le=1)
    recall_source: str = Field(default="openfda", min_length=1, max_length=40)


class MatchRunResponse(BaseModel):
    created: int
    updated: int
    skipped: int


class MatchStatusRequest(BaseModel):
    status: str = Field(min_length=1, max_length=40)
    note: str | None = Field(default=None, max_length=1000)
    reviewer_name: str | None = Field(default="Demo User", max_length=120)


class MatchStatusResponse(BaseModel):
    id: uuid.UUID
    status: str
    reviewed_at: datetime | None


class DashboardSummary(BaseModel):
    active_recalls: int
    inventory_items: int
    matches_needing_review: int
    high_confidence_matches: int
    matches_by_status: dict[str, int]
    matches_by_confidence: dict[str, int]
    matches_by_exposure: dict[str, int]
    recall_source_counts: dict[str, int]
    current_inventory_company: dict[str, Any] | None = None
    top_exposed_locations: list[dict[str, Any]]
    top_exposed_suppliers: list[dict[str, Any]]
    recent_activity: list[AuditEventOut]
    high_risk_matches: list[RecallMatchOut]
