"""
ENEM TRI Calculator Package

This package provides tools to estimate ENEM exam scores based on the 
Item Response Theory (TRI) methodology.
"""

__version__ = "0.1.0"
__author__ = "ENEM TRI Calculator Team"

from src.models.exam_area import ExamArea
from src.models.exam_result import ExamResult
from src.tri_calculator.calculator import TriCalculator
from src.cli.cli import cli

__all__ = [
    "ExamArea",
    "ExamResult",
    "TriCalculator",
    "cli",
]
