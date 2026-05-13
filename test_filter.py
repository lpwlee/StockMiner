"""
Test filtering logic
"""

import pandas as pd
from src.ui.components.filtering import filter_stocks

# Create sample data
sample_data = pd.DataFrame([
    {'Code': 'HK.09992', 'Confirm_Buy': False, 'Confirm_Sell': True, 'Bullish_Divergence': True, 'Bearish_Divergence': False, 'Rise_Score': 50, 'Fall_Score': 78},
    {'Code': 'HK.09987', 'Confirm_Buy': True, 'Confirm_Sell': False, 'Bullish_Divergence': True, 'Bearish_Divergence': False, 'Rise_Score': 60, 'Fall_Score': 50},
    {'Code': 'HK.00576', 'Confirm_Buy': True, 'Confirm_Sell': False, 'Bullish_Divergence': False, 'Bearish_Divergence': True, 'Rise_Score': 85, 'Fall_Score': 50},
])

print("Testing filters:")
print(f"Buy filter: {len(filter_stocks(sample_data, 'buy'))} stocks")
print(f"Sell filter: {len(filter_stocks(sample_data, 'sell'))} stocks")
print(f"Divergence filter: {len(filter_stocks(sample_data, 'divergence'))} stocks")
print(f"All filter: {len(filter_stocks(sample_data, 'all'))} stocks")
