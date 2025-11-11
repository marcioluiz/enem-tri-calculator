"""
TRI Calculator

Main calculator class that coordinates score estimation for all ENEM areas.
"""

from typing import Dict, Optional, List
from pathlib import Path

from src.models.exam_area import ExamArea, AreaType
from src.models.exam_result import ExamResult
from src.tri_calculator.estimator import TriEstimator


class TriCalculator:
    """
    Main calculator for estimating ENEM scores using TRI methodology.
    
    This class coordinates the estimation of scores across all ENEM areas:
    - Mathematics and its Technologies
    - Languages, Codes and its Technologies
    - Natural Sciences and its Technologies
    - Human Sciences and its Technologies
    - Essay (uses direct score, not estimated)
    """
    
    @staticmethod
    def _calculate_default_params_from_inep() -> Dict[AreaType, Dict]:
        """
        Calculate default parameters from INEP historical data.
        Uses average of the last 5 years of available data.
        
        Returns:
            Dictionary of parameters per area
        """
        from src.data_collection.historical_data import HistoricalDataCollector
        
        collector = HistoricalDataCollector(Path(__file__).parent.parent.parent / "data")
        
        # Use last 5 years to calculate averages (2020-2024)
        years_to_average = range(2020, 2025)
        area_mapping = {
            'mathematics': AreaType.MATHEMATICS,
            'languages': AreaType.LANGUAGES,
            'natural_sciences': AreaType.NATURAL_SCIENCES,
            'human_sciences': AreaType.HUMAN_SCIENCES,
        }
        
        params = {}
        for area_name, area_type in area_mapping.items():
            stats_sum = {'min': 0, 'max': 0, 'mean': 0, 'std': 0}
            count = 0
            
            for year in years_to_average:
                year_stats = collector.load_inep_statistics(year)
                if year_stats and area_name in year_stats:
                    area_stats = year_stats[area_name]
                    stats_sum['min'] += area_stats['min']
                    stats_sum['max'] += area_stats['max']
                    stats_sum['mean'] += area_stats['mean']
                    stats_sum['std'] += area_stats['std']
                    count += 1
            
            if count > 0:
                params[area_type] = {
                    "min_score": stats_sum['min'] / count,
                    "max_score": stats_sum['max'] / count,
                    "mean_score": stats_sum['mean'] / count,
                    "std_deviation": stats_sum['std'] / count
                }
            else:
                # Fallback only if no data available at all
                params[area_type] = {
                    "min_score": 300.0,
                    "max_score": 900.0,
                    "mean_score": 500.0,
                    "std_deviation": 100.0
                }
        
        return params
    
    def __init__(
        self,
        total_questions_per_area: int = 45,
        custom_parameters: Optional[Dict[AreaType, Dict]] = None,
        use_inep_data: bool = True,
        reference_year: int = 2023
    ):
        """
        Initialize the TRI calculator.
        
        Args:
            total_questions_per_area: Number of questions per knowledge area
            custom_parameters: Custom parameters for each area (optional)
            use_inep_data: Whether to use INEP historical statistics
            reference_year: Year to use as reference for INEP data
        """
        self.total_questions = total_questions_per_area
        self.estimators: Dict[AreaType, TriEstimator] = {}
        self.use_inep_data = use_inep_data
        self.reference_year = reference_year
        
        # Load INEP statistics if requested and no custom parameters
        if use_inep_data and custom_parameters is None:
            params = self._load_inep_parameters(reference_year)
        elif custom_parameters is not None:
            params = custom_parameters
        else:
            # Calculate from real INEP data instead of using hardcoded values
            params = self._calculate_default_params_from_inep()
        
        # Map area types to microdata names
        area_name_mapping = {
            AreaType.MATHEMATICS: 'mathematics',
            AreaType.LANGUAGES: 'languages',
            AreaType.NATURAL_SCIENCES: 'natural_sciences',
            AreaType.HUMAN_SCIENCES: 'human_sciences',
        }
        
        data_path = Path(__file__).parent.parent.parent / "data"
        
        for area_type in [
            AreaType.MATHEMATICS,
            AreaType.LANGUAGES,
            AreaType.NATURAL_SCIENCES,
            AreaType.HUMAN_SCIENCES
        ]:
            area_params = params.get(area_type, {})
            self.estimators[area_type] = TriEstimator(
                total_questions=self.total_questions,
                min_score=area_params.get("min_score", 300.0),
                max_score=area_params.get("max_score", 900.0),
                mean_score=area_params.get("mean_score", 500.0),
                std_deviation=area_params.get("std_deviation", 100.0),
                area_name=area_name_mapping.get(area_type),
                data_dir=data_path
            )
    
    def _load_inep_parameters(self, year: int) -> Dict[AreaType, Dict]:
        """
        Load parameters from INEP historical data.
        
        Args:
            year: Reference year for statistics
            
        Returns:
            Dictionary of parameters per area
        """
        from src.data_collection.historical_data import HistoricalDataCollector
        
        collector = HistoricalDataCollector(Path(__file__).parent.parent.parent / "data")
        
        # Ensure statistics are downloaded/saved for all years (2009-2024 with TRI)
        for hist_year in range(2009, 2025):
            if not collector.download_inep_data(hist_year):
                # If download failed, at least try to generate from internal data
                pass
        
        stats = collector.load_inep_statistics(year)
        
        if not stats:
            # Fall back to calculated averages
            return self._calculate_default_params_from_inep()
        
        # Map statistics to parameters
        params = {}
        area_mapping = {
            'mathematics': AreaType.MATHEMATICS,
            'languages': AreaType.LANGUAGES,
            'natural_sciences': AreaType.NATURAL_SCIENCES,
            'human_sciences': AreaType.HUMAN_SCIENCES,
        }
        
        for area_name, area_type in area_mapping.items():
            if area_name in stats:
                area_stats = stats[area_name]
                params[area_type] = {
                    "min_score": area_stats['min'],
                    "max_score": area_stats['max'],
                    "mean_score": area_stats['mean'],
                    "std_deviation": area_stats['std']
                }
            else:
                # Use calculated averages if specific year not available
                default_params = self._calculate_default_params_from_inep()
                params[area_type] = default_params[area_type]
        
        return params
    
    def calculate_score(
        self,
        mathematics: int,
        languages: int,
        natural_sciences: int,
        human_sciences: int,
        essay_score: float
    ) -> ExamResult:
        """
        Calculate estimated scores for all ENEM areas.
        
        Args:
            mathematics: Number of correct answers in Mathematics (0-45)
            languages: Number of correct answers in Languages (0-45)
            natural_sciences: Number of correct answers in Natural Sciences (0-45)
            human_sciences: Number of correct answers in Human Sciences (0-45)
            essay_score: Essay score (0-1000)
            
        Returns:
            ExamResult object with estimated scores for all areas
        """
        # Validate essay score
        if essay_score < 0 or essay_score > 1000:
            raise ValueError("Essay score must be between 0 and 1000")
        
        # Create exam areas
        areas = {
            AreaType.MATHEMATICS: ExamArea(
                area_type=AreaType.MATHEMATICS,
                total_questions=self.total_questions,
                correct_answers=mathematics
            ),
            AreaType.LANGUAGES: ExamArea(
                area_type=AreaType.LANGUAGES,
                total_questions=self.total_questions,
                correct_answers=languages
            ),
            AreaType.NATURAL_SCIENCES: ExamArea(
                area_type=AreaType.NATURAL_SCIENCES,
                total_questions=self.total_questions,
                correct_answers=natural_sciences
            ),
            AreaType.HUMAN_SCIENCES: ExamArea(
                area_type=AreaType.HUMAN_SCIENCES,
                total_questions=self.total_questions,
                correct_answers=human_sciences
            ),
            AreaType.ESSAY: ExamArea(
                area_type=AreaType.ESSAY,
                total_questions=1,
                correct_answers=1,
                score=essay_score
            )
        }
        
        # Calculate scores for objective areas (use reference_year for z-score projection)
        math_score = self.estimators[AreaType.MATHEMATICS].estimate_score(
            mathematics, current_year=self.reference_year
        )
        lang_score = self.estimators[AreaType.LANGUAGES].estimate_score(
            languages, current_year=self.reference_year
        )
        nat_score = self.estimators[AreaType.NATURAL_SCIENCES].estimate_score(
            natural_sciences, current_year=self.reference_year
        )
        hum_score = self.estimators[AreaType.HUMAN_SCIENCES].estimate_score(
            human_sciences, current_year=self.reference_year
        )
        
        # Calculate score ranges
        math_range = self.estimators[AreaType.MATHEMATICS].estimate_score_range(
            mathematics, current_year=self.reference_year
        )
        lang_range = self.estimators[AreaType.LANGUAGES].estimate_score_range(
            languages, current_year=self.reference_year
        )
        nat_range = self.estimators[AreaType.NATURAL_SCIENCES].estimate_score_range(
            natural_sciences, current_year=self.reference_year
        )
        hum_range = self.estimators[AreaType.HUMAN_SCIENCES].estimate_score_range(
            human_sciences, current_year=self.reference_year
        )
        
        # Update areas with calculated scores
        areas[AreaType.MATHEMATICS].score = math_score
        areas[AreaType.LANGUAGES].score = lang_score
        areas[AreaType.NATURAL_SCIENCES].score = nat_score
        areas[AreaType.HUMAN_SCIENCES].score = hum_score
        
        # Create and return result
        result = ExamResult(
            mathematics_score=math_score,
            languages_score=lang_score,
            natural_sciences_score=nat_score,
            human_sciences_score=hum_score,
            essay_score=essay_score,
            areas=areas,
            mathematics_pessimistic=math_range[0] if math_range else None,
            mathematics_calculated=math_range[1] if math_range else None,
            mathematics_optimistic=math_range[2] if math_range else None,
            languages_pessimistic=lang_range[0] if lang_range else None,
            languages_calculated=lang_range[1] if lang_range else None,
            languages_optimistic=lang_range[2] if lang_range else None,
            natural_sciences_pessimistic=nat_range[0] if nat_range else None,
            natural_sciences_calculated=nat_range[1] if nat_range else None,
            natural_sciences_optimistic=nat_range[2] if nat_range else None,
            human_sciences_pessimistic=hum_range[0] if hum_range else None,
            human_sciences_calculated=hum_range[1] if hum_range else None,
            human_sciences_optimistic=hum_range[2] if hum_range else None
        )
        
        return result
    
    def calculate_area_score(
        self,
        area_type: AreaType,
        correct_answers: int,
        current_year: Optional[int] = None
    ) -> float:
        """
        Calculate score for a specific area.
        
        Args:
            area_type: Type of knowledge area
            correct_answers: Number of correct answers
            current_year: Current year for z-score projection
            
        Returns:
            Estimated score for the area
        """
        if area_type == AreaType.ESSAY:
            raise ValueError("Essay score must be provided directly, not calculated")
        
        if area_type not in self.estimators:
            raise ValueError(f"Invalid area type: {area_type}")
        
        return self.estimators[area_type].estimate_score(
            correct_answers,
            current_year=current_year
        )
    
    def get_confidence_interval(
        self,
        area_type: AreaType,
        correct_answers: int,
        confidence: float = 0.95
    ) -> tuple[float, float]:
        """
        Get confidence interval for a score estimation.
        
        Args:
            area_type: Type of knowledge area
            correct_answers: Number of correct answers
            confidence: Confidence level (default 0.95)
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if area_type == AreaType.ESSAY:
            raise ValueError("Confidence interval not applicable for essay")
        
        if area_type not in self.estimators:
            raise ValueError(f"Invalid area type: {area_type}")
        
        return self.estimators[area_type].get_confidence_interval(
            correct_answers,
            confidence
        )
    
    def load_historical_data(self, data_path: Path) -> None:
        """
        Load historical data to improve estimation accuracy.
        
        Args:
            data_path: Path to directory containing historical data files
        """
        # This method would load historical ENEM data
        # For now, it's a placeholder for future implementation
        pass
    
    def calibrate_with_user_data(
        self,
        area_type: AreaType,
        correct_answers_list: List[int],
        scores_list: List[float],
        years_list: Optional[List[int]] = None
    ) -> None:
        """
        Calibrate estimator for a specific area using user's historical data.
        
        Args:
            area_type: Type of knowledge area
            correct_answers_list: List of correct answers from previous years
            scores_list: List of corresponding official scores
            years_list: List of years corresponding to each data point
        """
        if area_type == AreaType.ESSAY:
            return  # Essay doesn't need calibration
        
        if area_type not in self.estimators:
            return
        
        if len(correct_answers_list) > 0 and len(scores_list) > 0:
            # Load INEP statistics for each year if available
            inep_stats_by_year = {}
            if years_list is not None:
                from src.data_collection.historical_data import HistoricalDataCollector
                collector = HistoricalDataCollector(Path(__file__).parent.parent.parent / "data")
                
                area_name_map = {
                    AreaType.MATHEMATICS: 'mathematics',
                    AreaType.LANGUAGES: 'languages',
                    AreaType.NATURAL_SCIENCES: 'natural_sciences',
                    AreaType.HUMAN_SCIENCES: 'human_sciences',
                }
                area_name = area_name_map.get(area_type)
                
                if area_name:
                    for year in years_list:
                        year_stats = collector.load_inep_statistics(year)
                        if year_stats and area_name in year_stats:
                            inep_stats_by_year[year] = year_stats[area_name]
            
            self.estimators[area_type].set_historical_data(
                correct_answers_list,
                scores_list,
                years_list,
                inep_stats_by_year if inep_stats_by_year else None
            )
    
    def __repr__(self) -> str:
        """Return string representation of the calculator."""
        return (
            f"TriCalculator(questions_per_area={self.total_questions}, "
            f"areas={len(self.estimators)})"
        )
