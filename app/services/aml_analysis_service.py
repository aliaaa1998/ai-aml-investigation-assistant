import json
import uuid

import structlog
from sqlalchemy.orm import Session

from app.repositories.case_repository import CaseRepository
from app.schemas.case import AnalysisResultPayload, AnalyzeCaseResponse, CaseInput
from app.services.openai_service import OpenAIService
from app.services.transaction_pattern_service import TransactionPatternService
from app.utils.time import Timer

logger = structlog.get_logger(__name__)

ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "case_id": {"type": "string"},
        "summary": {"type": "string"},
        "observed_patterns": {"type": "array", "items": {"type": "string"}},
        "risk_indicators": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "indicator": {"type": "string"},
                    "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                    "rationale": {"type": "string"},
                },
                "required": ["indicator", "severity", "rationale"],
                "additionalProperties": False,
            },
        },
        "assessment": {"type": "string"},
        "recommended_actions": {"type": "array", "items": {"type": "string"}},
        "escalation": {
            "type": "object",
            "properties": {"recommended": {"type": "boolean"}, "reason": {"type": "string"}},
            "required": ["recommended", "reason"],
            "additionalProperties": False,
        },
        "limitations": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
    },
    "required": [
        "case_id",
        "summary",
        "observed_patterns",
        "risk_indicators",
        "assessment",
        "recommended_actions",
        "escalation",
        "limitations",
        "confidence",
    ],
    "additionalProperties": False,
}


class AMLAnalysisService:
    def __init__(self, db: Session, openai_service: OpenAIService):
        self.repo = CaseRepository(db)
        self.db = db
        self.openai_service = openai_service
        self.pattern_service = TransactionPatternService()

    def analyze_case(self, case: CaseInput) -> AnalyzeCaseResponse:
        correlation_id = str(uuid.uuid4())
        patterns = self.pattern_service.extract_patterns(case)
        sanitized_input = {
            "case_id": case.case_id,
            "customer_segment": case.customer_profile.segment,
            "alert_count": len(case.alerts),
            "transaction_count": len(case.transactions),
        }
        payload = {"case": case.model_dump(mode="json"), "deterministic_signals": patterns}

        logger.info("analyze_case.started", case_id=case.case_id, correlation_id=correlation_id)
        with Timer() as timer:
            ai_response = self.openai_service.analyze_case(payload, ANALYSIS_SCHEMA)

        parsed = AnalysisResultPayload.model_validate(json.loads(ai_response["text"]))
        run = self.repo.create_case_run(
            case_id=case.case_id,
            correlation_id=correlation_id,
            request_id=ai_response["id"],
            model_name=ai_response["model"],
            latency_ms=timer.elapsed_ms,
            token_usage=ai_response.get("usage"),
            sanitized_input_preview=sanitized_input,
            escalation_flag=parsed.escalation.recommended,
            confidence=parsed.confidence,
        )
        self.repo.create_input_snapshot(
            case_run_id=run.id, case_id=case.case_id, input_payload=case.model_dump(mode="json")
        )
        self.repo.create_analysis_result(
            case_run_id=run.id, case_id=case.case_id, result_payload=parsed.model_dump(mode="json")
        )
        self.db.commit()
        logger.info(
            "analyze_case.completed",
            case_id=case.case_id,
            latency_ms=timer.elapsed_ms,
            request_id=ai_response["id"],
        )

        return AnalyzeCaseResponse(
            request_id=ai_response["id"] or "n/a",
            correlation_id=correlation_id,
            model=ai_response["model"] or "n/a",
            latency_ms=timer.elapsed_ms,
            analysis=parsed,
        )
