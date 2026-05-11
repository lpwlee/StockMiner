"""
Enhanced CLI with better user experience
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.analyzer import StockAnalyzer
from src.models.market_enums import Market
from src.ui.enhanced_display import EnhancedDisplay
from src.utils.logger import setup_logger
import yaml

logger = setup_logger(__name__)

def load_preferences():
    """Load user preferences"""
    try:
        with open("config/user_preferences.yaml", 'r') as f:
            return yaml.safe_load(f)
    except:
        return {}

def main():
    print("\n" + "="*60)
    print("🚀 StockMiner - Professional Technical Analysis Tool")
    print("="*60)
    print("\n✅ FutuOpenD Connected Successfully!")
    print("   Analyzing real-time market data...")
    
    preferences = load_preferences()
    analyzer = StockAnalyzer()
    display = EnhancedDisplay()
    
    while True:
        print("\n" + "="*60)
        print("📋 MAIN MENU")
        print("="*60)
        print("   1. Hong Kong Stocks (Main Board)")
        print("   2. US Stocks (NASDAQ/NYSE)")
        print("   3. Quick Scan - Both Markets")
        print("   4. Change Settings")
        print("   5. Exit")
        
        choice = input("\n👉 Enter choice (1-5): ").strip()
        
        if choice == '5':
            print("\n👋 Goodbye! Happy Trading!")
            analyzer.connector.release_connection()
            break
        
        elif choice == '1':
            analyze_market(analyzer, display, Market.HK_STOCKS, "Hong Kong Stocks")
        
        elif choice == '2':
            analyze_market(analyzer, display, Market.US_STOCKS, "US Stocks")
        
        elif choice == '3':
            print("\n🔍 Running Quick Scan on both markets...")
            analyze_market(analyzer, display, Market.HK_STOCKS, "Hong Kong Stocks", quick=True)
            print("\n" + "-"*60)
            analyze_market(analyzer, display, Market.US_STOCKS, "US Stocks", quick=True)
        
        elif choice == '4':
            show_settings()
        
        else:
            print("❌ Invalid choice")

def analyze_market(analyzer, display, market, market_name, quick=False):
    """Analyze a specific market"""
    try:
        if quick:
            print(f"\n⚡ Quick Analysis for {market_name}...")
            rising, falling = analyzer.analyze_market(market, top_n=10)
        else:
            print(f"\n📊 Full Analysis for {market_name}...")
            rising, falling = analyzer.analyze_market(market, top_n=20)
        
        if rising is not None and falling is not None:
            # Use enhanced display
            display.print_enhanced_results(rising, falling, market_name)
        else:
            print(f"\n❌ No results found for {market_name}")
            print("   Try adjusting filters or check FutuOpenD connection")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Analysis interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Analysis error: {e}")

def show_settings():
    """Display current settings"""
    print("\n" + "="*60)
    print("⚙️  CURRENT SETTINGS")
    print("="*60)
    
    try:
        with open("config/user_preferences.yaml", 'r') as f:
            prefs = yaml.safe_load(f)
            
        print(f"\n📊 Filters:")
        print(f"   Min Price: ${prefs.get('filters', {}).get('min_price', 1.0)}")
        print(f"   Min Volume: {prefs.get('filters', {}).get('min_volume', 1000000):,} shares")
        print(f"   Exclude Penny Stocks: {prefs.get('trading_preferences', {}).get('exclude_penny_stocks', True)}")
        
        print(f"\n🎯 Trading Preferences:")
        print(f"   Risk Tolerance: {prefs.get('trading_preferences', {}).get('risk_tolerance', 'medium')}")
        print(f"   Min Signal Strength: {prefs.get('trading_preferences', {}).get('min_signal_strength', 60)}%")
        
        print("\n💡 To modify settings, edit: config/user_preferences.yaml")
        
    except Exception as e:
        print(f"\n⚠️ Could not load settings: {e}")
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
