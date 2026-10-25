"""Allow running as python -m usajobs_checker"""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
