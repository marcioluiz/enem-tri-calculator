"""
Tests for cache cleaner utility.
"""

import pytest
from pathlib import Path
import tempfile
import os

from src.utils.cache_cleaner import clean_pycache, get_cache_size, format_size


class TestCacheCleaner:
    """Test cases for cache cleaner functions."""
    
    def test_format_size_bytes(self):
        """Test formatting bytes."""
        assert "100.0 B" == format_size(100)
    
    def test_format_size_kilobytes(self):
        """Test formatting kilobytes."""
        assert "1.0 KB" == format_size(1024)
    
    def test_format_size_megabytes(self):
        """Test formatting megabytes."""
        assert "1.0 MB" == format_size(1024 * 1024)
    
    def test_clean_pycache_with_temp_dir(self):
        """Test cleaning pycache in temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create fake __pycache__ directory
            pycache_dir = tmp_path / "__pycache__"
            pycache_dir.mkdir()
            
            # Create fake .pyc file
            pyc_file = pycache_dir / "test.pyc"
            pyc_file.write_text("fake bytecode")
            
            # Clean cache
            removed = clean_pycache(root_path=tmp_path, verbose=False)
            
            assert removed >= 1
            assert not pycache_dir.exists()
    
    def test_get_cache_size_empty_dir(self):
        """Test getting cache size in empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            size = get_cache_size(root_path=Path(tmpdir))
            assert size == 0
    
    def test_get_cache_size_with_cache(self):
        """Test getting cache size with cache files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create fake __pycache__ directory with file
            pycache_dir = tmp_path / "__pycache__"
            pycache_dir.mkdir()
            
            pyc_file = pycache_dir / "test.pyc"
            pyc_file.write_text("fake bytecode content")
            
            size = get_cache_size(root_path=tmp_path)
            assert size > 0
