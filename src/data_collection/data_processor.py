"""
Data Processor

Processes and normalizes ENEM data for use in calculations.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class DataProcessor:
    """
    Processes and normalizes ENEM data.
    
    Responsibilities:
    - Clean raw data
    - Calculate statistics
    - Create score mappings
    - Validate data quality
    """
    
    def __init__(self):
        """Initialize the data processor."""
        pass
    
    def process_raw_scores(
        self,
        correct_answers: List[int],
        scores: List[float]
    ) -> pd.DataFrame:
        """
        Process raw score data into a structured format.
        
        Args:
            correct_answers: List of number of correct answers
            scores: List of corresponding scores
            
        Returns:
            Processed DataFrame with statistics
        """
        if len(correct_answers) != len(scores):
            raise ValueError("Lists must have same length")
        
        df = pd.DataFrame({
            "correct_answers": correct_answers,
            "score": scores
        })
        
        # Sort by correct answers
        df = df.sort_values("correct_answers").reset_index(drop=True)
        
        # Calculate statistics
        df["score_mean"] = df.groupby("correct_answers")["score"].transform("mean")
        df["score_std"] = df.groupby("correct_answers")["score"].transform("std")
        df["score_min"] = df.groupby("correct_answers")["score"].transform("min")
        df["score_max"] = df.groupby("correct_answers")["score"].transform("max")
        
        # Fill NaN std with 0 (for single observations)
        df["score_std"] = df["score_std"].fillna(0)
        
        return df
    
    def calculate_percentiles(
        self,
        scores: List[float],
        percentiles: List[int] = [10, 25, 50, 75, 90]
    ) -> Dict[int, float]:
        """
        Calculate score percentiles.
        
        Args:
            scores: List of scores
            percentiles: List of percentile values to calculate
            
        Returns:
            Dictionary mapping percentile to score
        """
        return {
            p: float(np.percentile(scores, p))
            for p in percentiles
        }
    
    def create_score_mapping(
        self,
        df: pd.DataFrame,
        correct_col: str = "correct_answers",
        score_col: str = "score"
    ) -> Dict[int, float]:
        """
        Create a mapping from number of correct answers to average score.
        
        Args:
            df: DataFrame with score data
            correct_col: Column name for correct answers
            score_col: Column name for scores
            
        Returns:
            Dictionary mapping correct answers to average score
        """
        grouped = df.groupby(correct_col)[score_col].mean()
        return grouped.to_dict()
    
    def smooth_scores(
        self,
        score_mapping: Dict[int, float],
        window_size: int = 3
    ) -> Dict[int, float]:
        """
        Apply smoothing to score mapping using moving average.
        
        Args:
            score_mapping: Original score mapping
            window_size: Size of moving average window
            
        Returns:
            Smoothed score mapping
        """
        sorted_items = sorted(score_mapping.items())
        correct_answers = [item[0] for item in sorted_items]
        scores = [item[1] for item in sorted_items]
        
        # Apply moving average
        smoothed_scores = []
        for i in range(len(scores)):
            start = max(0, i - window_size // 2)
            end = min(len(scores), i + window_size // 2 + 1)
            avg_score = np.mean(scores[start:end])
            smoothed_scores.append(avg_score)
        
        return dict(zip(correct_answers, smoothed_scores))
    
    def validate_score_mapping(
        self,
        score_mapping: Dict[int, float],
        min_score: float = 0,
        max_score: float = 1000
    ) -> Tuple[bool, List[str]]:
        """
        Validate a score mapping for consistency.
        
        Args:
            score_mapping: Score mapping to validate
            min_score: Minimum allowed score
            max_score: Maximum allowed score
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check if empty
        if not score_mapping:
            errors.append("Score mapping is empty")
            return False, errors
        
        sorted_items = sorted(score_mapping.items())
        
        # Check score bounds
        for correct, score in sorted_items:
            if score < min_score or score > max_score:
                errors.append(
                    f"Score {score} for {correct} correct answers is out of bounds "
                    f"[{min_score}, {max_score}]"
                )
        
        # Check monotonicity (scores should generally increase)
        prev_score = None
        for correct, score in sorted_items:
            if prev_score is not None:
                if score < prev_score - 50:  # Allow some variation
                    errors.append(
                        f"Large decrease in score at {correct} correct answers: "
                        f"{prev_score:.1f} -> {score:.1f}"
                    )
            prev_score = score
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def interpolate_missing_values(
        self,
        score_mapping: Dict[int, float],
        total_questions: int = 45
    ) -> Dict[int, float]:
        """
        Interpolate missing values in score mapping.
        
        Args:
            score_mapping: Partial score mapping
            total_questions: Total number of questions
            
        Returns:
            Complete score mapping with interpolated values
        """
        from scipy.interpolate import interp1d
        
        if not score_mapping:
            raise ValueError("Cannot interpolate empty mapping")
        
        # Get existing data points
        sorted_items = sorted(score_mapping.items())
        x_vals = np.array([item[0] for item in sorted_items])
        y_vals = np.array([item[1] for item in sorted_items])
        
        # Create interpolator
        interpolator = interp1d(
            x_vals,
            y_vals,
            kind='linear',
            bounds_error=False,
            fill_value=(y_vals[0], y_vals[-1])
        )
        
        # Generate complete mapping
        all_correct = range(0, total_questions + 1)
        complete_mapping = {
            correct: float(interpolator(correct))
            for correct in all_correct
        }
        
        return complete_mapping
    
    def export_to_csv(
        self,
        score_mapping: Dict[int, float],
        output_path: Path,
        area_name: str = "unknown"
    ) -> None:
        """
        Export score mapping to CSV file.
        
        Args:
            score_mapping: Score mapping to export
            output_path: Path to output CSV file
            area_name: Name of the knowledge area
        """
        df = pd.DataFrame([
            {"area": area_name, "correct_answers": k, "score": v}
            for k, v in sorted(score_mapping.items())
        ])
        
        df.to_csv(output_path, index=False)
    
    def __repr__(self) -> str:
        """Return string representation of the processor."""
        return "DataProcessor()"
