"""
Exam Result Model

Represents the complete result of an ENEM exam with all areas.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from src.models.exam_area import ExamArea, AreaType


@dataclass
class ExamResult:
    """
    Represents the complete result of an ENEM exam.
    
    Attributes:
        mathematics_score: Score for Mathematics area (0-1000)
        languages_score: Score for Languages area (0-1000)
        natural_sciences_score: Score for Natural Sciences area (0-1000)
        human_sciences_score: Score for Human Sciences area (0-1000)
        essay_score: Score for Essay (0-1000)
        areas: Dictionary containing ExamArea objects for each area
        mathematics_pessimistic: Pessimistic score for Mathematics (optional)
        mathematics_optimistic: Optimistic score for Mathematics (optional)
        languages_pessimistic: Pessimistic score for Languages (optional)
        languages_optimistic: Optimistic score for Languages (optional)
        natural_sciences_pessimistic: Pessimistic score for Natural Sciences (optional)
        natural_sciences_optimistic: Optimistic score for Natural Sciences (optional)
        human_sciences_pessimistic: Pessimistic score for Human Sciences (optional)
        human_sciences_optimistic: Optimistic score for Human Sciences (optional)
    """
    
    mathematics_score: float
    languages_score: float
    natural_sciences_score: float
    human_sciences_score: float
    essay_score: float
    areas: Dict[AreaType, ExamArea] = field(default_factory=dict)
    mathematics_pessimistic: Optional[float] = None
    mathematics_calculated: Optional[float] = None
    mathematics_optimistic: Optional[float] = None
    languages_pessimistic: Optional[float] = None
    languages_calculated: Optional[float] = None
    languages_optimistic: Optional[float] = None
    natural_sciences_pessimistic: Optional[float] = None
    natural_sciences_calculated: Optional[float] = None
    natural_sciences_optimistic: Optional[float] = None
    human_sciences_pessimistic: Optional[float] = None
    human_sciences_calculated: Optional[float] = None
    human_sciences_optimistic: Optional[float] = None
    
    def __post_init__(self):
        """Validate scores after initialization."""
        scores = [
            self.mathematics_score,
            self.languages_score,
            self.natural_sciences_score,
            self.human_sciences_score,
            self.essay_score,
        ]
        
        for score in scores:
            if score < 0 or score > 1000:
                raise ValueError(f"Score {score} must be between 0 and 1000")
    
    @property
    def average_score(self) -> float:
        """
        Calculate the average score across all areas.
        
        Returns:
            Average score (0-1000)
        """
        return (
            self.mathematics_score +
            self.languages_score +
            self.natural_sciences_score +
            self.human_sciences_score +
            self.essay_score
        ) / 5
    
    @property
    def objective_average(self) -> float:
        """
        Calculate the average score for objective tests only (excluding essay).
        
        Returns:
            Average score for objective tests (0-1000)
        """
        return (
            self.mathematics_score +
            self.languages_score +
            self.natural_sciences_score +
            self.human_sciences_score
        ) / 4
    
    def get_score_by_area(self, area_type: AreaType) -> float:
        """
        Get the score for a specific area.
        
        Args:
            area_type: The area type to get the score for
            
        Returns:
            Score for the specified area
        """
        area_scores = {
            AreaType.MATHEMATICS: self.mathematics_score,
            AreaType.LANGUAGES: self.languages_score,
            AreaType.NATURAL_SCIENCES: self.natural_sciences_score,
            AreaType.HUMAN_SCIENCES: self.human_sciences_score,
            AreaType.ESSAY: self.essay_score,
        }
        return area_scores.get(area_type, 0.0)
    
    def to_dict(self) -> Dict[str, float]:
        """
        Convert the exam result to a dictionary.
        
        Returns:
            Dictionary with area names and scores
        """
        return {
            "mathematics": self.mathematics_score,
            "languages": self.languages_score,
            "natural_sciences": self.natural_sciences_score,
            "human_sciences": self.human_sciences_score,
            "essay": self.essay_score,
            "average": self.average_score,
            "objective_average": self.objective_average,
        }
    
    def __repr__(self) -> str:
        """Return a string representation of the exam result."""
        return (
            f"ExamResult(\n"
            f"  Mathematics: {self.mathematics_score:.1f}\n"
            f"  Languages: {self.languages_score:.1f}\n"
            f"  Natural Sciences: {self.natural_sciences_score:.1f}\n"
            f"  Human Sciences: {self.human_sciences_score:.1f}\n"
            f"  Essay: {self.essay_score:.1f}\n"
            f"  Average: {self.average_score:.1f}\n"
            f")"
        )
