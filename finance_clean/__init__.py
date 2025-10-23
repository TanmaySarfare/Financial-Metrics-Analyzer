"""
Finance Clean - Accurate Financial Metric Computation
A clean, modular approach to financial analysis using yfinance data.
"""

__version__ = "1.0.0"
__author__ = "Senior Python Engineer"

from .compute import compute_all
from .fetch import get_financials
from .validate import check_accounting_equation

__all__ = ["compute_all", "get_financials", "check_accounting_equation"]
