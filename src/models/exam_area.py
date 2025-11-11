"""
Exam Area Model

Represents a knowledge area in the ENEM exam with its properties.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class AreaType(Enum):
    """Enum for ENEM knowledge areas."""
    
    MATHEMATICS = "mathematics"
    LANGUAGES = "languages"
    NATURAL_SCIENCES = "natural_sciences"
    HUMAN_SCIENCES = "human_sciences"
    ESSAY = "essay"


@dataclass
class ExamArea:
    """
    Represents a knowledge area in the ENEM exam.
    
    Attributes:
        area_type: Type of knowledge area
        total_questions: Total number of questions in this area
        correct_answers: Number of correct answers
        score: Calculated TRI score (0-1000)
    """
    
    area_type: AreaType
    total_questions: int
    correct_answers: int
    score: Optional[float] = None
    
    def __post_init__(self):
        """Validate the exam area data after initialization."""
        if self.correct_answers < 0:
            raise ValueError("Number of correct answers cannot be negative")
        
        if self.correct_answers > self.total_questions:
            raise ValueError(
                f"Correct answers ({self.correct_answers}) cannot exceed "
                f"total questions ({self.total_questions})"
            )
    
    @property
    def accuracy_rate(self) -> float:
        """
        Calculate the accuracy rate (percentage of correct answers).
        
        Returns:
            Accuracy rate as a float between 0 and 1
        """
        if self.total_questions == 0:
            return 0.0
        return self.correct_answers / self.total_questions
    
    @property
    def name(self) -> str:
        """
        Get the human-readable name of the area.
        
        Returns:
            Name of the knowledge area
        """
        names = {
            AreaType.MATHEMATICS: "Matemática e suas Tecnologias",
            AreaType.LANGUAGES: "Linguagens, Códigos e suas Tecnologias",
            AreaType.NATURAL_SCIENCES: "Ciências da Natureza e suas Tecnologias",
            AreaType.HUMAN_SCIENCES: "Ciências Humanas e suas Tecnologias",
            AreaType.ESSAY: "Redação",
        }
        return names.get(self.area_type, "Unknown Area")
    
    def __repr__(self) -> str:
        """Return a string representation of the exam area."""
        score_str = f"{self.score:.1f}" if self.score is not None else "N/A"
        return (
            f"ExamArea(area={self.area_type.value}, "
            f"correct={self.correct_answers}/{self.total_questions}, "
            f"score={score_str})"
        )
