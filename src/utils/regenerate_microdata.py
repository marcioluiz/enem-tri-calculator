#!/usr/bin/env python
"""
Regenerate microdata statistics from INEP data.
"""

from src.data_collection.microdata_processor import MicrodataProcessor
from pathlib import Path

if __name__ == '__main__':
    processor = MicrodataProcessor(Path('data'))
    print('Regenerando estatísticas de microdados a partir dos dados INEP...')
    print('=' * 70)
    print()
    
    success_count = 0
    for year in range(2004, 2025):
        if processor.download_microdata(year):
            success_count += 1
            print(f'✓ {year}')
        else:
            print(f'✗ {year}')
    
    print()
    print('=' * 70)
    print(f'✓ {success_count}/21 arquivos gerados!')
    print('  Estatísticas calculadas a partir dos dados INEP')
    print('=' * 70)
