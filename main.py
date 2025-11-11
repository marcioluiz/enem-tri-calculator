#!/usr/bin/env python3
"""
ENEM TRI Calculator - Main Entry Point

This is the main entry point for running the ENEM TRI Calculator CLI.
Can be executed from the project root directory.
"""

import sys
import atexit
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.cli.cli import cli
from src.utils.cache_cleaner import clean_pycache


def cleanup():
    """Cleanup function to run on exit."""
    clean_pycache(verbose=False)


if __name__ == "__main__":
    # Clean cache at startup
    clean_pycache(verbose=False)
    
    # Register cleanup function to run on exit
    atexit.register(cleanup)
    
    try:
        cli()
    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)
