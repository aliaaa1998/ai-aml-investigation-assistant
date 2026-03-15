import pytest
from pydantic import ValidationError

from app.schemas.case import CaseInput, CustomerProfile


def test_case_input_requires_case_id_min_length():
    with pytest.raises(ValidationError):
        CaseInput(
            case_id="A",
            customer_profile=CustomerProfile(
                name="x", segment="retail", country="US", risk_rating="low"
            ),
            alerts=[],
            transactions=[],
            analyst_notes="note",
        )
