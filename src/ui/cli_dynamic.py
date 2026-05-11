"""
CLI with dynamic company name loading - CORRECTED VERSION
Properly distinguishes between Quick and Full analysis
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.analyzer_dynamic import StockAnalyzerDynamic
from src.models.market_enums import Market
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def print_banner():
    """Print application banner"""
    print("\n" + "="*60)
    print("  🚀 StockMiner - Professional Technical Analysis Tool")
    print("  Dynamic Edition - Real-time Company Names")
    print("="*60)
    print("\n  ✅ Connected to FutuOpenD")
    print("  📊 Real-time market data analysis")
    print("  🔄 Dynamic company name fetching from API")
    print("  ⚡ Automatic rate limiting to respect Futu API limits")

def main():
    print_banner()
    
    analyzer = StockAnalyzerDynamic()
    
    while True:
        print("\n" + "="*60)
        print("📋 MAIN MENU")
        print("="*60)
        print("   ⚡ QUICK ANALYSIS (~30 seconds):")
        print("     1. Hong Kong Stocks - Quick (100 stocks)")
        print("     2. US Stocks - Quick (100 stocks)")
        print("")
        print("   🔍 FULL ANALYSIS (~5-8 minutes):")
        print("     3. Hong Kong Stocks - FULL (ALL 1000+ active stocks)")
        print("     4. US Stocks - FULL (ALL active stocks)")
        print("")
        print("   🛠️  OTHER OPTIONS:")
        print("     5. Clear Name Cache")
        print("     6. Exit")
        
        choice = input("\n👉 Enter choice (1-6): ").strip()
        
        if choice == '6':
            print("\n👋 Thank you for using StockMiner!")
            analyzer.connector.release_connection()
            break
        
        elif choice == '1':
            print("\n⚡ QUICK ANALYSIS MODE: Analyzing 100 HK stocks...")
            analyze_market(analyzer, Market.HK_STOCKS, "Hong Kong Stocks (Quick)", max_stocks=100)
        
        elif choice == '2':
            print("\n⚡ QUICK ANALYSIS MODE: Analyzing 100 US stocks...")
            analyze_market(analyzer, Market.US_STOCKS, "US Stocks (Quick)", max_stocks=100)
        
        elif choice == '3':
            print("\n🔍 FULL ANALYSIS MODE SELECTED")
            confirm = input("⚠️  This will analyze ALL 1000+ active HK stocks (~5-8 min). Continue? (y/n): ")
            if confirm.lower() == 'y':
                analyze_market(analyzer, Market.HK_STOCKS, "Hong Kong Stocks (FULL)", max_stocks=None)
            else:
                print("   Cancelled. Returning to menu.")
        
        elif choice == '4':
            print("\n🔍 FULL ANALYSIS MODE SELECTED")
            confirm = input("⚠️  This will analyze ALL active US stocks (~5-8 min). Continue? (y/n): ")
            if confirm.lower() == 'y':
                analyze_market(analyzer, Market.US_STOCKS, "US Stocks (FULL)", max_stocks=None)
            else:
                print("   Cancelled. Returning to menu.")
        
        elif choice == '5':
            analyzer.connector.clear_name_cache()
            print("\n✅ Name cache cleared. Next analysis will fetch fresh names from API.")
        
        else:
            print("❌ Invalid choice. Please enter 1-6.")

def analyze_market(analyzer, market, market_name, max_stocks=None):
    """Analyze a specific market"""
    try:
        print(f"\n📈 Analyzing {market_name}...")
        
        rising, falling = analyzer.analyze_market(market, top_n=20, max_stocks=max_stocks)
        
        if rising is not None and falling is not None:
            analyzer.display_dynamic_results(rising, falling, market_name)
            
            # Show summary of what was analyzed
            if max_stocks:
                print(f"\n📊 Note: Quick analysis complete. Only {max_stocks} stocks were analyzed.")
                print("   For comprehensive results covering ALL active stocks, use FULL Analysis option (3 or 4).")
            else:
                print(f"\n📊 Full analysis complete. ALL active stocks were analyzed for comprehensive results.")
            
        else:
            print(f"\n❌ No results found for {market_name}")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Analysis error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
