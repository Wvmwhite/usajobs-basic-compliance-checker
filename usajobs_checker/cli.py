"""Command-line interface for the USAJOBS resume checker."""

import argparse
import sys
from pathlib import Path

from .analyzer import analyze_resume
from .extractor import ExtractionError, extract_resume
from .report import format_report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check a resume against basic USAJOBS requirements."
    )
    parser.add_argument(
        "resume",
        type=str,
        help="Path to resume file (.pdf or .docx)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON instead of text report (not yet implemented)",
    )
    args = parser.parse_args()

    path = Path(args.resume)
    try:
        extracted = extract_resume(path)
    except ExtractionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    report = analyze_resume(extracted)
    print(format_report(report))
    return 0 if report.overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
