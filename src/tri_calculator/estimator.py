"""
TRI Estimator

Implements the core algorithm for estimating TRI scores based on 
the number of correct answers.
"""

import numpy as np
from scipy.interpolate import interp1d
from scipy import stats
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class TriEstimator:
    """
    Estimates TRI scores based on historical data and statistical models.
    
    The TRI (Item Response Theory) uses a complex model that considers:
    - Item difficulty
    - Item discrimination
    - Guessing parameter
    
    Since exact item parameters are not publicly available, this estimator
    uses historical data and statistical approximations.
    """
    
    def __init__(
        self,
        total_questions: int = 45,
        min_score: float = 300.0,
        max_score: float = 900.0,
        mean_score: float = 500.0,
        std_deviation: float = 100.0,
        area_name: Optional[str] = None,
        data_dir: Optional[Path] = None
    ):
        """
        Initialize the TRI estimator.
        
        Args:
            total_questions: Total number of questions in the area
            min_score: Minimum possible score
            max_score: Maximum possible score
            mean_score: Expected mean score for average performance
            std_deviation: Standard deviation for score distribution
            area_name: Name of the knowledge area (for microdata lookup)
            data_dir: Directory containing microdata statistics
        """
        self.total_questions = total_questions
        self.min_score = min_score
        self.max_score = max_score
        self.mean_score = mean_score
        self.std_deviation = std_deviation
        self.area_name = area_name
        self.data_dir = data_dir
        
        # Create default score mapping
        self._score_map: Optional[Dict[int, float]] = None
        self._interpolator: Optional[interp1d] = None
    
    def set_historical_data(
        self,
        correct_answers: List[int],
        scores: List[float],
        years: Optional[List[int]] = None,
        inep_stats_by_year: Optional[Dict[int, Dict[str, float]]] = None
    ) -> None:
        """
        Set historical data for more accurate estimations.
        
        Args:
            correct_answers: List of number of correct answers
            scores: List of corresponding actual scores
            years: List of years corresponding to each data point
            inep_stats_by_year: INEP statistics (mean, std) for each year (not used)
        """
        if len(correct_answers) != len(scores):
            raise ValueError("correct_answers and scores must have same length")
        
        if len(correct_answers) < 2:
            return
        
        # Store for range calculations
        self._historical_correct_answers = correct_answers
        self._historical_scores = scores
        self._historical_years = years
        
        # Calculate conversion factors (score/CA ratio) for each data point
        factors = []
        for ca, score in zip(correct_answers, scores):
            if ca > 0:
                factor = score / ca
                factors.append(factor)
        
        if len(factors) > 0:
            # Use median factor for robustness against outliers
            self._conversion_factor = float(np.median(factors))
            
            # Store exact matches for reference
            from collections import defaultdict
            grouped = defaultdict(list)
            for ca, sc in zip(correct_answers, scores):
                grouped[ca].append(sc)
            
            x_data = np.array(sorted(grouped.keys()))
            y_data = np.array([np.mean(grouped[ca]) for ca in x_data])
            self._score_map = dict(zip(x_data, y_data))
            
            # Create a simple linear interpolator based on conversion factor
            def factor_interpolator(ca):
                return self._conversion_factor * ca
            
            self._interpolator = factor_interpolator
        else:
            self._conversion_factor = None
            self._score_map = None
            self._interpolator = None
    

    def estimate_score_range(
        self,
        correct_answers: int,
        current_year: Optional[int] = None
    ) -> Optional[Tuple[float, float, float]]:
        """
        Estimate score range and calculated score based on user's historical data.
        
        Args:
            correct_answers: Number of correct answers (0 to total_questions)
            current_year: Current year for projection (not used, kept for compatibility)
            
        Returns:
            Tuple of (pessimistic_score, calculated_score, optimistic_score) or None
        """
        # Need historical data and interpolator
        if not hasattr(self, '_interpolator') or self._interpolator is None:
            return None
        
        if not hasattr(self, '_historical_correct_answers') or len(self._historical_correct_answers) < 2:
            return None
        
        # Get base prediction from interpolation
        base_score = float(self._interpolator(correct_answers))
        
        # Calculate prediction errors from historical data
        errors = []
        for i, hist_ca in enumerate(self._historical_correct_answers):
            hist_score = self._historical_scores[i]
            predicted_hist = float(self._interpolator(hist_ca))
            error = hist_score - predicted_hist
            errors.append(error)
        
        # Pessimistic: average of (min_error, median_error)
        # Optimistic: 90% of max_error
        min_error = min(errors)
        max_error = max(errors)
        median_error = np.median(errors)
        
        pessimistic_error = (min_error + median_error) / 2
        optimistic_error = 0.9 * max_error
        
        pessimistic = base_score + pessimistic_error
        optimistic = base_score + optimistic_error
        
        # Clip to valid range
        pessimistic = float(np.clip(pessimistic, 300, 1000))
        optimistic = float(np.clip(optimistic, 300, 1000))
        
        # Ensure optimistic >= pessimistic
        if pessimistic > optimistic:
            pessimistic, optimistic = optimistic, pessimistic
        
        # Calculate growth factor from historical performance
        growth_factor = self._calculate_growth_factor()
        
        # Calculated score: average of range × growth factor
        base_calculated = (pessimistic + optimistic) / 2
        calculated = base_calculated * growth_factor
        
        # Ensure calculated is always between pessimistic and optimistic
        calculated = float(np.clip(calculated, pessimistic, optimistic))
        
        return (pessimistic, calculated, optimistic)
    
    def _calculate_growth_factor(self) -> float:
        """
        Calculate growth factor based on user's historical score progression.
        
        Returns:
            Growth factor (1.0 = no growth, >1.0 = improvement, <1.0 = decline)
        """
        if not hasattr(self, '_historical_scores') or len(self._historical_scores) < 2:
            return 1.0
        
        scores = np.array(self._historical_scores)
        
        # Calculate year-over-year growth rates
        growth_rates = []
        for i in range(1, len(scores)):
            if scores[i-1] > 0:
                rate = scores[i] / scores[i-1]
                growth_rates.append(rate)
        
        if not growth_rates:
            return 1.0
        
        # Use weighted average (more recent years weighted higher)
        weights = np.array([2 ** i for i in range(len(growth_rates))])
        weighted_avg_growth = np.average(growth_rates, weights=weights)
        
        # Limit to reasonable range (0.9 to 1.15)
        # Prevents extreme projections
        return float(np.clip(weighted_avg_growth, 0.9, 1.15))
    
    def estimate_score(
        self,
        correct_answers: int,
        use_logistic: bool = True,
        current_year: Optional[int] = None
    ) -> float:
        """
        Estimate the TRI score based on number of correct answers.
        
        Args:
            correct_answers: Number of correct answers (0 to total_questions)
            use_logistic: Whether to use logistic curve for estimation
            current_year: Current year for z-score projection
            
        Returns:
            Estimated TRI score (typically 0-1000)
        """
        # Validate input
        if correct_answers < 0 or correct_answers > self.total_questions:
            raise ValueError(
                f"Correct answers must be between 0 and {self.total_questions}"
            )
        
        # Priority 1: Use exact historical data if available
        if self._score_map is not None and correct_answers in self._score_map:
            return self._score_map[correct_answers]
        
        # Priority 2: Use interpolation if available
        if self._interpolator is not None:
            return float(self._interpolator(correct_answers))
        
        # Priority 3: Fallback to logistic model
        if use_logistic:
            return self._estimate_with_logistic(correct_answers)
        else:
            return self._estimate_with_linear(correct_answers)
    

    def _estimate_with_logistic(self, correct_answers: int) -> float:
        """
        Estimate score using a logistic curve model.
        
        The logistic curve better represents the TRI behavior where:
        - Very few correct answers -> Low score (but not 0)
        - Around 50% correct -> Mean score
        - Very high correct answers -> High score (but with diminishing returns)
        
        Args:
            correct_answers: Number of correct answers
            
        Returns:
            Estimated score
        """
        # Calculate proportion of correct answers
        proportion = correct_answers / self.total_questions
        
        # Transform to standard normal scale
        # Center at 50% correct answers (proportion = 0.5)
        z_score = (proportion - 0.5) / 0.15  # 0.15 controls the steepness
        
        # Apply logistic transformation
        # This maps the proportion to a score between min_score and max_score
        score_range = self.max_score - self.min_score
        normalized_score = 1 / (1 + np.exp(-z_score))
        
        # Scale to actual score range
        score = self.min_score + (score_range * normalized_score)
        
        # Apply additional adjustments based on extreme values
        if correct_answers == 0:
            score = max(score, self.min_score)
        elif correct_answers == self.total_questions:
            score = min(score, self.max_score)
        
        return float(score)
    
    def _estimate_with_linear(self, correct_answers: int) -> float:
        """
        Estimate score using a simple linear model with adjustments.
        
        Args:
            correct_answers: Number of correct answers
            
        Returns:
            Estimated score
        """
        # Calculate base proportion
        proportion = correct_answers / self.total_questions
        
        # Linear interpolation between min and max scores
        score_range = self.max_score - self.min_score
        score = self.min_score + (proportion * score_range)
        
        return float(score)
    
    def estimate_proficiency(self, correct_answers: int) -> float:
        """
        Estimate the proficiency level (theta) in TRI terminology.
        
        In TRI, proficiency (theta) is typically on a scale centered at 0
        with standard deviation of 1. We map this to our score scale.
        
        Args:
            correct_answers: Number of correct answers
            
        Returns:
            Estimated proficiency level (theta)
        """
        proportion = correct_answers / self.total_questions
        
        # Transform proportion to z-score (assuming normal distribution)
        # Handle edge cases
        if proportion <= 0.01:
            z_score = -3.0
        elif proportion >= 0.99:
            z_score = 3.0
        else:
            z_score = stats.norm.ppf(proportion)
        
        return float(z_score)
    
    def get_confidence_interval(
        self,
        correct_answers: int,
        confidence: float = 0.95
    ) -> Tuple[float, float]:
        """
        Calculate confidence interval for the estimated score.
        
        Args:
            correct_answers: Number of correct answers
            confidence: Confidence level (default 0.95 for 95% CI)
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        score = self.estimate_score(correct_answers)
        
        # Calculate margin of error based on standard error
        # Standard error depends on the number of items
        standard_error = self.std_deviation / np.sqrt(self.total_questions)
        
        # Z-score for confidence level
        z_score = stats.norm.ppf((1 + confidence) / 2)
        
        margin_of_error = z_score * standard_error
        
        lower_bound = max(self.min_score, score - margin_of_error)
        upper_bound = min(self.max_score, score + margin_of_error)
        
        return (float(lower_bound), float(upper_bound))
    

    
    def __repr__(self) -> str:
        """Return string representation of the estimator."""
        return (
            f"TriEstimator(questions={self.total_questions}, "
            f"score_range=[{self.min_score}, {self.max_score}])"
        )
