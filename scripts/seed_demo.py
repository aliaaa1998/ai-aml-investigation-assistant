"""Seed demo placeholder for local workflows."""
from pathlib import Path

print("Available cases:")
for p in sorted(Path("examples/cases").glob("*.json")):
    print("-", p.name)
