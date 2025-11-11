"""
Cache Cleaner Utility

Cleans Python cache files (__pycache__ directories and .pyc files).
"""

import shutil
from pathlib import Path
from typing import List


def clean_pycache(root_path: Path = None, verbose: bool = False) -> int:
    """
    Clean all __pycache__ directories and .pyc files from the project.
    
    Args:
        root_path: Root directory to start cleaning from. 
                   If None, uses the project root (3 levels up from this file).
        verbose: If True, print information about deleted caches.
    
    Returns:
        Number of cache directories/files removed.
    """
    if root_path is None:
        # Get project root (src/utils/cache_cleaner.py -> ../../..)
        root_path = Path(__file__).parent.parent.parent
    
    root_path = Path(root_path)
    removed_count = 0
    
    # Find and remove __pycache__ directories
    pycache_dirs = list(root_path.rglob("__pycache__"))
    
    for cache_dir in pycache_dirs:
        try:
            shutil.rmtree(cache_dir)
            removed_count += 1
            if verbose:
                print(f"Removed: {cache_dir}")
        except Exception as e:
            if verbose:
                print(f"Failed to remove {cache_dir}: {e}")
    
    # Find and remove .pyc files
    pyc_files = list(root_path.rglob("*.pyc"))
    
    for pyc_file in pyc_files:
        try:
            pyc_file.unlink()
            removed_count += 1
            if verbose:
                print(f"Removed: {pyc_file}")
        except Exception as e:
            if verbose:
                print(f"Failed to remove {pyc_file}: {e}")
    
    # Find and remove .pyo files (Python 2 optimized bytecode)
    pyo_files = list(root_path.rglob("*.pyo"))
    
    for pyo_file in pyo_files:
        try:
            pyo_file.unlink()
            removed_count += 1
            if verbose:
                print(f"Removed: {pyo_file}")
        except Exception as e:
            if verbose:
                print(f"Failed to remove {pyo_file}: {e}")
    
    return removed_count


def get_cache_size(root_path: Path = None) -> int:
    """
    Calculate total size of cache files in bytes.
    
    Args:
        root_path: Root directory to calculate from.
                   If None, uses the project root.
    
    Returns:
        Total size in bytes.
    """
    if root_path is None:
        root_path = Path(__file__).parent.parent.parent
    
    root_path = Path(root_path)
    total_size = 0
    
    # Calculate size of __pycache__ directories
    pycache_dirs = list(root_path.rglob("__pycache__"))
    
    for cache_dir in pycache_dirs:
        for item in cache_dir.rglob("*"):
            if item.is_file():
                total_size += item.stat().st_size
    
    # Calculate size of .pyc files outside __pycache__
    pyc_files = list(root_path.rglob("*.pyc"))
    for pyc_file in pyc_files:
        if "__pycache__" not in str(pyc_file):
            total_size += pyc_file.stat().st_size
    
    return total_size


def format_size(size_bytes: int) -> str:
    """
    Format bytes to human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


if __name__ == "__main__":
    # Can be run directly to clean caches
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean Python cache files")
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed information"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check cache size without cleaning"
    )
    
    args = parser.parse_args()
    
    if args.check_only:
        size = get_cache_size()
        print(f"Total cache size: {format_size(size)}")
    else:
        size = get_cache_size()
        print(f"Cache size before cleaning: {format_size(size)}")
        
        removed = clean_pycache(verbose=args.verbose)
        
        print(f"\n✓ Cleaned {removed} cache files/directories")
        
        size_after = get_cache_size()
        print(f"Cache size after cleaning: {format_size(size_after)}")
