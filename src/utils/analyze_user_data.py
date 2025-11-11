#!/usr/bin/env python3
"""
Analyze user's historical data to understand conversion factors
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data_collection.user_data_loader import UserDataLoader

def main():
    data_dir = Path("data")
    user_data = UserDataLoader(data_dir / "user_data.yaml")
    user_data.load()
    
    print("=" * 70)
    print("USER'S HISTORICAL DATA ANALYSIS")
    print("=" * 70)
    
    areas = ['mathematics', 'languages', 'natural_sciences', 'human_sciences']
    area_mapping = {
        'mathematics': ('mathematics_correct', 'mathematics_score'),
        'languages': ('languages_correct', 'languages_score'),
        'natural_sciences': ('natural_sciences_correct', 'natural_sciences_score'),
        'human_sciences': ('human_sciences_correct', 'human_sciences_score')
    }
    
    for area in areas:
        ca_attr, score_attr = area_mapping[area]
        print(f"\n{area.upper().replace('_', ' ')}:")
        print("-" * 70)
        
        ratios = []
        for year_data in user_data.previous_years:
            ca = getattr(year_data, ca_attr, 0)
            score = getattr(year_data, score_attr, None)
            
            if score is not None:
                if ca > 0:
                    ratio = score / ca
                    ratios.append(ratio)
                    print(f"  {year_data.year}: {ca:2d} acertos → {score:6.1f} pontos (ratio: {ratio:.2f})")
                else:
                    print(f"  {year_data.year}: ?? acertos → {score:6.1f} pontos (no CA data)")
        
        if ratios:
            avg_ratio = sum(ratios) / len(ratios)
            print(f"\n  Average ratio: {avg_ratio:.2f} points/correct_answer")
            print(f"  This means: score ≈ {avg_ratio:.2f} × correct_answers")
    
    print("\n" + "=" * 70)
    print("CURRENT YEAR (2025) PREDICTIONS:")
    print("=" * 70)
    
    current = user_data.current_year
    if current:
        print(f"\nUsing simple multiplication (score = ratio × CA):")
        print("-" * 70)
        
        for area in areas:
            ca_attr, _ = area_mapping[area]
            ca = getattr(current, ca_attr.replace('_score', '').replace('_correct', ''), 0)
            
            # Calculate ratio from previous years
            ratios = []
            for year_data in user_data.previous_years:
                year_ca = getattr(year_data, ca_attr, 0)
                year_score = getattr(year_data, ca_attr.replace('_correct', '_score'), None)
                if year_score and year_ca > 0:
                    ratios.append(year_score / year_ca)
            
            if ratios:
                avg_ratio = sum(ratios) / len(ratios)
                predicted = ca * avg_ratio
                print(f"  {area:20s}: {ca:2d} × {avg_ratio:5.2f} = {predicted:6.1f}")

if __name__ == "__main__":
    main()
