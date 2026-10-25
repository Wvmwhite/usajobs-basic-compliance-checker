"""Compliance analysis against basic USAJOBS resume requirements."""

import re
from dataclasses import dataclass, field
from typing import Any


# Regex patterns for common fields
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(
    r"(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b"
)
# Month/year or MM/YYYY date patterns common in resumes
DATE_RE = re.compile(
    r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
    r"Dec(?:ember)?)\s+\d{4}\b|"
    r"\b\d{1,2}/\d{4}\b|"
    r"\b\d{4}\s*[-–—]\s*(?:present|current|now|\d{1,2}/\d{4}|[A-Za-z]+\s+\d{4})\b",
    re.IGNORECASE,
)
HOURS_RE = re.compile(
    r"\b(?:\d+\s*(?:hours?|hrs?)\s*(?:per\s*week|/week|weekly|a\s*week)|"
    r"\d+\s*hrs?/wk|\d+\s*hr/wk)\b",
    re.IGNORECASE,
)
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
EDUCATION_KEYWORDS = re.compile(
    r"\b(education|university|college|bachelor|master|ph\.?d|mba|degree|"
    r"diploma|gpa|associate|certification|license)\b",
    re.IGNORECASE,
)


@dataclass
class CheckResult:
    """Result of a single compliance check."""

    name: str
    passed: bool
    detail: str
    severity: str = "required"  # required | recommended | warning


@dataclass
class ComplianceReport:
    """Full compliance report."""

    file_info: dict[str, Any]
    checks: list[CheckResult] = field(default_factory=list)
    overall_pass: bool = False
    summary: str = ""

    def add(self, name: str, passed: bool, detail: str, severity: str = "required") -> None:
        self.checks.append(CheckResult(name, passed, detail, severity))


def _has_email(text: str) -> bool:
    return bool(EMAIL_RE.search(text))


def _has_phone(text: str) -> bool:
    return bool(PHONE_RE.search(text))


def _count_date_patterns(text: str) -> int:
    return len(DATE_RE.findall(text))


def _has_hours_indicator(text: str) -> bool:
    return bool(HOURS_RE.search(text))


def _has_ssn(text: str) -> bool:
    return bool(SSN_RE.search(text))


def _has_education_indicators(text: str) -> bool:
    return bool(EDUCATION_KEYWORDS.search(text))


def analyze_resume(extracted: dict[str, Any]) -> ComplianceReport:
    """
    Analyze extracted resume data against basic USAJOBS requirements.

    Returns a ComplianceReport. Does not raise on content issues; those become failed checks.
    """
    meta = extracted.get("metadata", {})
    text = extracted.get("text", "")
    page_count = extracted.get("page_count")
    page_reliable = extracted.get("page_count_reliable", False)

    report = ComplianceReport(file_info=meta)

    # File size
    size_ok = meta.get("size_ok", False)
    report.add(
        "File size ≤ 5 MB",
        size_ok,
        f"{meta.get('size_mb', '?')} MB (limit 5 MB)",
    )

    # Format
    format_ok = meta.get("format_ok", False)
    report.add(
        "Supported file format",
        format_ok,
        f"Detected: {meta.get('extension', 'unknown')}. Prefer PDF.",
    )

    # Length
    if page_count is None:
        length_ok = False
        length_detail = "Could not determine page count"
    else:
        length_ok = page_count <= 2
        reliability = "accurate" if page_reliable else "estimated (convert to PDF for reliable check)"
        length_detail = f"{page_count} page(s) ({reliability}). Limit is 2 pages."
    report.add("Length ≤ 2 pages", length_ok, length_detail)

    # Contact
    report.add(
        "Email address present",
        _has_email(text),
        "Found" if _has_email(text) else "No email address detected",
    )
    report.add(
        "Phone number present",
        _has_phone(text),
        "Found" if _has_phone(text) else "No phone number detected",
    )

    # Work experience structure
    date_count = _count_date_patterns(text)
    has_hours = _has_hours_indicator(text)
    # Heuristic: at least one date pattern and hours indicator somewhere
    experience_ok = date_count >= 1 and has_hours
    exp_detail = (
        f"Date-like patterns found: {date_count}. "
        f"Hours-per-week indicator: {'yes' if has_hours else 'no'}."
    )
    report.add(
        "Work experience structure (dates + hours/week)",
        experience_ok,
        exp_detail,
        severity="required",
    )

    # Education
    edu_ok = _has_education_indicators(text)
    report.add(
        "Education indicators present",
        edu_ok,
        "Education-related keywords found" if edu_ok else "No clear education section indicators",
        severity="recommended",
    )

    # Red flags
    has_ssn = _has_ssn(text)
    report.add(
        "No Social Security Number",
        not has_ssn,
        "SSN pattern detected — remove it" if has_ssn else "No SSN pattern found",
        severity="required",
    )

    # Text extracted successfully
    text_ok = len(text.strip()) > 50
    report.add(
        "Readable text extracted",
        text_ok,
        f"{len(text)} characters extracted" if text_ok else "Very little or no text extracted",
    )

    # Overall: all required checks must pass
    required_failed = [c for c in report.checks if c.severity == "required" and not c.passed]
    report.overall_pass = len(required_failed) == 0 and text_ok

    if report.overall_pass:
        report.summary = "Passes basic USAJOBS structural checks. Review job-specific requirements separately."
    else:
        failed_names = [c.name for c in required_failed]
        report.summary = (
            f"Fails one or more required checks: {', '.join(failed_names)}. "
            "Address these before submitting."
        )

    return report
