"""
Hybrid CLI - Dynamic stock lists from Futu, data from Yahoo
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.analyzer_hybrid import HybridAnalyzer

def print_banner():
    print("\n" + "="*60)
    print("  🚀 StockMiner - Dynamic Hybrid Edition")
    print("="*60)
    print("\n  ✅ NO HARDCODED STOCKS!")
    print("  ✅ Stock list: Dynamic from Futu (always current)")
    print("  ✅ Data: Yahoo Finance (no quotas)")
    print("  ✅ Supports ALL HK and US stocks")

def main():
    print_banner()
    
    analyzer = HybridAnalyzer()
    
    while True:
        print("\n" + "="*60)
        print("📋 MAIN MENU")
        print("="*60)
        print("   ⚡ QUICK (100 stocks, ~1 min):")
        print("     1. Hong Kong Stocks - Quick")
        print("     2. US Stocks - Quick")
        print("")
        print("   🔍 FULL (All active stocks, ~5-8 min):")
        print("     3. Hong Kong Stocks - FULL")
        print("     4. US Stocks - FULL")
        print("")
        print("   5. Exit")
        
        choice = input("\n👉 Choice (1-5): ").strip()
        
        if choice == '5':
            print("\n👋 Goodbye!")
            analyzer.disconnect()
            break
        elif choice == '1':
            analyze_market(analyzer, "HK_STOCKS", "HK Stocks (Quick)", max_stocks=100)
        elif choice == '2':
            analyze_market(analyzer, "US_STOCKS", "US Stocks (Quick)", max_stocks=100)
        elif choice == '3':
            confirm = input("\n⚠️ FULL analysis of ALL HK stocks (~5-8 min). Continue? (y/n): ")
            if confirm.lower() == 'y':
                show_all = input("📋 Show complete list? (y/n): ").lower() == 'y'
                analyze_market(analyzer, "HK_STOCKS", "HK Stocks (FULL)", max_stocks=None, show_all=show_all)
        elif choice == '4':
            confirm = input("\n⚠️ FULL analysis of ALL US stocks (~5-8 min). Continue? (y/n): ")
            if confirm.lower() == 'y':
                show_all = input("📋 Show complete list? (y/n): ").lower() == 'y'
                analyze_market(analyzer, "US_STOCKS", "US Stocks (FULL)", max_stocks=None, show_all=show_all)
        else:
            print("❌ Invalid choice")

def analyze_market(analyzer, market, market_name, max_stocks=None, show_all=False, min_volume=300000):
    try:
        print(f"\n📈 Analyzing {market_name}...")
        rising, falling = analyzer.analyze(
            market, 
            max_stocks=max_stocks, 
            top_n=20, 
            show_all=show_all,
            min_volume=min_volume
        )
        
        if rising is not None and not rising.empty:
            display_results(rising, falling, market_name)
        else:
            print(f"\n❌ No results found")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def display_results(rising, falling, title):
    """Simple result display"""
    print("\n" + "="*100)
    print(f"📊 {title}")
    print("="*100)
    
    if rising is not None and not rising.empty:
        print("\n🟢 TOP STOCKS LIKELY TO RISE:")
        print("-"*100)
        for idx, (_, row) in enumerate(rising.head(10).iterrows(), 1):
            signal = "🔥🔥" if row['Rise_Score'] >= 70 else ("🔥" if row['Rise_Score'] >= 60 else "✓")
            print(f"  {idx:2}. {row['Code']:10} | {row['Name'][:25]:25} | ${row['Price']:8.2f} | "
                  f"Rise:{row['Rise_Score']:3.0f}% | RSI:{row['RSI']:3.0f} | "
                  f"10D:{row['Return_10D']:+5.1f}% | {signal}")
    
    if falling is not None and not falling.empty:
        print("\n🔴 TOP STOCKS LIKELY TO FALL:")
        print("-"*100)
        for idx, (_, row) in enumerate(falling.head(10).iterrows(), 1):
            signal = "⚠️⚠️" if row['Fall_Score'] >= 70 else ("⚠️" if row['Fall_Score'] >= 60 else "▼")
            print(f"  {idx:2}. {row['Code']:10} | {row['Name'][:25]:25} | ${row['Price']:8.2f} | "
                  f"Fall:{row['Fall_Score']:3.0f}% | RSI:{row['RSI']:3.0f} | "
                  f"10D:{row['Return_10D']:+5.1f}% | {signal}")

if __name__ == "__main__":
    main()
