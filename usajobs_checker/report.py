"""Human-readable report generation."""

from .analyzer import ComplianceReport


def format_report(report: ComplianceReport) -> str:
    """Return a plain-text compliance report."""
    lines = []
    lines.append("=" * 60)
    lines.append("USAJOBS RESUME COMPLIANCE REPORT")
    lines.append("=" * 60)
    lines.append("")

    meta = report.file_info
    lines.append(f"File: {meta.get('filename', 'unknown')}")
    lines.append(f"Size: {meta.get('size_mb', '?')} MB")
    lines.append(f"Format: {meta.get('extension', 'unknown')}")
    lines.append("")

    lines.append(f"OVERALL: {'PASS' if report.overall_pass else 'FAIL'}")
    lines.append(report.summary)
    lines.append("")
    lines.append("-" * 60)
    lines.append("DETAILED CHECKS")
    lines.append("-" * 60)

    for check in report.checks:
        status = "PASS" if check.passed else "FAIL"
        sev = f"[{check.severity.upper()}]" if check.severity != "required" else ""
        lines.append(f"{status:4}  {check.name} {sev}")
        lines.append(f"       {check.detail}")
        lines.append("")

    lines.append("-" * 60)
    lines.append("NOTES")
    lines.append("-" * 60)
    lines.append(
        "• This checks basic structural requirements only "
        "(length, contact, experience fields, etc.)."
    )
    lines.append(
        "• Job announcements may require additional specialized experience, "
        "certifications, or other items."
    )
    lines.append(
        "• For DOCX files, page count is estimated. Convert to PDF for an accurate length check."
    )
    lines.append(
        "• Always review the current USAJOBS Help Center and the specific job announcement."
    )
    lines.append("")
    lines.append("Source guidance: help.usajobs.gov and OPM Merit Hiring Plan materials.")
    lines.append("=" * 60)

    return "\n".join(lines)
