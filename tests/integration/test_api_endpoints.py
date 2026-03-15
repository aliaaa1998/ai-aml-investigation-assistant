from fastapi.testclient import TestClient

from app.api.v1.routes import get_db
from app.main import app
from app.schemas.case import AnalysisResultPayload, AnalyzeCaseResponse, DraftReportResponse


class DummyDB:
    def commit(self):
        return None

    def close(self):
        return None


app.dependency_overrides[get_db] = lambda: DummyDB()


def test_health_and_readyz():
    client = TestClient(app)
    assert client.get("/api/v1/healthz").status_code == 200
    assert client.get("/api/v1/readyz").status_code == 200


def test_analyze_endpoint_with_mocked_service(monkeypatch):
    from app.api.v1 import routes

    def fake_analyze_case(self, payload):
        return AnalyzeCaseResponse(
            request_id="req_1",
            correlation_id="corr_1",
            model="gpt-test",
            latency_ms=5,
            analysis=AnalysisResultPayload(
                case_id=payload.case_id,
                summary="summary",
                observed_patterns=["pattern"],
                risk_indicators=[{"indicator": "x", "severity": "low", "rationale": "r"}],
                assessment="assessment",
                recommended_actions=["review"],
                escalation={"recommended": False, "reason": "insufficient information"},
                limitations=["missing kyc"],
                confidence="low",
            ),
        )

    monkeypatch.setattr(routes.AMLAnalysisService, "analyze_case", fake_analyze_case)
    client = TestClient(app)
    payload = {
        "case_id": "AML-1",
        "customer_profile": {
            "name": "n",
            "segment": "retail",
            "country": "US",
            "risk_rating": "low",
        },
        "alerts": [],
        "transactions": [],
        "analyst_notes": "note",
    }
    res = client.post("/api/v1/cases/analyze", json=payload)
    assert res.status_code == 200
    assert res.json()["analysis"]["case_id"] == "AML-1"


def test_draft_report_endpoint_with_mocked_service(monkeypatch):
    from app.api.v1 import routes

    def fake_draft(self, payload):
        return DraftReportResponse(
            report_id="r1",
            case_id=payload.case_payload.case_id,
            output_type=payload.output_type,
            content="## Case Overview",
            model="gpt-test",
            latency_ms=7,
            request_id="req_2",
        )

    monkeypatch.setattr(routes.ReportService, "draft_report", fake_draft)
    client = TestClient(app)
    payload = {
        "output_type": "analyst_memo",
        "case_payload": {
            "case_id": "AML-2",
            "customer_profile": {
                "name": "n",
                "segment": "retail",
                "country": "US",
                "risk_rating": "low",
            },
            "alerts": [],
            "transactions": [],
            "analyst_notes": "note",
        },
    }
    res = client.post("/api/v1/cases/draft-report", json=payload)
    assert res.status_code == 200
    assert res.json()["report_id"] == "r1"
