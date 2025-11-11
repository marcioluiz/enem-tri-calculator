"""
Pytest configuration and fixtures.
"""

import pytest
from pathlib import Path


@pytest.fixture
def sample_data_dir(tmp_path):
    """
    Create a temporary directory for test data.
    
    Args:
        tmp_path: Pytest's temporary directory fixture
        
    Returns:
        Path to the temporary data directory
    """
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    raw_dir = data_dir / "raw"
    raw_dir.mkdir()
    
    processed_dir = data_dir / "processed"
    processed_dir.mkdir()
    
    return data_dir


@pytest.fixture
def sample_exam_data():
    """
    Provide sample exam data for testing.
    
    Returns:
        Dictionary with sample exam answers
    """
    return {
        "mathematics": 35,
        "languages": 40,
        "natural_sciences": 38,
        "human_sciences": 42,
        "essay_score": 900.0
    }


@pytest.fixture
def sample_score_mapping():
    """
    Provide a sample score mapping for testing.
    
    Returns:
        Dictionary mapping correct answers to scores
    """
    return {
        0: 300.0,
        10: 380.0,
        20: 500.0,
        30: 650.0,
        40: 820.0,
        45: 900.0
    }
