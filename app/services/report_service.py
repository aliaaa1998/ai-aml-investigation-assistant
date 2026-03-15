from pathlib import Path
from uuid import uuid4

import structlog
from sqlalchemy.orm import Session

from app.repositories.case_repository import CaseRepository
from app.schemas.case import DraftReportRequest, DraftReportResponse
from app.services.openai_service import OpenAIService
from app.utils.time import Timer

logger = structlog.get_logger(__name__)


class ReportService:
    def __init__(self, db: Session, openai_service: OpenAIService):
        self.db = db
        self.repo = CaseRepository(db)
        self.openai_service = openai_service

    def draft_report(self, request: DraftReportRequest) -> DraftReportResponse:
        case_id = request.case_id
        payload = request.model_dump(mode="json")
        if request.case_id and not request.case_payload:
            analysis = self.repo.get_latest_analysis_by_case(request.case_id)
            if analysis:
                payload["analysis"] = analysis.result_payload
                case_id = request.case_id

        with Timer() as timer:
            ai_response = self.openai_service.draft_report(payload)

        report = self.repo.create_report(
            case_id=case_id or request.case_payload.case_id,
            request_id=ai_response["id"],
            output_type=request.output_type,
            content=ai_response["text"],
            model_name=ai_response["model"] or "n/a",
            latency_ms=timer.elapsed_ms,
        )
        self.db.commit()
        self._save_artifact(report.id, report.case_id, report.content)
        logger.info("report.completed", report_id=report.id, case_id=report.case_id)
        return DraftReportResponse(
            report_id=report.id,
            case_id=report.case_id,
            output_type=report.output_type,
            content=report.content,
            model=report.model_name,
            latency_ms=report.latency_ms,
            request_id=report.request_id or str(uuid4()),
        )

    @staticmethod
    def _save_artifact(report_id: str, case_id: str, content: str) -> None:
        p = Path("artifacts/reports")
        p.mkdir(parents=True, exist_ok=True)
        (p / f"{case_id}-{report_id}.md").write_text(content, encoding="utf-8")
