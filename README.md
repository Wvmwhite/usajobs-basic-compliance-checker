# USAJOBS Basic Compliance Checker

A simple Python tool that checks a resume (PDF or DOCX) against basic USAJOBS requirements and prints a clear pass/fail report.

It looks for the structural items that commonly cause a federal resume to be rejected before anyone reviews the content: file size, length, contact info, month/year dates, hours per week, education indicators, and no Social Security Number.

This is an advisory check only. It does not evaluate whether your experience matches a specific job announcement.

## Quick start (Windows)

1. Download or clone this repository.
2. Open PowerShell in the project folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Check a resume:

```powershell
python -m usajobs_checker "C:\Users\YourName\Documents\my_resume.pdf"
```

You will see a report that ends with **OVERALL: PASS** or **OVERALL: FAIL** plus details on each check.

## Quick start (macOS / Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m usajobs_checker /path/to/your_resume.pdf
```

## Use case examples

**Check a PDF resume**
```powershell
python -m usajobs_checker "C:\Users\Jane\Downloads\Jane_Doe_Resume.pdf"
```

**Check a Word resume**
```powershell
python -m usajobs_checker "C:\Users\Jane\Documents\Jane_Doe_Resume.docx"
```

**Check a resume that has spaces or parentheses in the filename**
```powershell
python -m usajobs_checker "C:\Users\Jane\Downloads\Joseph_Becker_Resume_IRS (1).pdf"
```

**See the report and the exit code**
```powershell
python -m usajobs_checker resume.pdf
echo "Exit code: $LASTEXITCODE"
```
- `0` = overall pass  
- `1` = one or more required checks failed  
- `2` = file could not be read

## What it checks

- File size ≤ 5 MB
- Supported format (PDF preferred, DOCX accepted)
- Length ≤ 2 pages (accurate for PDF; estimated for DOCX)
- Email address present
- Phone number present
- Work experience structure (month/year dates + hours-per-week indicator)
- Education-related keywords
- No Social Security Number
- Text could be extracted successfully

## Running the tests

```powershell
pytest tests/ -v
```

## Limitations

- Page count is accurate for PDF. For DOCX it is only an estimate — convert to PDF for a reliable length check.
- Detection uses simple patterns, not full AI analysis. Unusual formatting may be missed.
- Does not check job-specific specialized experience or questionnaire answers.
- Always review the current job announcement and [USAJOBS Help Center](https://help.usajobs.gov) before submitting.

## Project layout

```
usajobs_checker/     # the package
  extractor.py       # read PDF/DOCX
  analyzer.py        # the compliance checks
  report.py          # format the report
  cli.py             # command-line interface
tests/               # unit tests
requirements.txt
README.md
```
