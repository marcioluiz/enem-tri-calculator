"""
User Data Loader

Loads and validates user historical data from YAML configuration.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class YearData:
    """Data for a specific year."""
    year: int
    mathematics_correct: int
    mathematics_score: Optional[float] = None
    languages_correct: int = 0
    languages_score: Optional[float] = None
    natural_sciences_correct: int = 0
    natural_sciences_score: Optional[float] = None
    human_sciences_correct: int = 0
    human_sciences_score: Optional[float] = None
    essay_score: float = 0.0


class UserDataLoader:
    """
    Loads user historical data from YAML configuration file.
    """
    
    def __init__(self, data_path: Path = None):
        """
        Initialize the data loader.
        
        Args:
            data_path: Path to YAML configuration file.
                       If None, uses default data/user_data.yaml
        """
        if data_path is None:
            # Default path relative to project root
            project_root = Path(__file__).parent.parent.parent
            data_path = project_root / "data" / "user_data.yaml"
        
        self.data_path = Path(data_path)
        self.data: Dict[str, Any] = {}
        self.current_year: Optional[YearData] = None
        self.previous_years: List[YearData] = []
        self.settings: Dict[str, Any] = {}
    
    def load(self) -> bool:
        """
        Load data from YAML file.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.data_path.exists():
            return False
        
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.data = yaml.safe_load(f)
            
            # Parse current year data
            if 'current_year' in self.data:
                self.current_year = self._parse_current_year(self.data['current_year'])
            
            # Parse previous years data
            if 'previous_years' in self.data:
                self.previous_years = self._parse_previous_years(self.data['previous_years'])
            
            # Load settings
            if 'settings' in self.data:
                self.settings = self.data['settings']
            
            return True
            
        except Exception as e:
            print(f"Error loading user data: {e}")
            return False
    
    def _parse_current_year(self, data: Dict) -> YearData:
        """Parse current year data (only correct answers)."""
        if not data:
            return None
            
        return YearData(
            year=data.get('year', 2025),
            mathematics_correct=data.get('mathematics', 0),
            languages_correct=data.get('languages', 0),
            natural_sciences_correct=data.get('natural_sciences', 0),
            human_sciences_correct=data.get('human_sciences', 0),
            essay_score=data.get('essay_score', 0.0)
        )
    
    def _parse_previous_years(self, data: List[Dict]) -> List[YearData]:
        """Parse previous years data (correct answers and official scores)."""
        previous = []
        
        for year_data in data:
            math_data = year_data.get('mathematics', {})
            lang_data = year_data.get('languages', {})
            nat_data = year_data.get('natural_sciences', {})
            hum_data = year_data.get('human_sciences', {})
            
            year_obj = YearData(
                year=year_data.get('year', 0),
                mathematics_correct=math_data.get('correct_answers') or 0,
                mathematics_score=math_data.get('official_score'),
                languages_correct=lang_data.get('correct_answers') or 0,
                languages_score=lang_data.get('official_score'),
                natural_sciences_correct=nat_data.get('correct_answers') or 0,
                natural_sciences_score=nat_data.get('official_score'),
                human_sciences_correct=hum_data.get('correct_answers') or 0,
                human_sciences_score=hum_data.get('official_score'),
                essay_score=year_data.get('essay_score', 0.0)
            )
            previous.append(year_obj)
        
        return previous
    
    def get_historical_data_for_area(self, area: str) -> tuple[List[int], List[float]]:
        """
        Get historical correct answers and scores for a specific area.
        
        Args:
            area: Area name ('mathematics', 'languages', 'natural_sciences', 'human_sciences')
            
        Returns:
            Tuple of (correct_answers_list, scores_list)
            Note: correct_answers may be 0 if not provided, but scores will always have values
        """
        correct_answers = []
        scores = []
        
        for year_data in self.previous_years:
            if area == 'mathematics':
                if year_data.mathematics_score is not None and year_data.mathematics_correct > 0:
                    correct_answers.append(year_data.mathematics_correct)
                    scores.append(year_data.mathematics_score)
            elif area == 'languages':
                if year_data.languages_score is not None and year_data.languages_correct > 0:
                    correct_answers.append(year_data.languages_correct)
                    scores.append(year_data.languages_score)
            elif area == 'natural_sciences':
                if year_data.natural_sciences_score is not None and year_data.natural_sciences_correct > 0:
                    correct_answers.append(year_data.natural_sciences_correct)
                    scores.append(year_data.natural_sciences_score)
            elif area == 'human_sciences':
                if year_data.human_sciences_score is not None and year_data.human_sciences_correct > 0:
                    correct_answers.append(year_data.human_sciences_correct)
                    scores.append(year_data.human_sciences_score)
        
        return correct_answers, scores
    
    def get_historical_data_with_years(self, area: str) -> tuple[List[int], List[float], List[int]]:
        """
        Get historical correct answers, scores, and years for a specific area.
        
        Args:
            area: Area name ('mathematics', 'languages', 'natural_sciences', 'human_sciences')
            
        Returns:
            Tuple of (correct_answers_list, scores_list, years_list)
        """
        correct_answers = []
        scores = []
        years = []
        
        for year_data in self.previous_years:
            include = False
            ca = 0
            score = None
            
            if area == 'mathematics' and year_data.mathematics_score is not None:
                ca = year_data.mathematics_correct
                score = year_data.mathematics_score
                include = True
            elif area == 'languages' and year_data.languages_score is not None:
                ca = year_data.languages_correct
                score = year_data.languages_score
                include = True
            elif area == 'natural_sciences' and year_data.natural_sciences_score is not None:
                ca = year_data.natural_sciences_correct
                score = year_data.natural_sciences_score
                include = True
            elif area == 'human_sciences' and year_data.human_sciences_score is not None:
                ca = year_data.human_sciences_correct
                score = year_data.human_sciences_score
                include = True
            
            if include:
                correct_answers.append(ca)
                scores.append(score)
                years.append(year_data.year)
        
        return correct_answers, scores, years
    
    def get_historical_scores_only(self, area: str) -> List[float]:
        """
        Get only historical scores for an area (without correct answers requirement).
        Useful for adjusting statistical parameters even without correct answer data.
        
        Args:
            area: Area name ('mathematics', 'languages', 'natural_sciences', 'human_sciences')
            
        Returns:
            List of historical scores
        """
        scores = []
        
        for year_data in self.previous_years:
            score = None
            if area == 'mathematics':
                score = year_data.mathematics_score
            elif area == 'languages':
                score = year_data.languages_score
            elif area == 'natural_sciences':
                score = year_data.natural_sciences_score
            elif area == 'human_sciences':
                score = year_data.human_sciences_score
            
            if score is not None:
                scores.append(score)
        
        return scores
    
    def has_historical_data(self) -> bool:
        """Check if there is any historical data available."""
        return len(self.previous_years) > 0
    
    def use_historical_data(self) -> bool:
        """Check if historical data should be used based on settings."""
        return self.settings.get('use_historical_data', True)
    
    def show_comparison(self) -> bool:
        """Check if comparison with previous years should be shown."""
        return self.settings.get('show_comparison', True)
    
    def get_confidence_level(self) -> float:
        """Get the confidence level for intervals."""
        return self.settings.get('confidence_level', 0.95)
    
    def validate_current_year(self) -> tuple[bool, List[str]]:
        """
        Validate current year data.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if self.current_year is None:
            errors.append("No current year data found")
            return False, errors
        
        # Validate correct answers range (handle None values)
        for field, value in [
            ('mathematics', self.current_year.mathematics_correct),
            ('languages', self.current_year.languages_correct),
            ('natural_sciences', self.current_year.natural_sciences_correct),
            ('human_sciences', self.current_year.human_sciences_correct),
        ]:
            if value is None:
                errors.append(f"{field}: correct answers cannot be None")
            elif not 0 <= value <= 45:
                errors.append(f"{field}: correct answers must be between 0 and 45, got {value}")
        
        # Validate essay score (handle None)
        if self.current_year.essay_score is None:
            errors.append("essay_score cannot be None")
        elif not 0 <= self.current_year.essay_score <= 1000:
            errors.append(f"essay_score must be between 0 and 1000, got {self.current_year.essay_score}")
        
        return len(errors) == 0, errors
    
    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"UserDataLoader(current_year={self.current_year.year if self.current_year else None}, "
            f"previous_years={len(self.previous_years)})"
        )
