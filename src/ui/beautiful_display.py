"""
Beautiful display formatter for stock analysis results
"""

from datetime import datetime
import pandas as pd

class BeautifulDisplay:
    """Professional display formatter for stock analysis"""
    
    @staticmethod
    def print_header(title, total_stocks):
        """Print analysis header"""
        print("\n" + "="*100)
        print(f"  {title}")
        print("="*100)
        print(f"  📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  📊 Total Stocks Analyzed: {total_stocks:,}")
        print("="*100)
    
    @staticmethod
    def print_rising_stocks(rising_df, title="🟢 TOP 20 RISING STOCKS (Strong Buy Signals)"):
        """Print beautifully formatted rising stocks table"""
        if rising_df is None or rising_df.empty:
            print("\n⚠️ No rising stocks found")
            return
        
        print(f"\n{'='*100}")
        print(f"  {title}")
        print(f"{'='*100}")
        
        # Header
        print(f"\n{'#':<4} {'Code':<12} {'Company Name':<35} {'Price':<10} {'Rise%':<7} {'RSI':<7} {'10D%':<9} {'Volume':<8} {'Signal'}")
        print(f"{'-'*100}")
        
        # Display top 20 rising stocks
        for idx, (_, row) in enumerate(rising_df.head(20).iterrows(), 1):
            # Determine signal strength based on Rise Score
            if row['Rise_Score'] >= 75:
                signal = "🔴🔴 EXTREME"
                signal_color = "🔥🔥🔥"
            elif row['Rise_Score'] >= 70:
                signal = "🟢 STRONG"
                signal_color = "🔥🔥"
            elif row['Rise_Score'] >= 60:
                signal = "📈 MODERATE"
                signal_color = "🔥"
            else:
                signal = "👀 WATCH"
                signal_color = "✓"
            
            # Format price
            price = row['Price']
            if price >= 1000:
                price_str = f"{price:,.0f}"
            elif price >= 1:
                price_str = f"{price:.2f}"
            else:
                price_str = f"{price:.4f}"
            
            # Format company name (truncate if too long)
            name = row['Name'][:33] if len(row['Name']) > 33 else row['Name']
            
            # Determine RSI status
            rsi = row['RSI']
            if rsi < 30:
                rsi_status = "🔥 OVERSOLD"
            elif rsi > 70:
                rsi_status = "⚠️ OVERBOUGHT"
            else:
                rsi_status = "⚪ NEUTRAL"
            
            # Volume ratio indicator
            vol_ratio = row.get('Volume_Ratio', 1)
            if vol_ratio > 2:
                vol_signal = f"{vol_ratio:.1f}x 🔥"
            elif vol_ratio > 1.5:
                vol_signal = f"{vol_ratio:.1f}x ↑"
            elif vol_ratio < 0.5:
                vol_signal = f"{vol_ratio:.1f}x ↓"
            else:
                vol_signal = f"{vol_ratio:.1f}x"
            
            print(f"{idx:<4} {row['Code']:<12} {name:<35} ${price_str:<9} "
                  f"{row['Rise_Score']:<7.0f} {rsi:<7.0f} "
                  f"{row['Return_10D']:+6.1f}% {vol_signal:<8} {signal_color:<10}")
        
        # Add summary statistics for rising stocks
        print(f"\n{'─'*100}")
        print(f"  📊 Rising Stocks Summary:")
        print(f"     • Average Rise Score: {rising_df['Rise_Score'].head(20).mean():.1f}%")
        print(f"     • Average RSI: {rising_df['RSI'].head(20).mean():.1f}")
        print(f"     • Average 10D Return: {rising_df['Return_10D'].head(20).mean():+.1f}%")
        print(f"     • Best Performer: {rising_df.iloc[0]['Code']} ({rising_df.iloc[0]['Name'][:30]}) - Rise: {rising_df.iloc[0]['Rise_Score']:.0f}%")
    
    @staticmethod
    def print_falling_stocks(falling_df, title="🔴 TOP 20 FALLING STOCKS (Strong Sell Signals)"):
        """Print beautifully formatted falling stocks table"""
        if falling_df is None or falling_df.empty:
            print("\n⚠️ No falling stocks found")
            return
        
        print(f"\n{'='*100}")
        print(f"  {title}")
        print(f"{'='*100}")
        
        # Header
        print(f"\n{'#':<4} {'Code':<12} {'Company Name':<35} {'Price':<10} {'Fall%':<7} {'RSI':<7} {'10D%':<9} {'Volume':<8} {'Signal'}")
        print(f"{'-'*100}")
        
        # Display top 20 falling stocks
        for idx, (_, row) in enumerate(falling_df.head(20).iterrows(), 1):
            # Determine signal strength based on Fall Score
            if row['Fall_Score'] >= 75:
                signal = "🔴🔴 EXTREME"
                signal_color = "⚠️⚠️⚠️"
            elif row['Fall_Score'] >= 70:
                signal = "🔴 STRONG"
                signal_color = "⚠️⚠️"
            elif row['Fall_Score'] >= 60:
                signal = "📉 MODERATE"
                signal_color = "⚠️"
            else:
                signal = "👀 WATCH"
                signal_color = "▼"
            
            # Format price
            price = row['Price']
            if price >= 1000:
                price_str = f"{price:,.0f}"
            elif price >= 1:
                price_str = f"{price:.2f}"
            else:
                price_str = f"{price:.4f}"
            
            # Format company name
            name = row['Name'][:33] if len(row['Name']) > 33 else row['Name']
            
            # Determine RSI status
            rsi = row['RSI']
            if rsi > 70:
                rsi_status = "⚠️ OVERBOUGHT"
            elif rsi < 30:
                rsi_status = "🔥 OVERSOLD"
            else:
                rsi_status = "⚪ NEUTRAL"
            
            # Volume ratio indicator
            vol_ratio = row.get('Volume_Ratio', 1)
            if vol_ratio > 2:
                vol_signal = f"{vol_ratio:.1f}x 🔥"
            elif vol_ratio > 1.5:
                vol_signal = f"{vol_ratio:.1f}x ↑"
            else:
                vol_signal = f"{vol_ratio:.1f}x"
            
            print(f"{idx:<4} {row['Code']:<12} {name:<35} ${price_str:<9} "
                  f"{row['Fall_Score']:<7.0f} {rsi:<7.0f} "
                  f"{row['Return_10D']:+6.1f}% {vol_signal:<8} {signal_color:<10}")
        
        # Add summary statistics for falling stocks
        print(f"\n{'─'*100}")
        print(f"  📊 Falling Stocks Summary:")
        print(f"     • Average Fall Score: {falling_df['Fall_Score'].head(20).mean():.1f}%")
        print(f"     • Average RSI: {falling_df['RSI'].head(20).mean():.1f}")
        print(f"     • Average 10D Return: {falling_df['Return_10D'].head(20).mean():+.1f}%")
        print(f"     • Worst Performer: {falling_df.iloc[0]['Code']} ({falling_df.iloc[0]['Name'][:30]}) - Fall: {falling_df.iloc[0]['Fall_Score']:.0f}%")
    
    @staticmethod
    def print_market_summary(df, total_stocks, successful_analysis):
        """Print overall market summary"""
        print(f"\n{'='*100}")
        print(f"  📈 MARKET SUMMARY")
        print(f"{'='*100}")
        
        if df is None or df.empty:
            print("  No data available")
            return
        
        # Calculate key metrics
        bullish = len(df[df['Rise_Score'] > df['Fall_Score']])
        bearish = len(df[df['Fall_Score'] > df['Rise_Score']])
        neutral = len(df) - bullish - bearish
        
        avg_rsi = df['RSI'].mean()
        avg_rise = df['Rise_Score'].mean()
        avg_fall = df['Fall_Score'].mean()
        avg_return = df['Return_10D'].mean()
        
        # Find extremes
        most_oversold = df.loc[df['RSI'].idxmin()]
        most_overbought = df.loc[df['RSI'].idxmax()]
        best_performer = df.loc[df['Return_10D'].idxmax()]
        worst_performer = df.loc[df['Return_10D'].idxmin()]
        
        print(f"\n  📊 Market Sentiment:")
        print(f"     • Bullish Signals: {bullish} ({bullish/len(df)*100:.1f}%)")
        print(f"     • Bearish Signals: {bearish} ({bearish/len(df)*100:.1f}%)")
        print(f"     • Neutral Signals: {neutral} ({neutral/len(df)*100:.1f}%)")
        
        print(f"\n  📈 Average Metrics:")
        print(f"     • Average RSI: {avg_rsi:.1f}")
        print(f"     • Average Rise Score: {avg_rise:.1f}%")
        print(f"     • Average Fall Score: {avg_fall:.1f}%")
        print(f"     • Average 10-Day Return: {avg_return:+.1f}%")
        
        print(f"\n  🎯 Extreme Cases:")
        print(f"     • Most Oversold: {most_oversold['Code']} ({most_oversold['Name'][:30]}) - RSI: {most_oversold['RSI']:.1f}")
        print(f"     • Most Overbought: {most_overbought['Code']} ({most_overbought['Name'][:30]}) - RSI: {most_overbought['RSI']:.1f}")
        print(f"     • Best 10-Day Performer: {best_performer['Code']} ({best_performer['Name'][:30]}) - Return: {best_performer['Return_10D']:+.1f}%")
        print(f"     • Worst 10-Day Performer: {worst_performer['Code']} ({worst_performer['Name'][:30]}) - Return: {worst_performer['Return_10D']:+.1f}%")
    
    @staticmethod
    def print_trading_recommendations(rising_df, falling_df):
        """Print actionable trading recommendations"""
        print(f"\n{'='*100}")
        print(f"  💡 ACTIONABLE TRADING RECOMMENDATIONS")
        print(f"{'='*100}")
        
        if rising_df is not None and not rising_df.empty:
            top_buy = rising_df.iloc[0]
            print(f"\n  ✅ TOP BUY RECOMMENDATION:")
            print(f"     • Stock: {top_buy['Code']} - {top_buy['Name'][:40]}")
            print(f"     • Current Price: ${top_buy['Price']:.2f}")
            print(f"     • Rise Probability: {top_buy['Rise_Score']:.0f}%")
            print(f"     • RSI: {top_buy['RSI']:.0f} (Oversold < 30 is best)")
            print(f"     • Recent Performance: {top_buy['Return_10D']:+.1f}% in 10 days")
            if top_buy.get('Volume_Ratio', 0) > 1.5:
                print(f"     • Volume: {top_buy['Volume_Ratio']:.1f}x average (High volume confirmation)")
            
            print(f"\n     🎯 Suggested Strategy:")
            print(f"     • Entry: Market price")
            print(f"     • Stop Loss: ${top_buy['Price'] * 0.93:.2f} (-7%)")
            print(f"     • Target 1: ${top_buy['Price'] * 1.10:.2f} (+10%)")
            print(f"     • Target 2: ${top_buy['Price'] * 1.15:.2f} (+15%)")
        
        if falling_df is not None and not falling_df.empty:
            top_sell = falling_df.iloc[0]
            print(f"\n  ❌ TOP SELL/SHORT RECOMMENDATION:")
            print(f"     • Stock: {top_sell['Code']} - {top_sell['Name'][:40]}")
            print(f"     • Current Price: ${top_sell['Price']:.2f}")
            print(f"     • Fall Probability: {top_sell['Fall_Score']:.0f}%")
            print(f"     • RSI: {top_sell['RSI']:.0f} (Overbought > 70 is best)")
            print(f"     • Recent Performance: {top_sell['Return_10D']:+.1f}% in 10 days")
            
            print(f"\n     🎯 Suggested Strategy:")
            print(f"     • Action: Take profits or consider short position")
            print(f"     • Stop Loss: ${top_sell['Price'] * 1.07:.2f} (+7%)")
            print(f"     • Target 1: ${top_sell['Price'] * 0.90:.2f} (-10%)")
            print(f"     • Target 2: ${top_sell['Price'] * 0.85:.2f} (-15%)")
        
        print(f"\n{'─'*100}")
        print(f"  ⚠️ RISK WARNINGS:")
        print(f"     • This is technical analysis only - not financial advice")
        print(f"     • Always use stop-loss orders to manage risk")
        print(f"     • Consider position sizing: 1-3% of portfolio per trade")
        print(f"     • Oversold can stay oversold; wait for confirmation signals")
    
    @staticmethod
    def print_footer():
        """Print footer with disclaimers"""
        print(f"\n{'='*100}")
        print(f"  📌 DISCLAIMER")
        print(f"{'='*100}")
        print(f"  This analysis is based on technical indicators and historical data only.")
        print(f"  Past performance does not guarantee future results.")
        print(f"  Always conduct your own research before making investment decisions.")
        print(f"  Data sources: Futu (stock lists) & Yahoo Finance (historical data)")
        print(f"{'='*100}\n")

def display_comprehensive_analysis(df, rising_df, falling_df, title, total_stocks):
    """Main function to display comprehensive analysis"""
    display = BeautifulDisplay()
    
    display.print_header(title, total_stocks)
    
    if rising_df is not None and not rising_df.empty:
        display.print_rising_stocks(rising_df)
    
    if falling_df is not None and not falling_df.empty:
        display.print_falling_stocks(falling_df)
    
    display.print_market_summary(df, total_stocks, len(df))
    display.print_trading_recommendations(rising_df, falling_df)
    display.print_footer()
