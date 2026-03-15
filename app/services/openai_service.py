import json
from pathlib import Path

from openai import OpenAI

from app.core.config import Settings


class OpenAIService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = OpenAI(
            api_key=settings.openai_api_key, timeout=settings.openai_request_timeout_seconds
        )
        self.prompt_dir = Path("app/prompts")

    def _read_prompt(self, name: str) -> str:
        return (self.prompt_dir / name).read_text(encoding="utf-8")

    def analyze_case(self, payload: dict, schema: dict) -> dict:
        response = self.client.responses.create(
            model=self.settings.openai_model_analysis,
            input=[
                {"role": "system", "content": self._read_prompt("system.md")},
                {
                    "role": "user",
                    "content": self._read_prompt("analysis.md") + "\n\n" + json.dumps(payload),
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "aml_analysis",
                    "schema": schema,
                    "strict": True,
                }
            },
        )
        return self._normalize_response(response)

    def draft_report(self, payload: dict) -> dict:
        response = self.client.responses.create(
            model=self.settings.openai_model_reports,
            input=[
                {"role": "system", "content": self._read_prompt("system.md")},
                {
                    "role": "user",
                    "content": self._read_prompt("report.md") + "\n\n" + json.dumps(payload),
                },
            ],
        )
        return self._normalize_response(response)

    @staticmethod
    def _normalize_response(response) -> dict:
        output_text = getattr(response, "output_text", "")
        usage = getattr(response, "usage", None)
        return {
            "id": getattr(response, "id", None),
            "model": getattr(response, "model", None),
            "text": output_text,
            "usage": usage.model_dump() if hasattr(usage, "model_dump") else None,
        }
