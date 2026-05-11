"""
Test hybrid analyzer with fixed ticker conversion
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from src.core.analyzer_hybrid import HybridAnalyzer

print("\n" + "="*60)
print("🚀 Testing Fixed Hybrid Analyzer")
print("="*60)

analyzer = HybridAnalyzer()

# Test with 20 stocks instead of 5 to increase chance of finding working ones
print("\n📊 Testing with 20 HK stocks...")
rising, falling = analyzer.analyze(
    "HK_STOCKS", 
    max_stocks=20,  # Try 20 stocks
    top_n=10,
    show_all=True,
    min_volume=500000  # Higher volume threshold for better liquidity
)

if rising is not None and not rising.empty:
    print(f"\n✅ SUCCESS! Found {len(rising)} rising stocks:")
    for _, row in rising.head(10).iterrows():
        print(f"   📈 {row['Code']}: {row['Name'][:40]} - Rise: {row['Rise_Score']:.0f}% | RSI: {row['RSI']:.0f}")
    
    if falling is not None and not falling.empty:
        print(f"\n📉 Found {len(falling)} falling stocks:")
        for _, row in falling.head(10).iterrows():
            print(f"   📉 {row['Code']}: {row['Name'][:40]} - Fall: {row['Fall_Score']:.0f}% | RSI: {row['RSI']:.0f}")
else:
    print("\n⚠️ No results. Check if data is available for these stocks.")

analyzer.disconnect()
print("\n" + "="*60)
