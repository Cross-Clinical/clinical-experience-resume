"""Validate vendored shadowing-hours-schema."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schema" / "shadowing-hour-record.schema.json").read_text())

EXAMPLE = {
    "schema_version": "0.1.0",
    "student": {"name": "Alex Rivera", "school": "State University"},
    "host": {"name": "Dr. Jordan Lee", "credential_tier": "licensed"},
    "site": {"name": "Riverside Community Hospital", "location": "Austin, TX"},
    "specialty": "Emergency Medicine",
    "started_at": "2026-06-10T14:00:00-05:00",
    "ended_at": "2026-06-10T18:00:00-05:00",
    "hours": 4,
    "mode": "in_person",
    "verification": {
        "status": "verified",
        "verified_at": "2026-06-10T18:05:00-05:00",
        "verifier_name": "Dr. Jordan Lee",
    },
}


class TestSchema(unittest.TestCase):
    def test_example_record_validates(self) -> None:
        validate(EXAMPLE, SCHEMA)

    def test_schema_has_email_format(self) -> None:
        email = SCHEMA["properties"]["student"]["properties"]["email"]
        self.assertEqual(email.get("format"), "email")


if __name__ == "__main__":
    unittest.main()
