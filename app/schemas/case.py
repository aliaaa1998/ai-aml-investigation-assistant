from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class CustomerProfile(BaseModel):
    name: str
    segment: str
    country: str
    occupation_or_industry: str | None = None
    risk_rating: Literal["low", "medium", "high"] = "medium"


class AlertItem(BaseModel):
    alert_type: str
    score: float = Field(ge=0, le=100)
    description: str
    triggered_rules: list[str] = Field(default_factory=list)


class TransactionItem(BaseModel):
    date: date
    amount: float = Field(gt=0)
    currency: str
    type: str
    channel: str
    direction: Literal["inbound", "outbound"]
    destination_country: str | None = None
    counterparty: str | None = None


class CaseInput(BaseModel):
    case_id: str
    customer_profile: CustomerProfile
    alerts: list[AlertItem] = Field(default_factory=list)
    transactions: list[TransactionItem] = Field(default_factory=list, max_length=5000)
    analyst_notes: str
    supporting_context: str | None = None
    policy_notes: str | None = None

    @field_validator("case_id")
    @classmethod
    def valid_case_id(cls, value: str) -> str:
        if len(value) < 3:
            raise ValueError("case_id too short")
        return value


class RiskIndicator(BaseModel):
    indicator: str
    severity: Literal["low", "medium", "high"]
    rationale: str


class EscalationRecommendation(BaseModel):
    recommended: bool
    reason: str


class AnalysisResultPayload(BaseModel):
    case_id: str
    summary: str
    observed_patterns: list[str]
    risk_indicators: list[RiskIndicator]
    assessment: str
    recommended_actions: list[str]
    escalation: EscalationRecommendation
    limitations: list[str]
    confidence: Literal["low", "medium", "high"]


class AnalyzeCaseResponse(BaseModel):
    request_id: str
    correlation_id: str
    model: str
    latency_ms: int
    analysis: AnalysisResultPayload
    disclaimer: str = "Decision-support output only; requires human analyst validation."


class DraftReportRequest(BaseModel):
    case_id: str | None = None
    case_payload: CaseInput | None = None
    output_type: Literal["analyst_memo", "concise_summary", "manager_summary"] = "analyst_memo"
    tone: str = "formal"


class DraftReportResponse(BaseModel):
    report_id: str
    case_id: str
    output_type: str
    content: str
    model: str
    latency_ms: int
    request_id: str


class CaseListItem(BaseModel):
    case_id: str
    created_at: str
    escalation_recommended: bool
    confidence: str


class CaseDetailResponse(BaseModel):
    case_id: str
    created_at: str
    request_id: str
    correlation_id: str
    status: str
    analysis: dict


class ReportDetailResponse(BaseModel):
    report_id: str
    case_id: str
    output_type: str
    content: str
    created_at: str
