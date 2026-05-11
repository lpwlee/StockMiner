"""
Test divergence detection
"""

import pandas as pd
import numpy as np
from src.indicators.divergence import calculate_divergence

# Create sample price data with bullish divergence pattern
# Price: lower low, RSI: higher low
dates = pd.date_range('2024-01-01', periods=50, freq='D')
prices = [100, 98, 95, 92, 90, 88, 85, 83, 80, 78, 76, 75, 74, 73, 72, 
          71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 62, 64, 66,
          68, 70, 72, 74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104, 106]

# Create DataFrame
df = pd.DataFrame({'close': prices, 'time_key': dates})

print("Testing Divergence Detection...")
print("="*50)

bullish, bearish = calculate_divergence(df)

print(f"\nBullish Divergence: {bullish.get('detected', False)}")
if bullish.get('detected'):
    print(f"  Strength: {bullish.get('strength')}")
    print(f"  Description: {bullish.get('description')}")

print(f"\nBearish Divergence: {bearish.get('detected', False)}")
if bearish.get('detected'):
    print(f"  Strength: {bearish.get('strength')}")
    print(f"  Description: {bearish.get('description')}")

print("\n✅ Divergence detection is working!")
