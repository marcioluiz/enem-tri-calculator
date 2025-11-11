"""
TRI Calculator Module

Provides the main calculator for estimating ENEM scores based on TRI.
"""

from src.tri_calculator.calculator import TriCalculator
from src.tri_calculator.estimator import TriEstimator

__all__ = [
    "TriCalculator",
    "TriEstimator",
]
