"""
Enhanced display with better formatting and analysis
"""

import pandas as pd
from datetime import datetime
from typing import Tuple

class EnhancedDisplay:
    """Enhanced display with color coding and better formatting"""
    
    @staticmethod
    def print_enhanced_results(rising: pd.DataFrame, falling: pd.DataFrame, market_name: str):
        """Print enhanced analysis results"""
        
        print("\n" + "="*100)
        print(f"📊 ENHANCED ANALYSIS REPORT - {market_name}")
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*100)
        
        # Summary Statistics
        if rising is not None and not rising.empty:
            print("\n📈 SUMMARY STATISTICS:")
            print(f"   Total Rising Candidates: {len(rising)}")
            print(f"   Average Rise Score: {rising['Rise_Score'].mean():.1f}%")
            print(f"   Average RSI (Rising): {rising['RSI'].mean():.1f}")
            print(f"   Average 10-Day Return: {rising['Return_10D'].mean():+.1f}%")
        
        if falling is not None and not falling.empty:
            print(f"   Total Falling Candidates: {len(falling)}")
            print(f"   Average Fall Score: {falling['Fall_Score'].mean():.1f}%")
            print(f"   Average RSI (Falling): {falling['RSI'].mean():.1f}")
            print(f"   Average 10-Day Return: {falling['Return_10D'].mean():+.1f}%")
        
        # Strong Buy Signals (High confidence)
        if rising is not None and not rising.empty:
            strong_buy = rising[rising['Rise_Score'] >= 70]
            if not strong_buy.empty:
                print("\n🔥 STRONG BUY SIGNALS (Rise Score ≥ 70%):")
                print("-"*100)
                for _, row in strong_buy.iterrows():
                    rsi_status = "OVERSOLD" if row['RSI'] < 30 else "NEUTRAL" if row['RSI'] < 70 else "OVERBOUGHT"
                    print(f"   {row['Code']:12} | Price: ${row['Current_Price']:8.2f} | "
                          f"Rise: {row['Rise_Score']:5.1f}% | RSI: {row['RSI']:5.1f} ({rsi_status}) | "
                          f"10D: {row['Return_10D']:+6.1f}%")
        
        # Strong Sell Signals
        if falling is not None and not falling.empty:
            strong_sell = falling[falling['Fall_Score'] >= 70]
            if not strong_sell.empty:
                print("\n⚠️  STRONG SELL SIGNALS (Fall Score ≥ 70%):")
                print("-"*100)
                for _, row in strong_sell.iterrows():
                    rsi_status = "OVERBOUGHT" if row['RSI'] > 70 else "NEUTRAL" if row['RSI'] > 30 else "OVERSOLD"
                    print(f"   {row['Code']:12} | Price: ${row['Current_Price']:8.2f} | "
                          f"Fall: {row['Fall_Score']:5.1f}% | RSI: {row['RSI']:5.1f} ({rsi_status}) | "
                          f"10D: {row['Return_10D']:+6.1f}%")
        
        # Volume Surge Detection
        if rising is not None and not rising.empty:
            high_volume = rising[rising['Volume_Ratio'] > 1.5]
            if not high_volume.empty:
                print("\n📊 HIGH VOLUME ALERTS (Volume > 1.5x average):")
                print("-"*100)
                for _, row in high_volume.iterrows():
                    print(f"   {row['Code']:12} | Volume Ratio: {row['Volume_Ratio']:.2f}x | "
                          f"10D Return: {row['Return_10D']:+6.1f}% | RSI: {row['RSI']:.1f}")
        
        # Risk Warnings
        print("\n⚠️  RISK WARNINGS:")
        print("-"*100)
        
        # Penny stocks (price < $1 HKD)
        if rising is not None:
            penny_stocks = rising[rising['Current_Price'] < 1.0]
            if not penny_stocks.empty:
                print(f"   🚨 Penny Stocks (<$1): {', '.join(penny_stocks['Code'].tolist())} - Higher risk")
        
        check_and_print("📉 Low Volume Stocks", rising, falling, 'Volume_Ratio', '<', 0.5)
        check_and_print("📈 Extreme RSI (Overbought)", falling, rising, 'RSI', '>', 80)
        check_and_print("📉 Extreme RSI (Oversold)", rising, falling, 'RSI', '<', 20)
        
        # Trading Recommendation Summary
        print("\n" + "="*100)
        print("💡 TRADING RECOMMENDATIONS:")
        print("="*100)
        
        if rising is not None and not rising.empty:
            best_rise = rising.iloc[0]
            print(f"\n   ✅ BEST BUY OPPORTUNITY: {best_rise['Code']}")
            print(f"      - Rise Probability: {best_rise['Rise_Score']:.1f}%")
            print(f"      - Current Price: ${best_rise['Current_Price']:.2f}")
            print(f"      - RSI: {best_rise['RSI']:.1f} ({'Oversold - Good entry' if best_rise['RSI'] < 30 else 'Neutral'})")
            print(f"      - Recent Performance: {best_rise['Return_10D']:+.1f}% in 10 days")
        
        if falling is not None and not falling.empty:
            best_fall = falling.iloc[0]
            print(f"\n   ❌ BEST SHORT OPPORTUNITY: {best_fall['Code']}")
            print(f"      - Fall Probability: {best_fall['Fall_Score']:.1f}%")
            print(f"      - Current Price: ${best_fall['Current_Price']:.2f}")
            print(f"      - RSI: {best_fall['RSI']:.1f} ({'Overbought - Good short entry' if best_fall['RSI'] > 70 else 'Neutral'})")
            print(f"      - Recent Performance: {best_fall['Return_10D']:+.1f}% in 10 days")

def check_and_print(title, primary_df, secondary_df, column, operator, threshold):
    """Helper function to check and print conditions"""
    items = []
    
    if primary_df is not None and not primary_df.empty:
        if operator == '<':
            mask = primary_df[column] < threshold
        elif operator == '>':
            mask = primary_df[column] > threshold
        else:
            return
        
        items.extend(primary_df[mask]['Code'].tolist())
    
    if secondary_df is not None and not secondary_df.empty:
        if operator == '<':
            mask = secondary_df[column] < threshold
        elif operator == '>':
            mask = secondary_df[column] > threshold
        else:
            return
        
        items.extend(secondary_df[mask]['Code'].tolist())
    
    if items:
        print(f"   {title}: {', '.join(items)}")

if __name__ == "__main__":
    # Test with sample data
    sample_rising = pd.DataFrame({
        'Code': ['HK.00005', 'HK.00013'],
        'Current_Price': [139.70, 20.66],
        'Rise_Score': [75, 65],
        'RSI': [18.2, 13.1],
        'Return_10D': [-13.0, -5.6],
        'Volume_Ratio': [1.2, 0.8],
        'Fall_Score': [40, 58]
    })
    
    sample_falling = pd.DataFrame({
        'Code': ['HK.00012', 'HK.00017'],
        'Current_Price': [33.86, 9.55],
        'Fall_Score': [75, 75],
        'RSI': [81.1, 71.0],
        'Return_10D': [11.5, 13.4],
        'Volume_Ratio': [1.8, 2.1],
        'Rise_Score': [30, 35]
    })
    
    EnhancedDisplay.print_enhanced_results(sample_rising, sample_falling, "Hong Kong Stocks (Sample)")
