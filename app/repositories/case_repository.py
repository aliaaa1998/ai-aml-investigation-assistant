from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.entities import AnalysisResult, CaseInputSnapshot, CaseRun, ReportResult


class CaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_case_run(self, **kwargs) -> CaseRun:
        entity = CaseRun(**kwargs)
        self.db.add(entity)
        self.db.flush()
        return entity

    def create_input_snapshot(self, **kwargs) -> CaseInputSnapshot:
        entity = CaseInputSnapshot(**kwargs)
        self.db.add(entity)
        return entity

    def create_analysis_result(self, **kwargs) -> AnalysisResult:
        entity = AnalysisResult(**kwargs)
        self.db.add(entity)
        return entity

    def create_report(self, **kwargs) -> ReportResult:
        entity = ReportResult(**kwargs)
        self.db.add(entity)
        return entity

    def list_cases(self, limit: int = 100) -> list[CaseRun]:
        stmt = select(CaseRun).order_by(desc(CaseRun.created_at)).limit(limit)
        return list(self.db.scalars(stmt).all())

    def get_case(self, case_id: str) -> tuple[CaseRun, AnalysisResult] | None:
        run_stmt = (
            select(CaseRun)
            .where(CaseRun.case_id == case_id)
            .order_by(desc(CaseRun.created_at))
            .limit(1)
        )
        run = self.db.scalars(run_stmt).first()
        if not run:
            return None
        result_stmt = select(AnalysisResult).where(AnalysisResult.case_run_id == run.id)
        result = self.db.scalars(result_stmt).first()
        if not result:
            return None
        return run, result

    def get_report(self, report_id: str) -> ReportResult | None:
        stmt = select(ReportResult).where(ReportResult.id == report_id)
        return self.db.scalars(stmt).first()

    def get_latest_analysis_by_case(self, case_id: str) -> AnalysisResult | None:
        stmt = (
            select(AnalysisResult)
            .where(AnalysisResult.case_id == case_id)
            .order_by(desc(AnalysisResult.created_at))
            .limit(1)
        )
        return self.db.scalars(stmt).first()
