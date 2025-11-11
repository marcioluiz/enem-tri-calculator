"""
Tests for TRI Estimator.
"""

import pytest
from src.tri_calculator.estimator import TriEstimator


class TestTriEstimator:
    """Test cases for TriEstimator class."""
    
    def test_create_estimator(self):
        """Test creating an estimator with default parameters."""
        estimator = TriEstimator()
        
        assert estimator.total_questions == 45
        assert estimator.min_score == 300.0
        assert estimator.max_score == 900.0
    
    def test_estimate_score_basic(self):
        """Test basic score estimation."""
        estimator = TriEstimator(
            total_questions=45,
            min_score=300.0,
            max_score=900.0
        )
        
        score = estimator.estimate_score(25)
        
        assert 300.0 <= score <= 900.0
        assert isinstance(score, float)
    
    def test_estimate_score_invalid_input(self):
        """Test that invalid input raises error."""
        estimator = TriEstimator(total_questions=45)
        
        with pytest.raises(ValueError, match="must be between"):
            estimator.estimate_score(-1)
        
        with pytest.raises(ValueError, match="must be between"):
            estimator.estimate_score(50)
    
    def test_estimate_score_zero(self):
        """Test estimation with zero correct answers."""
        estimator = TriEstimator(total_questions=45)
        
        score = estimator.estimate_score(0)
        
        assert score >= estimator.min_score
        assert score < estimator.mean_score
    
    def test_estimate_score_all_correct(self):
        """Test estimation with all correct answers."""
        estimator = TriEstimator(total_questions=45)
        
        score = estimator.estimate_score(45)
        
        assert score > estimator.mean_score
        assert score <= estimator.max_score
    
    def test_estimate_score_monotonic(self):
        """Test that scores increase monotonically."""
        estimator = TriEstimator(total_questions=45)
        
        scores = [estimator.estimate_score(i) for i in range(46)]
        
        # Check monotonic increase
        for i in range(len(scores) - 1):
            assert scores[i] <= scores[i + 1]
    
    def test_set_historical_data(self):
        """Test setting historical data."""
        estimator = TriEstimator(total_questions=45)
        
        correct_answers = [0, 10, 20, 30, 40, 45]
        scores = [300.0, 400.0, 500.0, 650.0, 800.0, 900.0]
        
        estimator.set_historical_data(correct_answers, scores)
        
        # Test that exact values are returned
        assert estimator.estimate_score(20) == 500.0
        assert estimator.estimate_score(30) == 650.0
    
    def test_set_historical_data_mismatched_length(self):
        """Test that mismatched data lengths raise error."""
        estimator = TriEstimator(total_questions=45)
        
        with pytest.raises(ValueError, match="must match"):
            estimator.set_historical_data([1, 2, 3], [100.0, 200.0])
    
    def test_estimate_with_logistic(self):
        """Test estimation using logistic curve."""
        estimator = TriEstimator(total_questions=45)
        
        score = estimator.estimate_score(22, use_logistic=True)
        
        assert 300.0 <= score <= 900.0
    
    def test_estimate_with_linear(self):
        """Test estimation using linear model."""
        estimator = TriEstimator(total_questions=45)
        
        score = estimator._estimate_with_linear(22)
        
        assert 300.0 <= score <= 900.0
    
    def test_estimate_proficiency(self):
        """Test proficiency estimation."""
        estimator = TriEstimator(total_questions=45)
        
        # Test various levels
        theta_low = estimator.estimate_proficiency(5)
        theta_mid = estimator.estimate_proficiency(22)
        theta_high = estimator.estimate_proficiency(40)
        
        assert theta_low < theta_mid < theta_high
        assert -3.5 <= theta_low <= 3.5
        assert -3.5 <= theta_mid <= 3.5
        assert -3.5 <= theta_high <= 3.5
    
    def test_get_confidence_interval(self):
        """Test confidence interval calculation."""
        estimator = TriEstimator(total_questions=45)
        
        lower, upper = estimator.get_confidence_interval(25)
        
        assert lower < upper
        assert 0 <= lower <= 1000
        assert 0 <= upper <= 1000
    
    def test_get_confidence_interval_different_levels(self):
        """Test confidence intervals at different levels."""
        estimator = TriEstimator(total_questions=45)
        
        lower_95, upper_95 = estimator.get_confidence_interval(25, confidence=0.95)
        lower_99, upper_99 = estimator.get_confidence_interval(25, confidence=0.99)
        
        # 99% CI should be wider than 95% CI
        assert (upper_99 - lower_99) > (upper_95 - lower_95)
    
    def test_repr(self):
        """Test string representation."""
        estimator = TriEstimator(total_questions=45)
        
        repr_str = repr(estimator)
        assert "TriEstimator" in repr_str
        assert "45" in repr_str
