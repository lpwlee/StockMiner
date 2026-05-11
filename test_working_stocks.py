"""
Test with known working HK stocks
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from src.connectors.yahoo_client import YahooClient

print("\n" + "="*60)
print("Testing with known HK stocks")
print("="*60)

client = YahooClient()

# Known HK stocks that should work
test_stocks = [
    "HK.00700",  # Tencent
    "HK.09988",  # Alibaba  
    "HK.00005",  # HSBC
    "HK.00388",  # HKEX
]

print("\n📊 Testing Yahoo Finance data fetch:")
print("-"*60)

for code in test_stocks:
    print(f"\nTesting {code}...")
    ticker = client._convert_futu_ticker_to_yahoo(code)
    print(f"  Yahoo ticker: {ticker}")
    
    data = client.get_history_kline(code, "2025-01-01", "2026-05-11")
    
    if not data.empty:
        print(f"  ✅ Got {len(data)} days of data")
        print(f"  Latest price: ${data['close'].iloc[-1]:.2f}")
        print(f"  Latest volume: {data['volume'].iloc[-1]:,.0f}")
    else:
        print(f"  ❌ No data available")

client.disconnect()
print("\n" + "="*60)
