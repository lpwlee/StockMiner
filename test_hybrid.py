"""
Quick test of hybrid analyzer
"""

from src.core.analyzer_hybrid import HybridAnalyzer

print("Testing Hybrid Analyzer...")
print("="*60)

analyzer = HybridAnalyzer()

# Test with just 10 stocks first
print("\nTesting with 10 HK stocks...")
rising, falling = analyzer.analyze(
    "HK_STOCKS", 
    max_stocks=10,  # Just test with 10 stocks
    top_n=5,
    show_all=True,
    min_volume=100000  # Lower volume threshold for testing
)

if rising is not None:
    print("\n✅ Test successful! Found rising and falling stocks.")
else:
    print("\n❌ Test failed. No results returned.")

analyzer.disconnect()
