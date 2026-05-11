#!/usr/bin/env python
"""
Launch the StockMiner Interactive Dashboard
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.ui.dashboard import StockDashboard

def main():
    print("\n" + "="*60)
    print("  📊 StockMiner Interactive Dashboard")
    print("  Candlestick Charts + Technical Analysis")
    print("="*60)
    print("\n  Features:")
    print("  • Real-time candlestick charts")
    print("  • Buy/Sell signal filtering")
    print("  • Technical indicators (SMA, RSI, Volume)")
    print("  • Interactive stock selection")
    print("  • Comprehensive stock analysis")
    print("\n" + "="*60)
    
    dashboard = StockDashboard()
    
    try:
        dashboard.run(port=8050)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down dashboard...")
        dashboard.stop()
        print("Goodbye!")

if __name__ == "__main__":
    main()
