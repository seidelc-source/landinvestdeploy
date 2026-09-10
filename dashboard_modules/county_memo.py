"""Pure Markdown rendering helpers for county memo exports."""

from __future__ import annotations

from typing import Iterable


def _extend_or_default(lines: list[str], markdown_lines: Iterable[str], default_line: str) -> None:
    emitted = [line for line in markdown_lines if str(line).strip()]
    if emitted:
        lines.extend(emitted)
    else:
        lines.append(default_line)


def render_county_memo_markdown(
    *,
    county_name: str,
    state: str,
    fips: str,
    generated_at: str,
    summary: str,
    score_snapshot_lines: Iterable[str],
    support_lines: Iterable[str],
    brake_lines: Iterable[str],
    preboom_signal_lines: Iterable[str],
    xfactor_theme_lines: Iterable[str],
    structural_summary: str,
    decision_thesis: str,
    confidence_label: str,
    confidence_lines: Iterable[str],
    analog_lines: Iterable[str],
    parcel_readiness: str,
    diligence_lines: Iterable[str],
    thesis_breaker_lines: Iterable[str],
) -> str:
    lines = [
        f"# LandInvest County Memo: {county_name}, {state}",
        "",
        f"- FIPS: `{fips}`",
        f"- Generated at: `{generated_at}`",
        "- Use: county-level screening memo, not investment advice or parcel-level diligence.",
        "",
        "## Summary Thesis",
        "",
        summary,
        "",
        "## Score Snapshot",
        "",
    ]
    lines.extend(score_snapshot_lines)
    lines.extend(["", "## Key Supports", ""])
    _extend_or_default(lines, support_lines, "- No positive driver summary is currently available.")
    lines.extend(["", "## Key Brakes", ""])
    _extend_or_default(lines, brake_lines, "- No caution summary is currently available.")
    lines.extend(["", "## X-Factor / Pre-Boom Signals", ""])
    _extend_or_default(lines, preboom_signal_lines, "- This county is not currently present in the loaded top pre-boom review surfaces.")
    if any(str(line).strip() for line in xfactor_theme_lines):
        lines.extend(xfactor_theme_lines)
    lines.extend(["", "## Structural Land Context", "", structural_summary, f"- Decision thesis: {decision_thesis}"])
    lines.extend(["", "## Risk And Uncertainty", "", f"- Confidence read: `{confidence_label}`"])
    _extend_or_default(lines, confidence_lines, "- No confidence bullet summary is currently available.")
    lines.extend(["", "## Similar Historical Analogs", ""])
    _extend_or_default(lines, analog_lines, "- No analog library context is currently available for this county.")
    lines.extend(["", "## Diligence Checklist", "", f"- Parcel readiness: `{parcel_readiness}`"])
    _extend_or_default(lines, diligence_lines, "- Operator check required before parcel-level action.")
    lines.extend(["", "## What Would Make This Thesis Wrong", ""])
    _extend_or_default(lines, thesis_breaker_lines, "- No thesis-breaker checklist is currently available.")
    return "\n".join(lines).rstrip() + "\n"
