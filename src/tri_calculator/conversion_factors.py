"""
Conversion Factors Calculator

Calculates and adjusts conversion factors from correct answers to TRI scores
using historical INEP data and user's personal history.
"""

from typing import Dict, List, Optional, Tuple
from pathlib import Path
import numpy as np
from dataclasses import dataclass


@dataclass
class YearFactor:
    """Conversion factor for a specific year and area."""
    year: int
    area: str
    
    # Global factors (from INEP data)
    global_min_factor: float  # min_score / min_correct_answers
    global_max_factor: float  # max_score / max_correct_answers
    global_mean_factor: float  # mean_score / mean_correct_answers
    
    # Adjusted factors (after user calibration)
    adjusted_factor: Optional[float] = None
    
    # Confidence in this factor (based on data quality)
    confidence: float = 1.0


class ConversionFactorsCalculator:
    """
    Calculates conversion factors from correct answers to TRI scores.
    
    Process:
    1. Extract global factors from INEP data (score stats + microdata stats)
    2. Calculate user-specific factors from historical data
    3. Blend global and user factors to get personalized conversion
    4. Project factor for current year based on historical trend
    """
    
    def __init__(self, data_dir: Path):
        """
        Initialize the conversion factors calculator.
        
        Args:
            data_dir: Directory containing INEP and microdata statistics
        """
        self.data_dir = data_dir
        self.global_factors: Dict[str, Dict[int, YearFactor]] = {}
        self.user_factors: Dict[str, Dict[int, float]] = {}
        
    def calculate_global_factors(self, area: str, years: List[int]) -> Dict[int, YearFactor]:
        """
        Calculate global conversion factors from INEP data.
        
        Combines TRI score statistics with microdata (correct answers) statistics
        to derive conversion factors.
        
        Args:
            area: Knowledge area name (mathematics, languages, etc.)
            years: List of years to calculate factors for
            
        Returns:
            Dictionary mapping year to YearFactor
        """
        from src.data_collection.historical_data import HistoricalDataCollector
        from src.data_collection.microdata_processor import MicrodataProcessor
        
        score_collector = HistoricalDataCollector(self.data_dir)
        microdata_processor = MicrodataProcessor(self.data_dir)
        
        factors = {}
        
        for year in years:
            # Load TRI score statistics
            score_stats = score_collector.load_inep_statistics(year)
            if not score_stats or area not in score_stats:
                continue
            
            # Load microdata (correct answers) statistics
            ca_stats = microdata_processor.load_correct_answers_stats(year)
            if not ca_stats or area not in ca_stats:
                continue
            
            scores = score_stats[area]
            correct_answers = ca_stats[area]
            
            # Calculate factors: score / correct_answers
            # We use mean as primary factor
            mean_factor = scores['mean'] / correct_answers['mean'] if correct_answers['mean'] > 0 else 0
            
            # Calculate factors for min and max (less reliable but useful)
            # Min: assuming min correct answers is around 0-5
            min_ca = max(correct_answers['percentiles'].get('25', 5), 5)
            min_factor = scores['min'] / min_ca if min_ca > 0 else 0
            
            # Max: using 90th percentile of correct answers
            max_ca = correct_answers['percentiles'].get('90', correct_answers['max'])
            max_factor = scores['max'] / max_ca if max_ca > 0 else 0
            
            # Create YearFactor
            factors[year] = YearFactor(
                year=year,
                area=area,
                global_min_factor=min_factor,
                global_max_factor=max_factor,
                global_mean_factor=mean_factor,
                confidence=1.0
            )
        
        return factors
    
    def calculate_user_factors(
        self,
        area: str,
        correct_answers_list: List[int],
        scores_list: List[float],
        years_list: List[int]
    ) -> Dict[int, float]:
        """
        Calculate user-specific conversion factors from historical data.
        
        Args:
            area: Knowledge area name
            correct_answers_list: User's correct answers per year
            scores_list: User's official scores per year
            years_list: Corresponding years
            
        Returns:
            Dictionary mapping year to user's conversion factor
        """
        if len(correct_answers_list) != len(scores_list) or len(scores_list) != len(years_list):
            return {}
        
        user_factors = {}
        
        for ca, score, year in zip(correct_answers_list, scores_list, years_list):
            if ca > 0:  # Only calculate if we have correct answers
                factor = score / ca
                user_factors[year] = factor
        
        return user_factors
    
    def blend_factors(
        self,
        area: str,
        year: int,
        user_weight: float = 0.7
    ) -> Optional[float]:
        """
        Blend global and user factors to get personalized conversion factor.
        
        Args:
            area: Knowledge area name
            year: Target year
            user_weight: Weight for user factors (0-1), default 0.7
            
        Returns:
            Blended conversion factor, or None if no data available
        """
        # Get global factor for this year
        global_factor = None
        if area in self.global_factors and year in self.global_factors[area]:
            global_factor = self.global_factors[area][year].global_mean_factor
        
        # Get user factor for this year (if exists)
        user_factor = None
        if area in self.user_factors and year in self.user_factors[area]:
            user_factor = self.user_factors[area][year]
        
        # If we have both, blend them
        if user_factor is not None and global_factor is not None:
            return user_weight * user_factor + (1 - user_weight) * global_factor
        
        # If only user factor, use it
        if user_factor is not None:
            return user_factor
        
        # If only global factor, use it
        if global_factor is not None:
            return global_factor
        
        return None
    
    def adjust_factors_with_user_data(
        self,
        area: str,
        correct_answers_list: List[int],
        scores_list: List[float],
        years_list: List[int]
    ) -> None:
        """
        Adjust global factors based on user's historical data.
        
        This calculates the delta between global and user factors,
        then adjusts all factors accordingly.
        
        Args:
            area: Knowledge area name
            correct_answers_list: User's correct answers per year
            scores_list: User's official scores per year
            years_list: Corresponding years
        """
        # Calculate user factors
        user_factors = self.calculate_user_factors(
            area, correct_answers_list, scores_list, years_list
        )
        
        if not user_factors:
            return
        
        # Store user factors
        if area not in self.user_factors:
            self.user_factors[area] = {}
        self.user_factors[area].update(user_factors)
        
        # Calculate adjustment ratio (user vs global)
        if area not in self.global_factors:
            return
        
        adjustments = []
        for year, user_factor in user_factors.items():
            if year in self.global_factors[area]:
                global_factor = self.global_factors[area][year].global_mean_factor
                if global_factor > 0:
                    adjustment = user_factor / global_factor
                    adjustments.append(adjustment)
        
        if not adjustments:
            return
        
        # Calculate average adjustment
        avg_adjustment = np.mean(adjustments)
        
        # Apply adjustment to all factors in this area
        for year_factor in self.global_factors[area].values():
            year_factor.adjusted_factor = year_factor.global_mean_factor * avg_adjustment
    
    def project_factor_range_for_year(
        self,
        area: str,
        target_year: int,
        use_user_data: bool = True
    ) -> Optional[Tuple[float, float]]:
        """
        Project a range of conversion factors (min, max) for a target year.
        
        Returns:
            Tuple of (min_factor, max_factor) or None
        """
        if use_user_data and area in self.user_factors and len(self.user_factors[area]) > 0:
            user_factor_values = list(self.user_factors[area].values())
            
            # Min: lowest historical factor
            min_factor = min(user_factor_values)
            
            # Max: highest historical factor
            max_factor = max(user_factor_values)
            
            return (float(min_factor), float(max_factor))
        
        return None
    
    def project_factor_for_year(
        self,
        area: str,
        target_year: int,
        use_user_data: bool = True
    ) -> Optional[float]:
        """
        Project conversion factor for a target year.
        
        Uses user's historical performance as baseline, but adjusts for year-over-year
        difficulty changes observed in global INEP data.
        
        Strategy:
        - User's average factor = their personal "points per correct answer"
        - Global factor changes year-to-year reflect exam difficulty variations
        - Apply the difficulty adjustment to user's baseline
        
        Args:
            area: Knowledge area name
            target_year: Year to project factor for
            use_user_data: Whether to use user's historical data
            
        Returns:
            Projected conversion factor
        """
        # Priority 1: If we have user factors, use them as baseline
        if use_user_data and area in self.user_factors and len(self.user_factors[area]) > 0:
            user_years = sorted(self.user_factors[area].keys())
            user_factor_values = [self.user_factors[area][y] for y in user_years]
            
            # Calculate user's average factor (their baseline performance level)
            # Use 2-year average for more recent trend, or all data if less than 2 years
            if len(user_factor_values) >= 2:
                user_avg_factor = np.mean(user_factor_values[-2:])  # Last 2 years
            else:
                user_avg_factor = np.mean(user_factor_values)  # Use what we have
            
            # Get the most recent year we have user data for
            last_user_year = user_years[-1]
            last_user_factor = user_factor_values[-1]
            
            # Check if we have global factors to estimate difficulty adjustment
            if area in self.global_factors:
                # Get global factors for last user year and target year
                global_last = None
                global_target = None
                
                if last_user_year in self.global_factors[area]:
                    global_last = self.global_factors[area][last_user_year].global_mean_factor
                
                if target_year in self.global_factors[area]:
                    global_target = self.global_factors[area][target_year].global_mean_factor
                
                # If we have both global factors, calculate difficulty adjustment
                if global_last and global_target and global_last > 0:
                    # Difficulty ratio: how much harder/easier is target year vs last user year?
                    difficulty_adjustment = global_target / global_last
                    
                    # First, calculate linear trend from user's historical data
                    if len(user_years) >= 2:
                        coefficients = np.polyfit(user_years, user_factor_values, 1)
                        trend_projected = coefficients[0] * target_year + coefficients[1]
                    else:
                        trend_projected = last_user_factor
                    
                    # Apply difficulty adjustment to the trend
                    projected = trend_projected * difficulty_adjustment
                    
                    # Only apply sensible bounds: don't go below 10 or above 50
                    projected = np.clip(projected, 10.0, 50.0)
                    
                    return float(projected)
            
            # Fallback: if no global data, learn from user's prediction errors
            if len(user_years) >= 3:
                # Calculate what linear trend would have predicted for each past year
                # Then see if user consistently over/under-performs the trend
                prediction_errors = []
                
                for i in range(2, len(user_years)):
                    # Use data up to year i-1 to predict year i
                    train_years = user_years[:i]
                    train_values = user_factor_values[:i]
                    actual_value = user_factor_values[i]
                    
                    # Fit trend on training data
                    if len(train_years) >= 2:
                        coef = np.polyfit(train_years, train_values, 1)
                        predicted = coef[0] * user_years[i] + coef[1]
                        error = actual_value - predicted
                        prediction_errors.append(error)
                
                # Detect and remove outliers using median absolute deviation
                if len(prediction_errors) >= 3:
                    median_error = np.median(prediction_errors)
                    mad = np.median(np.abs(np.array(prediction_errors) - median_error))
                    # Remove errors that are >2 MAD from median (likely outliers)
                    filtered_errors = [e for e in prediction_errors if abs(e - median_error) <= 2 * mad]
                    if len(filtered_errors) > 0:
                        prediction_errors = filtered_errors
                
                # Average prediction error (with more weight on recent errors)
                if len(prediction_errors) > 0:
                    error_weights = 2 ** np.arange(len(prediction_errors))
                    avg_error = np.average(prediction_errors, weights=error_weights)
                else:
                    avg_error = 0
                
                # Now make final prediction
                coefficients = np.polyfit(user_years, user_factor_values, 1)
                slope = coefficients[0]
                intercept = coefficients[1]
                trend_projected = slope * target_year + intercept
                
                # Apply 50% of the learned correction bias (be conservative)
                projected = trend_projected + (0.5 * avg_error)
                
                print(f"[ADAPTIVE {area}] years={user_years}, factors={[f'{x:.2f}' for x in user_factor_values]}, "
                      f"trend={trend_projected:.2f}, avg_error={avg_error:+.2f}, corrected={projected:.2f}")
                
                # Only apply sensible bounds: don't go below 10 or above 50
                projected = np.clip(projected, 10.0, 50.0)
                return float(projected)
            
            elif len(user_years) == 2:
                # Not enough data for error analysis, use simple average
                avg_factor = np.mean(user_factor_values)
                return float(avg_factor)
            
            # Only one data point: use it directly
            return user_avg_factor
        
        # Priority 2: Fall back to global factors if no user data
        if area not in self.global_factors:
            return None
        
        # Get factors from recent years
        years = sorted([y for y in self.global_factors[area].keys() if y <= target_year])
        if not years:
            return None
        
        # Use last 3-5 years for trend
        recent_years = years[-5:]
        recent_factors = []
        
        for year in recent_years:
            yf = self.global_factors[area][year]
            # Use adjusted factor if available, otherwise global
            factor = yf.adjusted_factor if yf.adjusted_factor is not None else yf.global_mean_factor
            recent_factors.append(factor)
        
        if not recent_factors:
            return None
        
        # If target year is beyond our data, extrapolate
        if target_year > years[-1]:
            # Simple linear extrapolation
            if len(recent_factors) >= 2:
                years_array = np.array(recent_years)
                factors_array = np.array(recent_factors)
                
                # Linear regression
                coefficients = np.polyfit(years_array, factors_array, 1)
                projected = coefficients[0] * target_year + coefficients[1]
                
                # Limit extrapolation (don't go too far from last known value)
                last_factor = recent_factors[-1]
                max_change = 0.1 * last_factor  # Max 10% change per year
                years_diff = target_year - years[-1]
                
                projected = np.clip(
                    projected,
                    last_factor - max_change * years_diff,
                    last_factor + max_change * years_diff
                )
                
                return float(projected)
            else:
                # Not enough data, use last known factor
                return recent_factors[-1]
        
        # Target year is within our data range, use interpolation
        return np.interp(target_year, recent_years, recent_factors)
    
    def estimate_score_from_correct_answers(
        self,
        area: str,
        correct_answers: int,
        year: int,
        return_range: bool = False
    ) -> Optional[float]:
        """
        Estimate TRI score from number of correct answers using conversion factors.
        
        Args:
            area: Knowledge area name
            correct_answers: Number of correct answers (0-45)
            year: Target year
            return_range: If True, returns (pessimistic, optimistic) tuple
            
        Returns:
            Estimated TRI score, or (pessimistic_score, optimistic_score) if return_range=True
        """
        if return_range:
            factor_range = self.project_factor_range_for_year(area, year, use_user_data=True)
            if factor_range is None:
                return None
            
            min_factor, max_factor = factor_range
            
            # Pessimistic: average of min and median
            median_factor = (min_factor + max_factor) / 2
            pessimistic_factor = (min_factor + median_factor) / 2
            
            # Optimistic: 90% of max
            optimistic_factor = 0.9 * max_factor
            
            pessimistic_score = np.clip(pessimistic_factor * correct_answers, 300, 1000)
            optimistic_score = np.clip(optimistic_factor * correct_answers, 300, 1000)
            
            return (float(pessimistic_score), float(optimistic_score))
        else:
            factor = self.project_factor_for_year(area, year, use_user_data=True)
            
            if factor is None:
                return None
            
            # Basic estimation: score = factor * correct_answers
            estimated_score = factor * correct_answers
            
            # Apply bounds (TRI scores are typically 300-1000)
            estimated_score = np.clip(estimated_score, 300, 1000)
            
            return float(estimated_score)
    
    def get_factor_evolution(self, area: str) -> List[Tuple[int, float, float]]:
        """
        Get evolution of factors over time.
        
        Args:
            area: Knowledge area name
            
        Returns:
            List of tuples (year, global_factor, adjusted_factor)
        """
        if area not in self.global_factors:
            return []
        
        evolution = []
        for year in sorted(self.global_factors[area].keys()):
            yf = self.global_factors[area][year]
            evolution.append((
                year,
                yf.global_mean_factor,
                yf.adjusted_factor if yf.adjusted_factor is not None else yf.global_mean_factor
            ))
        
        return evolution
    
    def initialize_area(self, area: str, years: Optional[List[int]] = None) -> None:
        """
        Initialize conversion factors for an area.
        
        Args:
            area: Knowledge area name
            years: List of years to initialize (default: 2004-2024)
        """
        if years is None:
            years = list(range(2004, 2025))
        
        self.global_factors[area] = self.calculate_global_factors(area, years)
