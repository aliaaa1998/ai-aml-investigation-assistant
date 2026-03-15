"""init schema"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260801_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "case_runs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("case_id", sa.String(), nullable=False),
        sa.Column("correlation_id", sa.String(), nullable=False),
        sa.Column("request_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("model_name", sa.String(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("token_usage", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("sanitized_input_preview", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("escalation_flag", sa.Boolean(), nullable=False),
        sa.Column("confidence", sa.String(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_case_runs_case_id", "case_runs", ["case_id"])
    op.create_index("ix_case_runs_correlation_id", "case_runs", ["correlation_id"])

    op.create_table(
        "case_input_snapshots",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("case_run_id", sa.String(), nullable=False),
        sa.Column("case_id", sa.String(), nullable=False),
        sa.Column("input_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["case_run_id"], ["case_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_case_input_snapshots_case_run_id", "case_input_snapshots", ["case_run_id"])
    op.create_index("ix_case_input_snapshots_case_id", "case_input_snapshots", ["case_id"])

    op.create_table(
        "analysis_results",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("case_run_id", sa.String(), nullable=False),
        sa.Column("case_id", sa.String(), nullable=False),
        sa.Column("result_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["case_run_id"], ["case_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analysis_results_case_run_id", "analysis_results", ["case_run_id"])
    op.create_index("ix_analysis_results_case_id", "analysis_results", ["case_id"])

    op.create_table(
        "report_results",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("case_id", sa.String(), nullable=False),
        sa.Column("request_id", sa.String(), nullable=True),
        sa.Column("output_type", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("model_name", sa.String(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_report_results_case_id", "report_results", ["case_id"])


def downgrade() -> None:
    op.drop_index("ix_report_results_case_id", table_name="report_results")
    op.drop_table("report_results")
    op.drop_index("ix_analysis_results_case_id", table_name="analysis_results")
    op.drop_index("ix_analysis_results_case_run_id", table_name="analysis_results")
    op.drop_table("analysis_results")
    op.drop_index("ix_case_input_snapshots_case_id", table_name="case_input_snapshots")
    op.drop_index("ix_case_input_snapshots_case_run_id", table_name="case_input_snapshots")
    op.drop_table("case_input_snapshots")
    op.drop_index("ix_case_runs_correlation_id", table_name="case_runs")
    op.drop_index("ix_case_runs_case_id", table_name="case_runs")
    op.drop_table("case_runs")
