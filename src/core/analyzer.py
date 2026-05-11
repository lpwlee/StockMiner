import pandas as pd
from datetime import datetime, timedelta
import time
import os

from src.connectors.futu_client import FutuClient
from src.core.stock_scanner import StockScanner
from src.indicators.technical import calculate_indicators
from src.indicators.scorer import calculate_scores
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class StockAnalyzer:
    def __init__(self):
        self.client = FutuClient()
        self.scanner = StockScanner(self.client)
        self.all_results = []
        self.last_analysis_time = None
        self.last_market = None
        self.min_history_days = 20  # Reduced from 50 to 20 days
    
    def analyze(self, market, max_stocks=None, top_n=20, show_all=False):
        logger.info(f"Analyzing {market}")
        
        # Reset results for new analysis
        self.all_results = []
        self.last_market = market
        self.last_analysis_time = datetime.now()
        
        # Get active stocks
        stock_list = self.scanner.scan_active_stocks(market, max_stocks)
        if not stock_list:
            return None, None
        
        mode = "QUICK" if max_stocks else "FULL"
        total_to_analyze = len(stock_list)
        print(f"\n📊 {mode} MODE: Analyzing {total_to_analyze} stocks...")
        print(f"   Minimum historical data required: {self.min_history_days} days")
        
        # Get names
        names = self.client.get_stock_names(stock_list)
        
        # Analyze each stock
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        failed_count = 0
        insufficient_data_count = 0
        
        for i, code in enumerate(stock_list):
            print(f"\r   Progress: {i+1}/{total_to_analyze} - {code} (Analyzed: {len(self.all_results)})", end="", flush=True)
            
            # Get historical data
            data = self.client.get_history_kline(code, start_date.strftime('%Y-%m-%d'), 
                                                  end_date.strftime('%Y-%m-%d'))
            
            if data.empty:
                failed_count += 1
                continue
            
            if len(data) < self.min_history_days:
                insufficient_data_count += 1
                continue
            
            # Calculate indicators and scores
            try:
                indicators = calculate_indicators(data)
                rise_score, fall_score, reasoning = calculate_scores(indicators)
                
                result = {
                    'Code': code,
                    'Name': names.get(code, code.split('.')[-1]),
                    'Price': indicators.get('price', 0),
                    'Rise_Score': rise_score,
                    'Fall_Score': fall_score,
                    'RSI': indicators.get('rsi', 50),
                    'Return_10D': indicators.get('return_10d', 0),
                    'Return_20D': indicators.get('return_20d', 0),
                    'Volume_Ratio': indicators.get('volume_ratio', 1),
                    'Reasoning': reasoning,
                    'Net_Score': rise_score - fall_score
                }
                self.all_results.append(result)
            except Exception as e:
                logger.debug(f"Error processing {code}: {e}")
                continue
            
            time.sleep(0.05)
        
        print(f"\n   ✅ Analysis Complete!")
        print(f"   📊 Successfully analyzed: {len(self.all_results)} stocks")
        print(f"   ⚠️  Insufficient data (<{self.min_history_days} days): {insufficient_data_count} stocks")
        print(f"   ❌ Failed to fetch: {failed_count} stocks")
        print(f"   📈 Total active stocks: {total_to_analyze}")
        
        if not self.all_results:
            print("❌ No stocks were successfully analyzed")
            return None, None
        
        # Create DataFrame from ALL results
        df = pd.DataFrame(self.all_results)
        
        # Show all analyzed stocks if requested
        if show_all:
            self.show_all_analyzed_stocks()
        
        # Calculate and display statistics from ALL analyzed stocks
        self.show_complete_statistics()
        
        # Save complete results to CSV
        self.save_complete_results(df, market, mode)
        
        # Get top rising and falling for display
        rising = df[df['Net_Score'] > 0].nlargest(top_n, 'Net_Score')
        falling = df[df['Net_Score'] < 0].nsmallest(top_n, 'Net_Score')
        
        return rising, falling
    
    def show_complete_statistics(self):
        """Display statistics from ALL analyzed stocks"""
        if not self.all_results:
            print("\n⚠️ No analysis data available")
            return
        
        df = pd.DataFrame(self.all_results)
        
        print("\n" + "="*70)
        print("📊 COMPLETE ANALYSIS STATISTICS")
        print("="*70)
        print(f"  Analysis Time: {self.last_analysis_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Market: {self.last_market}")
        print(f"  {'='*66}")
        print(f"  Total Stocks Analyzed: {len(df)}")
        print(f"  Average RSI: {df['RSI'].mean():.1f}")
        print(f"  Average Rise Score: {df['Rise_Score'].mean():.1f}")
        print(f"  Average Fall Score: {df['Fall_Score'].mean():.1f}")
        print(f"  Average 10D Return: {df['Return_10D'].mean():+.1f}%")
        print(f"  Average 20D Return: {df['Return_20D'].mean():+.1f}%")
        print(f"  Average Volume Ratio: {df['Volume_Ratio'].mean():.2f}x")
        print(f"  {'='*66}")
        
        bullish = len(df[df['Rise_Score'] > df['Fall_Score']])
        bearish = len(df[df['Fall_Score'] > df['Rise_Score']])
        neutral = len(df[df['Rise_Score'] == df['Fall_Score']])
        
        print(f"  Bullish Signals (Rise>Fall): {bullish} ({bullish/len(df)*100:.1f}%)")
        print(f"  Bearish Signals (Fall>Rise): {bearish} ({bearish/len(df)*100:.1f}%)")
        print(f"  Neutral Signals: {neutral} ({neutral/len(df)*100:.1f}%)")
        print(f"  {'='*66}")
        print(f"  Min RSI: {df['RSI'].min():.1f} (Most Oversold)")
        print(f"  Max RSI: {df['RSI'].max():.1f} (Most Overbought)")
        print(f"  Min 10D Return: {df['Return_10D'].min():+.1f}%")
        print(f"  Max 10D Return: {df['Return_10D'].max():+.1f}%")
        print("="*70)
    
    def show_all_analyzed_stocks(self):
        """Display all analyzed stocks with their scores"""
        if not self.all_results:
            print("\n⚠️ No analysis data available")
            return
        
        df = pd.DataFrame(self.all_results)
        
        print("\n" + "="*120)
        print(f"📋 COMPLETE LIST OF ALL {len(df)} ANALYZED STOCKS")
        print("="*120)
        print(f"{'No.':<5} {'Code':<10} {'Name':<20} {'Price':<10} {'Rise%':<7} {'Fall%':<7} {'RSI':<6} {'10D%':<9} {'Signal':<10}")
        print("-"*120)
        
        # Show ALL stocks
        for idx, (_, stock) in enumerate(df.iterrows(), 1):
            price = stock['Price']
            price_str = f"${price:,.0f}" if price >= 1000 else f"${price:.2f}"
            
            if stock['Rise_Score'] > stock['Fall_Score']:
                signal = "🟢 BUY"
            elif stock['Fall_Score'] > stock['Rise_Score']:
                signal = "🔴 SELL"
            else:
                signal = "⚪ NEUTRAL"
            
            print(f"{idx:<5} {stock['Code']:<10} {stock['Name']:<20} {price_str:<10} "
                  f"{stock['Rise_Score']:<7.0f} {stock['Fall_Score']:<7.0f} "
                  f"{stock['RSI']:<6.0f} {stock['Return_10D']:+6.1f}% {signal:<10}")
        
        print("="*120)
        print(f"✅ TOTAL: {len(df)} stocks successfully analyzed")
        print("="*120)
    
    def save_complete_results(self, df, market, mode):
        """Save all analyzed stocks to CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create reports directory
        os.makedirs("data/reports", exist_ok=True)
        
        # Save complete analysis (ALL stocks)
        filename = f"data/reports/complete_analysis_{market}_{mode}_{timestamp}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n💾 Complete analysis ({len(df)} stocks) saved to: {filename}")
        
        # Save summary statistics
        summary_data = {
            'Metric': [
                'Analysis Timestamp',
                'Market',
                'Mode',
                'Min History Days Required',
                'Total Stocks Analyzed',
                'Average RSI',
                'Average Rise Score',
                'Average Fall Score',
                'Average 10D Return (%)',
                'Average 20D Return (%)',
                'Average Volume Ratio',
                'Bullish Count (Rise > Fall)',
                'Bullish Percentage (%)',
                'Bearish Count (Fall > Rise)',
                'Bearish Percentage (%)',
                'Neutral Count',
                'Neutral Percentage (%)',
                'Min RSI',
                'Max RSI',
                'Min 10D Return (%)',
                'Max 10D Return (%)'
            ],
            'Value': [
                timestamp,
                market,
                mode,
                self.min_history_days,
                len(df),
                f"{df['RSI'].mean():.2f}",
                f"{df['Rise_Score'].mean():.2f}",
                f"{df['Fall_Score'].mean():.2f}",
                f"{df['Return_10D'].mean():+.2f}",
                f"{df['Return_20D'].mean():+.2f}",
                f"{df['Volume_Ratio'].mean():.2f}",
                len(df[df['Rise_Score'] > df['Fall_Score']]),
                f"{len(df[df['Rise_Score'] > df['Fall_Score']])/len(df)*100:.1f}",
                len(df[df['Fall_Score'] > df['Rise_Score']]),
                f"{len(df[df['Fall_Score'] > df['Rise_Score']])/len(df)*100:.1f}",
                len(df[df['Rise_Score'] == df['Fall_Score']]),
                f"{len(df[df['Rise_Score'] == df['Fall_Score']])/len(df)*100:.1f}",
                f"{df['RSI'].min():.2f}",
                f"{df['RSI'].max():.2f}",
                f"{df['Return_10D'].min():+.2f}",
                f"{df['Return_10D'].max():+.2f}"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_file = f"data/reports/summary_{market}_{mode}_{timestamp}.csv"
        summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig')
        print(f"💾 Summary statistics saved to: {summary_file}")
    
    def disconnect(self):
        self.client.disconnect()
