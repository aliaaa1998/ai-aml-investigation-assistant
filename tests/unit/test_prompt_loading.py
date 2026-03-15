from app.core.config import Settings
from app.services.openai_service import OpenAIService


def test_prompt_files_load():
    service = OpenAIService(Settings())
    assert "AML" in service._read_prompt("system.md")
    assert "JSON" in service._read_prompt("analysis.md")
