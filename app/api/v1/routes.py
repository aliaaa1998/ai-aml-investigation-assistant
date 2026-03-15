from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.repositories.case_repository import CaseRepository
from app.schemas.case import (
    AnalyzeCaseResponse,
    CaseDetailResponse,
    CaseInput,
    CaseListItem,
    DraftReportRequest,
    DraftReportResponse,
    ReportDetailResponse,
)
from app.services.aml_analysis_service import AMLAnalysisService
from app.services.openai_service import OpenAIService
from app.services.report_service import ReportService

router = APIRouter(prefix="/api/v1")


def get_openai_service() -> OpenAIService:
    return OpenAIService(get_settings())


@router.post("/cases/analyze", response_model=AnalyzeCaseResponse)
def analyze_case(
    payload: CaseInput,
    db: Session = Depends(get_db),
    openai_service: OpenAIService = Depends(get_openai_service),
):
    service = AMLAnalysisService(db, openai_service)
    return service.analyze_case(payload)


@router.post("/cases/draft-report", response_model=DraftReportResponse)
def draft_report(
    payload: DraftReportRequest,
    db: Session = Depends(get_db),
    openai_service: OpenAIService = Depends(get_openai_service),
):
    if not payload.case_id and not payload.case_payload:
        raise HTTPException(status_code=400, detail="case_id or case_payload is required")
    service = ReportService(db, openai_service)
    return service.draft_report(payload)


@router.get("/cases", response_model=list[CaseListItem])
def list_cases(db: Session = Depends(get_db)):
    repo = CaseRepository(db)
    return [
        CaseListItem(
            case_id=c.case_id,
            created_at=c.created_at.isoformat(),
            escalation_recommended=c.escalation_flag,
            confidence=c.confidence or "unknown",
        )
        for c in repo.list_cases()
    ]


@router.get("/cases/{case_id}", response_model=CaseDetailResponse)
def get_case(case_id: str, db: Session = Depends(get_db)):
    repo = CaseRepository(db)
    found = repo.get_case(case_id)
    if not found:
        raise HTTPException(status_code=404, detail="case not found")
    run, result = found
    return CaseDetailResponse(
        case_id=run.case_id,
        created_at=run.created_at.isoformat(),
        request_id=run.request_id or "n/a",
        correlation_id=run.correlation_id,
        status=run.status,
        analysis=result.result_payload,
    )


@router.get("/reports/{report_id}", response_model=ReportDetailResponse)
def get_report(report_id: str, db: Session = Depends(get_db)):
    repo = CaseRepository(db)
    report = repo.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="report not found")
    return ReportDetailResponse(
        report_id=report.id,
        case_id=report.case_id,
        output_type=report.output_type,
        content=report.content,
        created_at=report.created_at.isoformat(),
    )


@router.get("/healthz")
def healthz():
    return {"status": "ok"}


@router.get("/readyz")
def readyz(request: Request):
    return {"status": "ready", "service": request.app.title}
