"""
Tests for TRI Calculator.
"""

import pytest
from src.tri_calculator.calculator import TriCalculator
from src.models.exam_area import AreaType


class TestTriCalculator:
    """Test cases for TriCalculator class."""
    
    def test_create_calculator(self):
        """Test creating a calculator with default parameters."""
        calculator = TriCalculator()
        
        assert calculator.total_questions == 45
        assert len(calculator.estimators) == 4  # 4 objective areas
    
    def test_calculate_score(self):
        """Test calculating scores for all areas."""
        calculator = TriCalculator()
        
        result = calculator.calculate_score(
            mathematics=35,
            languages=40,
            natural_sciences=38,
            human_sciences=42,
            essay_score=900.0
        )
        
        # Check all scores are in valid range
        assert 0 <= result.mathematics_score <= 1000
        assert 0 <= result.languages_score <= 1000
        assert 0 <= result.natural_sciences_score <= 1000
        assert 0 <= result.human_sciences_score <= 1000
        assert result.essay_score == 900.0
        
        # Higher correct answers should generally give higher scores
        assert result.mathematics_score > 500  # 35/45 is good performance
        assert result.languages_score > 500  # 40/45 is excellent
    
    def test_calculate_score_invalid_essay(self):
        """Test that invalid essay score raises error."""
        calculator = TriCalculator()
        
        with pytest.raises(ValueError, match="between 0 and 1000"):
            calculator.calculate_score(
                mathematics=35,
                languages=40,
                natural_sciences=38,
                human_sciences=42,
                essay_score=1500.0
            )
    
    def test_calculate_area_score(self):
        """Test calculating score for a single area."""
        calculator = TriCalculator()
        
        score = calculator.calculate_area_score(AreaType.MATHEMATICS, 30)
        
        assert 0 <= score <= 1000
        assert isinstance(score, float)
    
    def test_calculate_area_score_essay_raises_error(self):
        """Test that calculating essay score raises error."""
        calculator = TriCalculator()
        
        with pytest.raises(ValueError, match="Essay score must be provided directly"):
            calculator.calculate_area_score(AreaType.ESSAY, 1)
    
    def test_get_confidence_interval(self):
        """Test getting confidence interval for a score."""
        calculator = TriCalculator()
        
        lower, upper = calculator.get_confidence_interval(
            AreaType.MATHEMATICS,
            30
        )
        
        assert lower < upper
        assert 0 <= lower <= 1000
        assert 0 <= upper <= 1000
    
    def test_confidence_interval_essay_raises_error(self):
        """Test that confidence interval for essay raises error."""
        calculator = TriCalculator()
        
        with pytest.raises(ValueError, match="not applicable for essay"):
            calculator.get_confidence_interval(AreaType.ESSAY, 1)
    
    def test_score_increases_with_correct_answers(self):
        """Test that score generally increases with more correct answers."""
        calculator = TriCalculator()
        
        scores = []
        for correct in [10, 20, 30, 40]:
            score = calculator.calculate_area_score(AreaType.MATHEMATICS, correct)
            scores.append(score)
        
        # Check monotonic increase
        for i in range(len(scores) - 1):
            assert scores[i] < scores[i + 1]
    
    def test_extreme_values(self):
        """Test calculation with extreme values."""
        calculator = TriCalculator()
        
        # Test with 0 correct answers
        result_min = calculator.calculate_score(
            mathematics=0,
            languages=0,
            natural_sciences=0,
            human_sciences=0,
            essay_score=0.0
        )
        
        # Scores should be low but not necessarily 0 (TRI behavior)
        assert result_min.mathematics_score < 500
        assert result_min.objective_average < 500
        
        # Test with all correct answers
        result_max = calculator.calculate_score(
            mathematics=45,
            languages=45,
            natural_sciences=45,
            human_sciences=45,
            essay_score=1000.0
        )
        
        # Scores should be high
        assert result_max.mathematics_score > 700
        assert result_max.objective_average > 700
    
    def test_repr(self):
        """Test string representation."""
        calculator = TriCalculator()
        
        repr_str = repr(calculator)
        assert "TriCalculator" in repr_str
        assert "45" in repr_str
