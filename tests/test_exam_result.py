"""
Tests for ExamResult model.
"""

import pytest
from src.models.exam_result import ExamResult
from src.models.exam_area import AreaType


class TestExamResult:
    """Test cases for ExamResult class."""
    
    def test_create_exam_result(self):
        """Test creating a valid exam result."""
        result = ExamResult(
            mathematics_score=700.0,
            languages_score=650.0,
            natural_sciences_score=680.0,
            human_sciences_score=720.0,
            essay_score=900.0
        )
        
        assert result.mathematics_score == 700.0
        assert result.languages_score == 650.0
        assert result.natural_sciences_score == 680.0
        assert result.human_sciences_score == 720.0
        assert result.essay_score == 900.0
    
    def test_score_below_zero_raises_error(self):
        """Test that scores below 0 raise ValueError."""
        with pytest.raises(ValueError, match="between 0 and 1000"):
            ExamResult(
                mathematics_score=-10.0,
                languages_score=650.0,
                natural_sciences_score=680.0,
                human_sciences_score=720.0,
                essay_score=900.0
            )
    
    def test_score_above_thousand_raises_error(self):
        """Test that scores above 1000 raise ValueError."""
        with pytest.raises(ValueError, match="between 0 and 1000"):
            ExamResult(
                mathematics_score=700.0,
                languages_score=650.0,
                natural_sciences_score=1100.0,
                human_sciences_score=720.0,
                essay_score=900.0
            )
    
    def test_average_score(self):
        """Test average score calculation."""
        result = ExamResult(
            mathematics_score=700.0,
            languages_score=600.0,
            natural_sciences_score=650.0,
            human_sciences_score=750.0,
            essay_score=800.0
        )
        
        expected_avg = (700.0 + 600.0 + 650.0 + 750.0 + 800.0) / 5
        assert result.average_score == pytest.approx(expected_avg, rel=1e-6)
    
    def test_objective_average(self):
        """Test objective tests average calculation."""
        result = ExamResult(
            mathematics_score=700.0,
            languages_score=600.0,
            natural_sciences_score=650.0,
            human_sciences_score=750.0,
            essay_score=800.0
        )
        
        expected_avg = (700.0 + 600.0 + 650.0 + 750.0) / 4
        assert result.objective_average == pytest.approx(expected_avg, rel=1e-6)
    
    def test_get_score_by_area(self):
        """Test getting score by area type."""
        result = ExamResult(
            mathematics_score=700.0,
            languages_score=650.0,
            natural_sciences_score=680.0,
            human_sciences_score=720.0,
            essay_score=900.0
        )
        
        assert result.get_score_by_area(AreaType.MATHEMATICS) == 700.0
        assert result.get_score_by_area(AreaType.LANGUAGES) == 650.0
        assert result.get_score_by_area(AreaType.NATURAL_SCIENCES) == 680.0
        assert result.get_score_by_area(AreaType.HUMAN_SCIENCES) == 720.0
        assert result.get_score_by_area(AreaType.ESSAY) == 900.0
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = ExamResult(
            mathematics_score=700.0,
            languages_score=650.0,
            natural_sciences_score=680.0,
            human_sciences_score=720.0,
            essay_score=900.0
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["mathematics"] == 700.0
        assert result_dict["languages"] == 650.0
        assert result_dict["natural_sciences"] == 680.0
        assert result_dict["human_sciences"] == 720.0
        assert result_dict["essay"] == 900.0
        assert "average" in result_dict
        assert "objective_average" in result_dict
    
    def test_repr(self):
        """Test string representation."""
        result = ExamResult(
            mathematics_score=700.0,
            languages_score=650.0,
            natural_sciences_score=680.0,
            human_sciences_score=720.0,
            essay_score=900.0
        )
        
        repr_str = repr(result)
        assert "700.0" in repr_str
        assert "650.0" in repr_str
        assert "Average" in repr_str
