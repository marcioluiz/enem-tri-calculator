"""
Tests for ExamArea model.
"""

import pytest
from src.models.exam_area import ExamArea, AreaType


class TestExamArea:
    """Test cases for ExamArea class."""
    
    def test_create_exam_area(self):
        """Test creating a valid exam area."""
        area = ExamArea(
            area_type=AreaType.MATHEMATICS,
            total_questions=45,
            correct_answers=30
        )
        
        assert area.area_type == AreaType.MATHEMATICS
        assert area.total_questions == 45
        assert area.correct_answers == 30
        assert area.score is None
    
    def test_create_exam_area_with_score(self):
        """Test creating an exam area with a score."""
        area = ExamArea(
            area_type=AreaType.LANGUAGES,
            total_questions=45,
            correct_answers=35,
            score=700.5
        )
        
        assert area.score == 700.5
    
    def test_negative_correct_answers_raises_error(self):
        """Test that negative correct answers raise ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            ExamArea(
                area_type=AreaType.MATHEMATICS,
                total_questions=45,
                correct_answers=-1
            )
    
    def test_correct_answers_exceed_total_raises_error(self):
        """Test that correct answers exceeding total raises ValueError."""
        with pytest.raises(ValueError, match="cannot exceed"):
            ExamArea(
                area_type=AreaType.MATHEMATICS,
                total_questions=45,
                correct_answers=50
            )
    
    def test_accuracy_rate(self):
        """Test accuracy rate calculation."""
        area = ExamArea(
            area_type=AreaType.MATHEMATICS,
            total_questions=45,
            correct_answers=36
        )
        
        assert area.accuracy_rate == pytest.approx(0.8, rel=1e-6)
    
    def test_accuracy_rate_zero_questions(self):
        """Test accuracy rate with zero questions."""
        area = ExamArea(
            area_type=AreaType.MATHEMATICS,
            total_questions=0,
            correct_answers=0
        )
        
        assert area.accuracy_rate == 0.0
    
    def test_area_name(self):
        """Test getting area name."""
        areas = [
            (AreaType.MATHEMATICS, "Matemática e suas Tecnologias"),
            (AreaType.LANGUAGES, "Linguagens, Códigos e suas Tecnologias"),
            (AreaType.NATURAL_SCIENCES, "Ciências da Natureza e suas Tecnologias"),
            (AreaType.HUMAN_SCIENCES, "Ciências Humanas e suas Tecnologias"),
            (AreaType.ESSAY, "Redação"),
        ]
        
        for area_type, expected_name in areas:
            area = ExamArea(
                area_type=area_type,
                total_questions=45,
                correct_answers=20
            )
            assert area.name == expected_name
    
    def test_repr(self):
        """Test string representation."""
        area = ExamArea(
            area_type=AreaType.MATHEMATICS,
            total_questions=45,
            correct_answers=30,
            score=650.0
        )
        
        repr_str = repr(area)
        assert "mathematics" in repr_str
        assert "30/45" in repr_str
        assert "650.0" in repr_str
