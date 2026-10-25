"""
USAJOBS Resume Checker

Extracts text and metadata from PDF or DOCX resumes and checks compliance
against basic USAJOBS / OPM federal resume requirements.

Requirements checked (derived from official USAJOBS Help Center and OPM guidance):
- File size ≤ 5 MB
- Supported format (PDF preferred, DOCX accepted)
- Length ≤ 2 pages
- Contact information: email and phone present
- Work experience structure: month/year dates and hours-per-week indicators
- Education section indicators
- No Social Security Number
- Plain, non-encrypted document (enforced by successful extraction)

This is an advisory tool. It does not guarantee acceptance. Always verify
against the current job announcement and USAJOBS requirements.
"""

__version__ = "0.1.0"
