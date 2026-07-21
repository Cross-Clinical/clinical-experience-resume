"""Clinical Experience Resume — consumes shadowing-hours-schema 0.1.0."""

from __future__ import annotations

import json
from pathlib import Path

import gradio as gr
from jsonschema import validate, ValidationError

from input_guard import DISCLAIMER

SCHEMA = json.loads(
    (Path(__file__).parent / "schema" / "shadowing-hour-record.schema.json").read_text()
)
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


def _load_records(text: str, file_obj) -> list[dict]:
    raw = ""
    if file_obj is not None:
        raw = Path(file_obj.name).read_text()
    elif text and text.strip():
        raw = text
    else:
        raise ValueError("Paste JSON or upload a .json file.")
    data = json.loads(raw)
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    raise ValueError("JSON must be an object or array of hour records.")


def build_resume(text: str, file_obj, verified_only: bool) -> str:
    try:
        records = _load_records(text, file_obj)
    except Exception as exc:  # noqa: BLE001
        return f"Could not parse input: {exc}"

    lines = [
        f"_{DISCLAIMER}_",
        "",
        "## Clinical Shadowing Experience",
        "",
        f"_Exported with schema_version **0.1.0** (Cross Clinical shadowing-hours-schema)._",
        "",
    ]
    total = 0.0
    used = 0
    errors = []
    for i, rec in enumerate(records, 1):
        try:
            validate(rec, SCHEMA)
        except ValidationError as exc:
            errors.append(f"Record {i}: {exc.message}")
            continue
        if verified_only and rec["verification"]["status"] != "verified":
            continue
        used += 1
        total += float(rec["hours"])
        loc = rec["site"].get("location")
        site = rec["site"]["name"] + (f" ({loc})" if loc else "")
        status = rec["verification"]["status"]
        lines.append(
            f"- **{rec['specialty']}** — {rec['hours']} hours "
            f"({rec['mode'].replace('_', ' ')}) at {site}; "
            f"host {rec['host']['name']}; verification: {status} "
            f"[{rec['started_at'][:10]} → {rec['ended_at'][:10]}]"
        )
    if errors:
        lines.append("\n### Validation issues\n" + "\n".join(f"- {e}" for e in errors))
    if used:
        lines.insert(4, f"**Total hours included:** {total:g}\n")
    elif not errors:
        lines.append("_No records matched filters._")
    return "\n".join(lines)


with gr.Blocks(title="Clinical Experience Resume") as demo:
    gr.Markdown(
        f"# Clinical Experience Resume\n\n**{DISCLAIMER}**\n\n"
        "Consumes [shadowing-hours-schema@0.1.0](https://github.com/Cross-Clinical/shadowing-hours-schema).\n\n"
        "[Cross Clinical OSS](https://github.com/Cross-Clinical/awesome) · "
        "[ProMedNet](https://crossclinical.com)"
    )
    text = gr.Code(language="json", label="Paste JSON (object or array)", value=json.dumps(EXAMPLE, indent=2))
    upload = gr.File(label="Or upload .json", file_types=[".json"])
    verified = gr.Checkbox(value=True, label="Verified hours only")
    out = gr.Markdown()
    gr.Button("Build résumé section").click(build_resume, [text, upload, verified], out)

if __name__ == "__main__":
    demo.launch()
