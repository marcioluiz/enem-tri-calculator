"""
Tests for user data loader.
"""

import pytest
from pathlib import Path
import tempfile
import yaml

from src.data_collection.user_data_loader import UserDataLoader, YearData


class TestUserDataLoader:
    """Test cases for UserDataLoader class."""
    
    def test_create_loader(self):
        """Test creating a loader instance."""
        loader = UserDataLoader()
        assert loader is not None
    
    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file."""
        loader = UserDataLoader(Path("/nonexistent/path.yaml"))
        result = loader.load()
        assert result is False
    
    def test_load_valid_yaml(self):
        """Test loading valid YAML file."""
        data = {
            'current_year': {
                'year': 2025,
                'mathematics': 35,
                'languages': 40,
                'natural_sciences': 38,
                'human_sciences': 42,
                'essay_score': 900
            },
            'previous_years': [
                {
                    'year': 2024,
                    'mathematics': {
                        'correct_answers': 30,
                        'official_score': 650.5
                    },
                    'languages': {
                        'correct_answers': 38,
                        'official_score': 720.3
                    },
                    'natural_sciences': {
                        'correct_answers': 35,
                        'official_score': 680.7
                    },
                    'human_sciences': {
                        'correct_answers': 40,
                        'official_score': 750.2
                    },
                    'essay_score': 880
                }
            ],
            'settings': {
                'use_historical_data': True,
                'show_comparison': True,
                'confidence_level': 0.95
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(data, f)
            temp_path = Path(f.name)
        
        try:
            loader = UserDataLoader(temp_path)
            result = loader.load()
            
            assert result is True
            assert loader.current_year.year == 2025
            assert loader.current_year.mathematics_correct == 35
            assert len(loader.previous_years) == 1
            assert loader.previous_years[0].mathematics_score == 650.5
        finally:
            temp_path.unlink()
    
    def test_validate_current_year_valid(self):
        """Test validation of valid current year data."""
        loader = UserDataLoader()
        loader.current_year = YearData(
            year=2025,
            mathematics_correct=35,
            languages_correct=40,
            natural_sciences_correct=38,
            human_sciences_correct=42,
            essay_score=900
        )
        
        is_valid, errors = loader.validate_current_year()
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_current_year_invalid_range(self):
        """Test validation with out of range values."""
        loader = UserDataLoader()
        loader.current_year = YearData(
            year=2025,
            mathematics_correct=50,  # Invalid: > 45
            languages_correct=40,
            natural_sciences_correct=38,
            human_sciences_correct=42,
            essay_score=900
        )
        
        is_valid, errors = loader.validate_current_year()
        assert is_valid is False
        assert len(errors) > 0
    
    def test_get_historical_data_for_area(self):
        """Test getting historical data for specific area."""
        loader = UserDataLoader()
        loader.previous_years = [
            YearData(
                year=2024,
                mathematics_correct=30,
                mathematics_score=650.5,
                languages_correct=38,
                languages_score=720.3,
                natural_sciences_correct=35,
                natural_sciences_score=680.7,
                human_sciences_correct=40,
                human_sciences_score=750.2,
                essay_score=880
            )
        ]
        
        correct, scores = loader.get_historical_data_for_area('mathematics')
        
        assert len(correct) == 1
        assert len(scores) == 1
        assert correct[0] == 30
        assert scores[0] == 650.5
    
    def test_has_historical_data(self):
        """Test checking for historical data."""
        loader = UserDataLoader()
        assert loader.has_historical_data() is False
        
        loader.previous_years = [YearData(year=2024, mathematics_correct=30)]
        assert loader.has_historical_data() is True
    
    def test_settings_defaults(self):
        """Test default settings values."""
        loader = UserDataLoader()
        assert loader.use_historical_data() is True
        assert loader.show_comparison() is True
        assert loader.get_confidence_level() == 0.95
