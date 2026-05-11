#!/usr/bin/env python
"""
StockMiner - Hybrid Stock Analyzer with Caching
Efficient stock analysis with local data storage
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.analyzer_hybrid import HybridAnalyzer

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header():
    print("\n" + "="*70)
    print("  🚀 STOCKMINER - Hybrid Stock Analyzer")
    print("  Efficient Caching + Delta Updates")
    print("="*70)
    print("\n  ✅ Stock lists: Dynamic from Futu")
    print("  ✅ Historical data: Yahoo Finance (cached locally)")
    print("  ✅ Smart caching: Only downloads new data")

def main():
    clear_screen()
    print_header()
    
    analyzer = HybridAnalyzer()
    
    # Show cache status on startup
    analyzer.show_cache_stats()
    
    while True:
        print("\n" + "="*70)
        print("📋 MAIN MENU")
        print("="*70)
        print("   ⚡ QUICK ANALYSIS (~1-2 min):")
        print("     1. Hong Kong Stocks - Quick (100 stocks)")
        print("     2. US Stocks - Quick (100 stocks)")
        print("")
        print("   🔍 FULL ANALYSIS (~3-5 min first time, faster after):")
        print("     3. Hong Kong Stocks - FULL (All active)")
        print("     4. US Stocks - FULL (All active)")
        print("")
        print("   🗃️  CACHE MANAGEMENT:")
        print("     5. Show cache statistics")
        print("     6. Clear cache (force refresh)")
        print("")
        print("   7. Exit")
        print("="*70)
        
        choice = input("\n👉 Enter choice (1-7): ").strip()
        
        if choice == '7':
            print("\n👋 Saving cache and exiting...")
            analyzer.disconnect()
            print("Goodbye!")
            break
        
        elif choice == '1':
            print("\n📈 Quick Analysis: Hong Kong Stocks...")
            rising, falling = analyzer.analyze(
                "HK_STOCKS", 
                max_stocks=100,
                top_n=15,
                show_all=False,
                min_volume=200000
            )
        
        elif choice == '2':
            print("\n📈 Quick Analysis: US Stocks...")
            rising, falling = analyzer.analyze(
                "US_STOCKS", 
                max_stocks=100,
                top_n=15,
                show_all=False,
                min_volume=500000
            )
        
        elif choice == '3':
            confirm = input("\n⚠️  FULL analysis of ALL HK stocks. Continue? (y/n): ")
            if confirm.lower() == 'y':
                force = input("🔄 Force refresh all data? (y/n - will use cache if available): ").lower() == 'y'
                rising, falling = analyzer.analyze(
                    "HK_STOCKS", 
                    max_stocks=None,
                    top_n=20,
                    show_all=False,
                    min_volume=200000,
                    force_refresh=force
                )
        
        elif choice == '4':
            confirm = input("\n⚠️  FULL analysis of ALL US stocks. Continue? (y/n): ")
            if confirm.lower() == 'y':
                force = input("🔄 Force refresh all data? (y/n - will use cache if available): ").lower() == 'y'
                rising, falling = analyzer.analyze(
                    "US_STOCKS", 
                    max_stocks=None,
                    top_n=20,
                    show_all=False,
                    min_volume=500000,
                    force_refresh=force
                )
        
        elif choice == '5':
            analyzer.show_cache_stats()
        
        elif choice == '6':
            confirm = input("\n⚠️  This will clear all cached data. Continue? (y/n): ")
            if confirm.lower() == 'y':
                analyzer.clear_cache()
        
        else:
            print("❌ Invalid choice. Please enter 1-7.")
        
        input("\nPress Enter to continue...")
        clear_screen()
        print_header()
        analyzer.show_cache_stats()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Program interrupted by user")
        print("Saving cache...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
