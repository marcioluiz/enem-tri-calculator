"""
TRI Parameters Model

Represents the statistical parameters used in TRI calculations.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import json
from pathlib import Path


@dataclass
class TriParameters:
    """
    Represents TRI statistical parameters for score estimation.
    
    Attributes:
        mean_score: Mean score for the distribution
        std_deviation: Standard deviation of the score distribution
        min_score: Minimum possible score
        max_score: Maximum possible score
        score_map: Mapping of number of correct answers to expected scores
    """
    
    mean_score: float
    std_deviation: float
    min_score: float = 0.0
    max_score: float = 1000.0
    score_map: Optional[Dict[int, float]] = None
    
    def __post_init__(self):
        """Initialize score map if not provided."""
        if self.score_map is None:
            self.score_map = {}
    
    @classmethod
    def from_historical_data(
        cls,
        correct_answers: List[int],
        scores: List[float]
    ) -> 'TriParameters':
        """
        Create TRI parameters from historical data.
        
        Args:
            correct_answers: List of number of correct answers
            scores: List of corresponding scores
            
        Returns:
            TriParameters object with calculated statistics
        """
        import numpy as np
        
        mean = float(np.mean(scores))
        std = float(np.std(scores))
        min_score = float(np.min(scores))
        max_score = float(np.max(scores))
        
        # Create score map
        score_map = dict(zip(correct_answers, scores))
        
        return cls(
            mean_score=mean,
            std_deviation=std,
            min_score=min_score,
            max_score=max_score,
            score_map=score_map
        )
    
    def estimate_score(self, correct_answers: int) -> float:
        """
        Estimate score based on number of correct answers.
        
        Args:
            correct_answers: Number of correct answers
            
        Returns:
            Estimated score (0-1000)
        """
        # If we have exact mapping, use it
        if self.score_map and correct_answers in self.score_map:
            return self.score_map[correct_answers]
        
        # Otherwise, use interpolation or return mean
        return self.mean_score
    
    def save_to_file(self, filepath: Path) -> None:
        """
        Save parameters to a JSON file.
        
        Args:
            filepath: Path to save the parameters
        """
        data = {
            "mean_score": self.mean_score,
            "std_deviation": self.std_deviation,
            "min_score": self.min_score,
            "max_score": self.max_score,
            "score_map": self.score_map
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, filepath: Path) -> 'TriParameters':
        """
        Load parameters from a JSON file.
        
        Args:
            filepath: Path to load the parameters from
            
        Returns:
            TriParameters object
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert string keys back to integers for score_map
        score_map = None
        if data.get('score_map'):
            score_map = {int(k): v for k, v in data['score_map'].items()}
        
        return cls(
            mean_score=data['mean_score'],
            std_deviation=data['std_deviation'],
            min_score=data.get('min_score', 0.0),
            max_score=data.get('max_score', 1000.0),
            score_map=score_map
        )
    
    def __repr__(self) -> str:
        """Return a string representation of the TRI parameters."""
        return (
            f"TriParameters(mean={self.mean_score:.1f}, "
            f"std={self.std_deviation:.1f})"
        )
