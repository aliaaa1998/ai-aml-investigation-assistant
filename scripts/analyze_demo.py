import json
from pathlib import Path

import httpx

case_path = Path("examples/cases/case_structuring.json")
payload = json.loads(case_path.read_text())
resp = httpx.post("http://localhost:8000/api/v1/cases/analyze", json=payload, timeout=30)
print(resp.status_code)
print(resp.text)
