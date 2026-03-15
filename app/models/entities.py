from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class CaseRun(Base):
    __tablename__ = "case_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    case_id: Mapped[str] = mapped_column(String, index=True)
    correlation_id: Mapped[str] = mapped_column(String, index=True)
    request_id: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="completed")
    model_name: Mapped[str | None] = mapped_column(String, nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    token_usage: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    sanitized_input_preview: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    escalation_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence: Mapped[str | None] = mapped_column(String, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    input_snapshot: Mapped["CaseInputSnapshot"] = relationship(
        back_populates="case_run", uselist=False
    )
    analysis_result: Mapped["AnalysisResult"] = relationship(
        back_populates="case_run", uselist=False
    )


class CaseInputSnapshot(Base):
    __tablename__ = "case_input_snapshots"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    case_run_id: Mapped[str] = mapped_column(ForeignKey("case_runs.id"), index=True)
    case_id: Mapped[str] = mapped_column(String, index=True)
    input_payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case_run: Mapped[CaseRun] = relationship(back_populates="input_snapshot")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    case_run_id: Mapped[str] = mapped_column(ForeignKey("case_runs.id"), index=True)
    case_id: Mapped[str] = mapped_column(String, index=True)
    result_payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case_run: Mapped[CaseRun] = relationship(back_populates="analysis_result")


class ReportResult(Base):
    __tablename__ = "report_results"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    case_id: Mapped[str] = mapped_column(String, index=True)
    request_id: Mapped[str | None] = mapped_column(String, nullable=True)
    output_type: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)
    model_name: Mapped[str] = mapped_column(String)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
