"""
Test HK ticker conversion
"""

from src.connectors.yahoo_client import YahooClient

client = YahooClient()

print("\n" + "="*60)
print("Testing HK Ticker Conversion")
print("="*60)

test_codes = [
    "HK.00001", "HK.00005", "HK.00388", 
    "HK.00700", "HK.09988", "HK.00002"
]

print("\nFutu Code -> Yahoo Ticker:")
print("-"*40)

for code in test_codes:
    yahoo_ticker = client._convert_futu_ticker_to_yahoo(code)
    print(f"  {code} -> {yahoo_ticker}")

print("\n" + "="*60)
print("Testing data fetch for corrected tickers:")
print("-"*60)

for code in test_codes[:3]:  # Test first 3
    print(f"\nTesting {code}...")
    data = client.get_history_kline(code, "2025-01-01", "2026-05-11")
    
    if not data.empty:
        print(f"  ✅ Got {len(data)} days of data")
        print(f"  Latest price: ${data['close'].iloc[-1]:.2f}")
    else:
        print(f"  ❌ No data available")

print("\n" + "="*60)
