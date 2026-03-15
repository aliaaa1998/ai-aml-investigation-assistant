from app.schemas.case import AlertItem, CaseInput, CustomerProfile, TransactionItem
from app.services.transaction_pattern_service import TransactionPatternService


def _base_case(transactions):
    return CaseInput(
        case_id="AML-TEST-1",
        customer_profile=CustomerProfile(
            name="Test",
            segment="retail",
            country="US",
            occupation_or_industry="teacher",
            risk_rating="low",
        ),
        alerts=[AlertItem(alert_type="x", score=60, description="d")],
        transactions=transactions,
        analyst_notes="notes",
    )


def test_extracts_sub_threshold_and_rapid_movement_patterns():
    txns = [
        TransactionItem(
            date="2026-01-01",
            amount=9900,
            currency="USD",
            type="dep",
            channel="branch",
            direction="inbound",
            destination_country="US",
        ),
        TransactionItem(
            date="2026-01-02",
            amount=9800,
            currency="USD",
            type="dep",
            channel="branch",
            direction="inbound",
            destination_country="US",
        ),
        TransactionItem(
            date="2026-01-03",
            amount=9700,
            currency="USD",
            type="dep",
            channel="branch",
            direction="inbound",
            destination_country="US",
        ),
        TransactionItem(
            date="2026-01-04",
            amount=9600,
            currency="USD",
            type="dep",
            channel="branch",
            direction="inbound",
            destination_country="US",
        ),
        TransactionItem(
            date="2026-01-05",
            amount=9500,
            currency="USD",
            type="dep",
            channel="branch",
            direction="inbound",
            destination_country="US",
        ),
        TransactionItem(
            date="2026-01-06",
            amount=47000,
            currency="USD",
            type="wire",
            channel="online",
            direction="outbound",
            destination_country="MX",
        ),
    ]
    result = TransactionPatternService().extract_patterns(_base_case(txns))
    assert "repeated_sub_threshold_transactions" in result["patterns"]
    assert "rapid_movement_of_funds" in result["patterns"]


def test_detects_cross_border_and_profile_mismatch():
    txns = [
        TransactionItem(
            date="2026-01-01",
            amount=100000,
            currency="USD",
            type="wire",
            channel="online",
            direction="outbound",
            destination_country="AE",
        ),
        TransactionItem(
            date="2026-01-02",
            amount=120000,
            currency="USD",
            type="wire",
            channel="online",
            direction="outbound",
            destination_country="SG",
        ),
        TransactionItem(
            date="2026-01-03",
            amount=110000,
            currency="USD",
            type="wire",
            channel="online",
            direction="outbound",
            destination_country="TR",
        ),
    ]
    result = TransactionPatternService().extract_patterns(_base_case(txns))
    assert "cross_border_activity" in result["patterns"]
    assert "profile_behavior_mismatch" in result["patterns"]
