"""
conftest.py — pytest configuration for CAS test suite.
Adds the project root to sys.path so 'cas' is importable
without installation, on any OS including Windows.
"""
import sys
import os

# Ensure the package root (cas_project/) is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
