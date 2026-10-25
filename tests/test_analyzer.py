"""Unit tests for the analyzer (pure functions, no file I/O)."""

import pytest

from usajobs_checker.analyzer import analyze_resume


def _make_extracted(
    text: str,
    size_mb: float = 0.5,
    extension: str = ".pdf",
    page_count: int = 2,
    page_reliable: bool = True,
) -> dict:
    return {
        "metadata": {
            "filename": "test.pdf",
            "size_mb": size_mb,
            "size_ok": size_mb <= 5.0,
            "extension": extension,
            "format_ok": extension in {".pdf", ".docx"},
        },
        "page_count": page_count,
        "page_count_reliable": page_reliable,
        "text": text,
        "text_length": len(text),
    }


def test_good_resume_passes():
    text = """
    Jane Doe
    jane.doe@email.com
    (202) 555-1234

    Work Experience
    Program Analyst
    Department of Example, Washington DC
    January 2020 – Present
    40 hours/week
    Led analysis of program data and produced reports.

    Education
    Bachelor of Science, Example University, 2019
    """
    extracted = _make_extracted(text)
    report = analyze_resume(extracted)
    assert report.overall_pass is True
    # Spot-check a few required items
    names = {c.name: c.passed for c in report.checks}
    assert names["Email address present"] is True
    assert names["Phone number present"] is True
    assert names["Work experience structure (dates + hours/week)"] is True
    assert names["No Social Security Number"] is True


def test_missing_hours_fails():
    text = """
    Jane Doe
    jane.doe@email.com
    202-555-1234
    January 2020 – Present
    Program Analyst at Example Agency.
    Education: Bachelor degree.
    """
    extracted = _make_extracted(text)
    report = analyze_resume(extracted)
    assert report.overall_pass is False
    exp_check = next(c for c in report.checks if "Work experience" in c.name)
    assert exp_check.passed is False


def test_too_long_fails():
    text = "Jane Doe jane@email.com 555-123-4567 January 2020 40 hours/week"
    extracted = _make_extracted(text, page_count=3)
    report = analyze_resume(extracted)
    length_check = next(c for c in report.checks if "Length" in c.name)
    assert length_check.passed is False
    assert report.overall_pass is False


def test_ssn_fails():
    text = """
    Jane Doe
    jane@email.com
    555-123-4567
    January 2020 – Present
    40 hours/week
    SSN: 123-45-6789
    """
    extracted = _make_extracted(text)
    report = analyze_resume(extracted)
    ssn_check = next(c for c in report.checks if "Social Security" in c.name)
    assert ssn_check.passed is False
    assert report.overall_pass is False


def test_oversized_file_fails():
    text = "Jane Doe jane@email.com 555-123-4567 January 2020 40 hours/week"
    extracted = _make_extracted(text, size_mb=6.0)
    report = analyze_resume(extracted)
    size_check = next(c for c in report.checks if "File size" in c.name)
    assert size_check.passed is False
    assert report.overall_pass is False


def test_no_contact_fails():
    text = "January 2020 – Present 40 hours/week Program Analyst duties."
    extracted = _make_extracted(text)
    report = analyze_resume(extracted)
    email_check = next(c for c in report.checks if "Email" in c.name)
    phone_check = next(c for c in report.checks if "Phone" in c.name)
    assert email_check.passed is False
    assert phone_check.passed is False
    assert report.overall_pass is False


def test_docx_estimated_pages_noted():
    text = "Jane Doe jane@email.com 555-123-4567 January 2020 40 hours/week"
    extracted = _make_extracted(text, extension=".docx", page_count=2, page_reliable=False)
    report = analyze_resume(extracted)
    length_check = next(c for c in report.checks if "Length" in c.name)
    assert "estimated" in length_check.detail.lower()
