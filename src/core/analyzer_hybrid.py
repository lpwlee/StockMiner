"""
Hybrid analyzer with efficient caching and delta updates
"""

import pandas as pd
from datetime import datetime
import time
import os

from src.connectors.stock_list_fetcher import StockListFetcher
from src.connectors.yahoo_client import YahooClient
from src.indicators.technical import calculate_indicators
from src.indicators.scorer import calculate_scores
from src.utils.logger import setup_logger
from src.ui.beautiful_display import display_comprehensive_analysis

logger = setup_logger(__name__)

class HybridAnalyzer:
    def __init__(self):
        self.stock_fetcher = StockListFetcher()
        self.yahoo_client = YahooClient()
        self.all_results = []
    
    def analyze(self, market, max_stocks=None, top_n=20, show_all=False, min_volume=300000, force_refresh=False):
        """Analyze stocks with caching and delta updates"""
        logger.info(f"Analyzing {market}")
        
        self.all_results = []
        
        # Show cache status
        cache_stats = self.yahoo_client.get_cache_stats()
        if cache_stats['total_stocks'] > 0:
            print(f"\n💾 Cache Status: {cache_stats['total_stocks']} stocks cached ({cache_stats['cache_size_mb']:.1f} MB)")
            print(f"   Last update: {cache_stats['last_update'] if cache_stats['last_update'] else 'Never'}")
        
        # Get stock list
        print(f"\n🔍 Getting stock list from Futu...")
        self.stock_fetcher.connect()
        
        stock_list = self.stock_fetcher.get_filtered_stocks(
            market, 
            min_volume=min_volume, 
            max_stocks=max_stocks
        )
        
        if not stock_list:
            print("❌ No stocks found")
            self.stock_fetcher.disconnect()
            return None, None
        
        mode = "QUICK" if max_stocks else "FULL"
        total_to_analyze = len(stock_list)
        
        # Count cached vs new stocks
        cached_count = sum(1 for code in stock_list if self.yahoo_client.cache.has_stock(code))
        new_count = total_to_analyze - cached_count
        
        print(f"\n📊 {mode} MODE: Analyzing {total_to_analyze} active stocks")
        print(f"   📦 Cached: {cached_count} stocks (will use cached data)")
        print(f"   🆕 New: {new_count} stocks (will fetch from Yahoo)")
        
        if force_refresh:
            print(f"   🔄 Force refresh enabled - fetching all stocks")
        
        # Get names (from cache or fetch)
        print(f"\n📝 Fetching company names...")
        names = self.yahoo_client.get_stock_names_batch(stock_list)
        
        # Fetch data and analyze (with caching)
        print(f"\n📈 Fetching historical data and analyzing...")
        
        results = []
        end_date = datetime.now()
        start_date = end_date - pd.Timedelta(days=365)
        
        for i, code in enumerate(stock_list):
            print(f"\r   Progress: {i+1}/{total_to_analyze} - Analyzed: {len(results)} - Cached: {self.yahoo_client.cache.has_stock(code)}", end="", flush=True)
            
            try:
                # Get data with caching
                data = self.yahoo_client.get_history_kline(
                    code,
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d'),
                    use_cache=not force_refresh
                )
                
                if data.empty or len(data) < 5:
                    continue
                
                # Calculate indicators
                indicators = calculate_indicators(data)
                
                if not indicators:
                    continue
                
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
                    'Data_Days': len(data),
                    'Reasoning': reasoning,
                    'Net_Score': rise_score - fall_score
                }
                results.append(result)
                
            except Exception as e:
                logger.debug(f"Error with {code}: {e}")
                continue
            
            time.sleep(0.03)
        
        self.all_results = results
        self.stock_fetcher.disconnect()
        
        # Save cache
        self.yahoo_client.save_cache()
        
        print(f"\n   ✅ Analysis Complete!")
        print(f"   📊 Successfully analyzed: {len(self.all_results)} stocks")
        
        # Show updated cache stats
        cache_stats = self.yahoo_client.get_cache_stats()
        print(f"   💾 Cache now has {cache_stats['total_stocks']} stocks ({cache_stats['cache_size_mb']:.1f} MB)")
        
        if not self.all_results:
            print("❌ No stocks were successfully analyzed")
            return None, None
        
        df = pd.DataFrame(self.all_results)
        
        # Save results
        self.save_results(df, market, mode)
        
        # Get top rising and falling
        rising = df[df['Net_Score'] > 0].nlargest(top_n, 'Net_Score')
        falling = df[df['Net_Score'] < 0].nsmallest(top_n, 'Net_Score')
        
        # Display comprehensive analysis
        title = f"{market.replace('_', ' ')} - {mode} ANALYSIS"
        display_comprehensive_analysis(df, rising, falling, title, len(stock_list))
        
        return rising, falling
    
    def save_results(self, df, market, mode):
        """Save to CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("data/reports", exist_ok=True)
        
        filename = f"data/reports/hybrid_{market}_{mode}_{timestamp}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n💾 Full results ({len(df)} stocks) saved to: {filename}")
    
    def clear_cache(self):
        """Clear all cached data"""
        self.yahoo_client.clear_cache()
        print("✅ Cache cleared successfully")
    
    def show_cache_stats(self):
        """Display cache statistics"""
        stats = self.yahoo_client.get_cache_stats()
        print("\n" + "="*60)
        print("📊 CACHE STATISTICS")
        print("="*60)
        print(f"  Total stocks cached: {stats['total_stocks']}")
        print(f"  Total data rows: {stats['total_rows']:,}")
        print(f"  Cache size: {stats['cache_size_mb']:.2f} MB")
        print(f"  Last update: {stats['last_update'] if stats['last_update'] else 'Never'}")
        
        # Show sample of cached stocks
        summary = self.yahoo_client.cache.get_data_summary()
        if not summary.empty:
            print(f"\n  Sample of cached stocks:")
            for _, row in summary.head(10).iterrows():
                print(f"    {row['Code']}: {row['Rows']} days (until {row['Last Date']})")
        print("="*60)
    
    def disconnect(self):
        self.yahoo_client.disconnect()
        self.stock_fetcher.disconnect()
