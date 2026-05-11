"""
Quick test of hybrid analyzer
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from src.core.analyzer_hybrid import HybridAnalyzer

print("\n" + "="*60)
print("🚀 Testing StockMiner Hybrid Analyzer")
print("="*60)

analyzer = HybridAnalyzer()

print("\n📊 Testing with 5 HK stocks...")
rising, falling = analyzer.analyze(
    "HK_STOCKS", 
    max_stocks=5,  # Just 5 stocks for quick test
    top_n=3,
    show_all=True,
    min_volume=100000
)

if rising is not None and not rising.empty:
    print("\n✅ SUCCESS! Found rising stocks:")
    for _, row in rising.iterrows():
        print(f"   📈 {row['Code']}: {row['Name'][:40]} - Rise: {row['Rise_Score']:.0f}% | RSI: {row['RSI']:.0f}")
    
    if falling is not None and not falling.empty:
        print("\n📉 Found falling stocks:")
        for _, row in falling.iterrows():
            print(f"   📉 {row['Code']}: {row['Name'][:40]} - Fall: {row['Fall_Score']:.0f}% | RSI: {row['RSI']:.0f}")
else:
    print("\n⚠️ No results. Check if FutuOpenD is running and stocks are available.")

analyzer.disconnect()
print("\n" + "="*60)
