"""
Test Yahoo Finance with HK stocks
"""

import yfinance as yf

print("Testing Yahoo Finance with HK stocks...")
print("="*50)

# Test different formats
test_tickers = [
    "0700.HK",      # Tencent
    "0005.HK",      # HSBC
    "9988.HK",      # Alibaba
    "700.HK",       # Tencent without leading zero
]

for ticker in test_tickers:
    print(f"\nTesting {ticker}...")
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        print(f"  Name: {info.get('longName', 'N/A')}")
        
        # Get recent data
        hist = stock.history(period="5d")
        if not hist.empty:
            print(f"  Latest price: ${hist['Close'].iloc[-1]:.2f}")
            print(f"  ✅ Success!")
        else:
            print(f"  ⚠️ No data found")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "="*50)
print("Testing with Futu format conversion...")

from src.connectors.yahoo_client import YahooClient
client = YahooClient()

test_futu_codes = ["HK.00700", "HK.00005", "HK.09988"]
for code in test_futu_codes:
    ticker = client._convert_futu_ticker_to_yahoo(code)
    print(f"  {code} -> {ticker}")

print("\n✅ Test complete!")
