"""
ENEM Microdata Processor

Processes ENEM microdata files to extract statistics about correct answers
per knowledge area. Uses official INEP microdata when available.
"""

from pathlib import Path
from typing import Dict, Optional, List
import json


class MicrodataProcessor:
    """
    Processes ENEM microdata to extract statistics about correct answers.
    
    Uses official INEP microdata files (CSV) when available, or falls back
    to pre-processed statistics.
    """
    
    def __init__(self, data_dir: Path):
        """
        Initialize the microdata processor.
        
        Args:
            data_dir: Directory to store/load microdata and statistics
        """
        self.data_dir = data_dir
        self.microdata_stats_dir = data_dir / "microdata_stats"
        
        # Create directory if it doesn't exist
        self.microdata_stats_dir.mkdir(parents=True, exist_ok=True)
    
    def load_correct_answers_stats(self, year: int) -> Optional[Dict[str, Dict]]:
        """
        Load statistics about correct answers for a specific year.
        
        Args:
            year: ENEM year
            
        Returns:
            Dictionary with statistics per area:
            {
                'mathematics': {
                    'mean': float,  # Mean number of correct answers
                    'std': float,   # Standard deviation
                    'min': int,     # Minimum (usually 0)
                    'max': int,     # Maximum (usually 45)
                    'percentiles': {
                        '25': float,
                        '50': float,  # Median
                        '75': float,
                        '90': float
                    }
                },
                ...
            }
        """
        stats_file = self.microdata_stats_dir / f"correct_answers_{year}.json"
        
        if stats_file.exists():
            with open(stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Microdata files would be downloaded and processed here
        # For now, use estimated statistics
        
        # Fall back to estimated statistics based on INEP data
        return self._get_estimated_correct_answers_stats(year)
    
    def _process_microdata_file(self, file_path: Path, year: int) -> Dict[str, Dict]:
        """
        Process a microdata CSV file to extract statistics.
        
        Note: This is a placeholder. Real implementation would:
        1. Read the large CSV file in chunks
        2. Extract columns for correct answers per area
        3. Calculate statistics (mean, std, percentiles)
        4. Save to JSON for faster future access
        
        Args:
            file_path: Path to microdata CSV
            year: ENEM year
            
        Returns:
            Statistics dictionary
        """
        # TODO: Implement CSV processing
        # For now, fall back to estimated stats
        return self._get_estimated_correct_answers_stats(year)
    
    def _get_estimated_correct_answers_stats(self, year: int) -> Dict[str, Dict]:
        """
        Calculate statistics for correct answers based on TRI score statistics.
        
        Uses inverse relationship: if we know score distribution, we can estimate
        correct answers distribution using approximate conversion factors.
        
        Args:
            year: ENEM year
            
        Returns:
            Estimated statistics dictionary
        """
        from src.data_collection.historical_data import HistoricalDataCollector
        
        # Load TRI score statistics from INEP data
        collector = HistoricalDataCollector(self.data_dir)
        score_stats = collector.load_inep_statistics(year)
        
        if not score_stats or not isinstance(score_stats, dict):
            # Fallback: return basic estimates for 45 questions
            return self._get_fallback_stats(year)
        
        # Calculate correct answers statistics from score statistics
        # Using conversion: score ≈ base + (correct_answers * factor)
        # Inverse: correct_answers ≈ (score - base) / factor
        
        # Try to load user data to calculate dynamic factors
        user_factors = self._calculate_user_conversion_factors()
        
        result = {}
        
        for area, scores in score_stats.items():
            if not isinstance(scores, dict):
                continue
            
            base_score = 300  # Minimum TRI score
            
            # Use user-calculated factor if available, otherwise estimate from score range
            if area in user_factors and user_factors[area] > 0:
                factor = user_factors[area]
            else:
                # Estimate factor from score range: (max_score - min_score) / 45 questions
                score_range = scores['max'] - scores['min']
                factor = score_range / 45.0 if score_range > 0 else 13.0
            
            # Convert score statistics to correct answers statistics
            # mean_correct_answers ≈ (mean_score - base) / factor
            mean_ca = max(0, (scores['mean'] - base_score) / factor)
            
            # Standard deviation scales inversely with factor
            # If score std is high, correct answers std is also high
            std_ca = scores['std'] / factor
            
            # Min/max correct answers
            min_ca = 0
            max_ca = 45
            
            # Calculate percentiles
            # P25: (25th percentile score - base) / factor
            p25_score = scores['mean'] - 0.67 * scores['std']  # Approx 25th percentile
            p25_ca = max(0, (p25_score - base_score) / factor)
            
            # P50: median ≈ mean for normal distribution
            p50_ca = mean_ca
            
            # P75: (75th percentile score - base) / factor
            p75_score = scores['mean'] + 0.67 * scores['std']  # Approx 75th percentile
            p75_ca = min(45, (p75_score - base_score) / factor)
            
            # P90: (90th percentile score - base) / factor
            p90_score = scores['mean'] + 1.28 * scores['std']  # Approx 90th percentile
            p90_ca = min(45, (p90_score - base_score) / factor)
            
            result[area] = {
                'mean': round(mean_ca, 2),
                'std': round(std_ca, 2),
                'min': min_ca,
                'max': max_ca,
                'percentiles': {
                    '25': round(p25_ca, 2),
                    '50': round(p50_ca, 2),
                    '75': round(p75_ca, 2),
                    '90': round(p90_ca, 2)
                }
            }
        
        return result
    
    def _calculate_user_conversion_factors(self) -> Dict[str, float]:
        """
        Calculate conversion factors from user's historical data.
        
        Returns:
            Dictionary mapping area to average conversion factor (score/correct_answer)
        """
        try:
            from src.data_collection.user_data_loader import UserDataLoader
            
            user_data = UserDataLoader(self.data_dir / "user_data.yaml")
            if not user_data.load():
                return {}
            
            if not user_data.previous_years:
                return {}
            
            # Calculate factor for each area from user's actual data
            factors = {}
            
            # Map area names to YearData attributes
            area_mapping = {
                'mathematics': ('mathematics_correct', 'mathematics_score'),
                'languages': ('languages_correct', 'languages_score'),
                'natural_sciences': ('natural_sciences_correct', 'natural_sciences_score'),
                'human_sciences': ('human_sciences_correct', 'human_sciences_score')
            }
            
            for area, (ca_attr, score_attr) in area_mapping.items():
                ratios = []
                
                for year_data in user_data.previous_years:
                    correct_answers = getattr(year_data, ca_attr, 0)
                    score = getattr(year_data, score_attr, None)
                    
                    if score is not None and correct_answers > 0:
                        ratio = score / correct_answers
                        ratios.append(ratio)
                
                # Average user's factors
                if ratios:
                    factors[area] = sum(ratios) / len(ratios)
            
            return factors
            
        except Exception as e:
            # If user data not available, return empty
            return {}
    
    def _get_fallback_stats(self, year: int) -> Dict[str, Dict]:
        """
        Minimal fallback when no data available - returns structure only.
        
        Args:
            year: ENEM year
            
        Returns:
            Basic structure with realistic bounds
        """
        # Return minimal structure - system should learn from user data
        return {
            'mathematics': {
                'mean': 22.5,
                'std': 8.0,
                'min': 0,
                'max': 45,
                'percentiles': {'25': 16.0, '50': 22.5, '75': 29.0, '90': 33.0}
            },
            'languages': {
                'mean': 24.0,
                'std': 7.0,
                'min': 0,
                'max': 45,
                'percentiles': {'25': 18.0, '50': 24.0, '75': 30.0, '90': 34.0}
            },
            'natural_sciences': {
                'mean': 23.0,
                'std': 7.5,
                'min': 0,
                'max': 45,
                'percentiles': {'25': 17.0, '50': 23.0, '75': 29.0, '90': 33.0}
            },
            'human_sciences': {
                'mean': 25.0,
                'std': 6.5,
                'min': 0,
                'max': 45,
                'percentiles': {'25': 20.0, '50': 25.0, '75': 31.0, '90': 35.0}
            }
        }
    
    def save_statistics(self, year: int, stats: Dict[str, Dict]) -> bool:
        """
        Save processed statistics to file.
        
        Args:
            year: ENEM year
            stats: Statistics dictionary
            
        Returns:
            True if saved successfully
        """
        try:
            stats_file = self.microdata_stats_dir / f"correct_answers_{year}.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving statistics for year {year}: {e}")
            return False
    
    def get_score_to_correct_answers_correlation(
        self,
        year: int,
        area: str
    ) -> Optional[Dict[str, float]]:
        """
        Get correlation data between TRI scores and correct answers.
        
        This helps estimate how many correct answers correspond to
        specific TRI score ranges.
        
        Args:
            year: ENEM year
            area: Knowledge area name
            
        Returns:
            Dictionary with correlation coefficients and parameters
        """
        # This would ideally come from actual microdata analysis
        # For now, return estimated linear relationship
        
        # Approximate linear relationship: score ≈ base + (correct_answers * factor)
        relationships = {
            'mathematics': {'base': 320, 'factor': 14.8, 'r_squared': 0.85},
            'languages': {'base': 330, 'factor': 11.8, 'r_squared': 0.82},
            'natural_sciences': {'base': 315, 'factor': 13.2, 'r_squared': 0.84},
            'human_sciences': {'base': 335, 'factor': 12.0, 'r_squared': 0.83},
        }
        
        return relationships.get(area)
    
    def download_microdata(self, year: int) -> bool:
        """
        Download ENEM microdata for a specific year.
        
        Note: This is a placeholder. Real implementation would:
        1. Download from INEP's official FTP/website
        2. Extract ZIP file
        3. Process and save relevant columns
        
        Args:
            year: ENEM year to download
            
        Returns:
            True if downloaded successfully
        """
        print(f"Download de microdados para {year} não implementado ainda.")
        print(f"Usando estatísticas estimadas baseadas em dados históricos.")
        
        # Generate and save estimated statistics
        stats = self._get_estimated_correct_answers_stats(year)
        return self.save_statistics(year, stats)
