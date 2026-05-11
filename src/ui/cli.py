import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.analyzer import StockAnalyzer
from src.ui.display import Display
from src.models.market_enums import Market

def main():
    print("\n" + "="*60)
    print("  🚀 StockMiner - Professional Stock Analyzer")
    print("="*60)
    
    analyzer = StockAnalyzer()
    display = Display()
    
    while True:
        print("\n" + "="*60)
        print("📋 MAIN MENU")
        print("="*60)
        print("   ⚡ QUICK (~30 sec):")
        print("     1. Hong Kong Stocks - Quick (100 stocks)")
        print("     2. US Stocks - Quick (100 stocks)")
        print("")
        print("   🔍 FULL (~5-8 min):")
        print("     3. Hong Kong Stocks - FULL (All active)")
        print("     4. US Stocks - FULL (All active)")
        print("")
        print("   📊 ANALYSIS OPTIONS:")
        print("     5. Show complete summary")
        print("     6. List all analyzed stocks (from last run)")
        print("")
        print("   7. Exit")
        
        choice = input("\n👉 Choice (1-7): ").strip()
        
        if choice == '7':
            print("\n👋 Goodbye!")
            analyzer.disconnect()
            break
        
        elif choice == '1':
            rising, falling = analyzer.analyze("HK_STOCKS", max_stocks=100)
            if rising is not None:
                display.show_results(rising, falling, "Hong Kong Stocks (Quick)")
        
        elif choice == '2':
            rising, falling = analyzer.analyze("US_STOCKS", max_stocks=100)
            if rising is not None:
                display.show_results(rising, falling, "US Stocks (Quick)")
        
        elif choice == '3':
            confirm = input("\n⚠️ FULL analysis of ALL HK stocks (~5-8 min). Continue? (y/n): ")
            if confirm.lower() == 'y':
                show_all = input("📋 Show complete list of all analyzed stocks? (y/n): ").lower() == 'y'
                rising, falling = analyzer.analyze("HK_STOCKS", max_stocks=None, show_all=show_all)
                if rising is not None:
                    display.show_results(rising, falling, "Hong Kong Stocks (FULL)")
        
        elif choice == '4':
            confirm = input("\n⚠️ FULL analysis of ALL US stocks (~5-8 min). Continue? (y/n): ")
            if confirm.lower() == 'y':
                show_all = input("📋 Show complete list of all analyzed stocks? (y/n): ").lower() == 'y'
                rising, falling = analyzer.analyze("US_STOCKS", max_stocks=None, show_all=show_all)
                if rising is not None:
                    display.show_results(rising, falling, "US Stocks (FULL)")
        
        elif choice == '5':
            analyzer.show_summary()
        
        elif choice == '6':
            analyzer.show_all_analyzed_stocks()
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
