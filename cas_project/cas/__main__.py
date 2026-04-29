"""
cas/__main__.py
Allows the package to be invoked as: python -m cas [options]
"""
import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())
