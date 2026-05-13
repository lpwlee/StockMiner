"""
Hybrid analyzer with proper progress reporting
"""

import pandas as pd
import numpy as np
from datetime import datetime
import time
import os
import json

from src.connectors.stock_list_fetcher import StockListFetcher
from src.connectors.yahoo_client import YahooClient
from src.core.name_fetcher import CompanyNameFetcher
from src.indicators.technical import calculate_indicators
from src.indicators.scorer import calculate_scores
from src.indicators.divergence import calculate_divergence
from src.indicators.confirmation import get_confirm_buy_signal, get_confirm_sell_signal, get_signal_summary
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class HybridAnalyzer:
    def __init__(self):
        self.stock_fetcher = StockListFetcher()
        self.yahoo_client = YahooClient()
        self.name_fetcher = CompanyNameFetcher()
        self.all_results = []
        self.analyzed_stocks = None
        self.last_update_time = None
    
    def get_active_stock_list(self, min_volume=200000):
        """Get list of active stocks"""
        print(f"\n🔍 Getting active stock list from Futu...")
        self.stock_fetcher.connect()
        
        stock_list = self.stock_fetcher.get_filtered_stocks(
            "HK_STOCKS", 
            min_volume=min_volume, 
            max_stocks=None
        )
        
        self.stock_fetcher.disconnect()
        return stock_list
    
    def fetch_company_names(self, stock_codes, progress_callback=None):
        """Fetch company names with progress"""
        return self.name_fetcher.fetch_all_names(stock_codes, progress_callback)
    
    def get_name_cache_stats(self):
        """Get name cache statistics"""
        return {
            'cached_count': self.name_fetcher.get_cached_count(),
            'cache_file': self.name_fetcher.cache_file
        }
    
    def clear_name_cache(self):
        """Clear company name cache"""
        self.name_fetcher.clear_cache()
    
    def analyze(self, market, stock_list, stock_names, max_stocks=None, top_n=20, force_refresh=False, progress_callback=None):
        """Analyze stocks with real progress updates"""
        logger.info(f"Analyzing {market}")
        
        self.all_results = []
        
        mode = "QUICK" if max_stocks else "FULL"
        total_to_analyze = len(stock_list)
        
        if progress_callback:
            progress_callback(0, f"Starting analysis of {total_to_analyze} stocks...")
        
        print(f"\n📊 {mode} MODE: Analyzing {total_to_analyze} active stocks")
        
        results = []
        end_date = datetime.now()
        start_date = end_date - pd.Timedelta(days=365)
        
        for i, code in enumerate(stock_list):
            # Calculate progress percentage
            percent = int((i / total_to_analyze) * 100)
            
            if progress_callback and i % 5 == 0:  # Update every 5 stocks
                progress_callback(percent, f"Analyzing {i+1}/{total_to_analyze}: {code}")
            
            print(f"\r   Progress: {i+1}/{total_to_analyze} - {percent}% - Analyzed: {len(results)}", end="", flush=True)
            
            try:
                data = self.yahoo_client.get_history_kline(
                    code,
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d'),
                    use_cache=not force_refresh
                )
                
                if data.empty or len(data) < 20:
                    continue
                
                indicators = calculate_indicators(data)
                if not indicators:
                    continue
                
                # Calculate divergence
                bullish_div, bearish_div = calculate_divergence(data, lookback=20)
                rise_score, fall_score, reasoning = calculate_scores(indicators)
                
                # Combine all signals
                row_data = {
                    'RSI': indicators.get('rsi', 50),
                    'Return_10D': indicators.get('return_10d', 0),
                    'Volume_Ratio': indicators.get('volume_ratio', 1),
                    'Rise_Score': rise_score,
                    'Fall_Score': fall_score,
                    'Net_Score': rise_score - fall_score,
                    'Bullish_Divergence': bullish_div.get('detected', False),
                    'Bullish_Strength': bullish_div.get('strength', 0),
                    'Bearish_Divergence': bearish_div.get('detected', False),
                    'Bearish_Strength': bearish_div.get('strength', 0)
                }
                
                is_confirm_buy, buy_strength, buy_confidence, buy_reasons = get_confirm_buy_signal(row_data)
                is_confirm_sell, sell_strength, sell_confidence, sell_reasons = get_confirm_sell_signal(row_data)
                signal_summary = get_signal_summary(row_data)
                
                result = {
                    'Code': code,
                    'Name': stock_names.get(code, code.split('.')[-1]),
                    'Price': indicators.get('price', 0),
                    'Rise_Score': rise_score,
                    'Fall_Score': fall_score,
                    'RSI': indicators.get('rsi', 50),
                    'Return_10D': indicators.get('return_10d', 0),
                    'Return_20D': indicators.get('return_20d', 0),
                    'Volume_Ratio': indicators.get('volume_ratio', 1),
                    'Data_Days': len(data),
                    'Reasoning': reasoning,
                    'Net_Score': rise_score - fall_score,
                    'Confirm_Buy': is_confirm_buy,
                    'Buy_Strength': buy_strength,
                    'Buy_Confidence': buy_confidence,
                    'Confirm_Sell': is_confirm_sell,
                    'Sell_Strength': sell_strength,
                    'Sell_Confidence': sell_confidence,
                    'Bullish_Divergence': bullish_div.get('detected', False),
                    'Bullish_Strength': bullish_div.get('strength', 0),
                    'Bullish_Div_Desc': bullish_div.get('description', ''),
                    'Bearish_Divergence': bearish_div.get('detected', False),
                    'Bearish_Strength': bearish_div.get('strength', 0),
                    'Bearish_Div_Desc': bearish_div.get('description', ''),
                    'Signal_Action': signal_summary['action'],
                    'Signal_Confidence': signal_summary['confidence'],
                    'Signal_Reasons': '; '.join(signal_summary['reasons'][:3])
                }
                results.append(result)
                
            except Exception as e:
                logger.debug(f"Error with {code}: {e}")
                continue
            
            time.sleep(0.03)
        
        self.all_results = results
        self.analyzed_stocks = pd.DataFrame(results)
        self.last_update_time = datetime.now()
        
        # Save results
        self.save_cached_data()
        
        if progress_callback:
            progress_callback(100, f"Complete! Analyzed {len(results)} stocks")
        
        print(f"\n   ✅ Analysis Complete!")
        print(f"   📊 Successfully analyzed: {len(self.all_results)} stocks out of {total_to_analyze} active")
        
        if not self.all_results:
            return None, None
        
        df = pd.DataFrame(self.all_results)
        
        confirmed_buy = df[df['Confirm_Buy'] == True].nlargest(top_n, 'Buy_Strength')
        confirmed_sell = df[df['Confirm_Sell'] == True].nlargest(top_n, 'Sell_Strength')
        
        self.display_summary(df, len(stock_list))
        
        return confirmed_buy, confirmed_sell
    
    def display_summary(self, df, total_scanned):
        """Display analysis summary"""
        print("\n" + "="*70)
        print("📊 ANALYSIS SUMMARY")
        print("="*70)
        print(f"  Total Stocks Scanned: {total_scanned:,}")
        print(f"  Successfully Analyzed: {len(df):,}")
        if 'Bullish_Divergence' in df.columns:
            print(f"  Bullish Divergence: {df['Bullish_Divergence'].sum()}")
            print(f"  Bearish Divergence: {df['Bearish_Divergence'].sum()}")
        print(f"  Confirmed Buy Signals: {df['Confirm_Buy'].sum() if 'Confirm_Buy' in df.columns else 0}")
        print(f"  Confirmed Sell Signals: {df['Confirm_Sell'].sum() if 'Confirm_Sell' in df.columns else 0}")
        print("="*70)
    
    def save_cached_data(self):
        """Save analysis results to cache"""
        if self.analyzed_stocks is None or self.analyzed_stocks.empty:
            return
        
        cache_file = "data/cache/latest_analysis.json"
        os.makedirs("data/cache", exist_ok=True)
        
        cache_data = {
            'timestamp': self.last_update_time.isoformat(),
            'stocks': self.analyzed_stocks.to_dict('records'),
            'cache_info': {
                'total_stocks': len(self.analyzed_stocks),
                'bullish_count': len(self.analyzed_stocks[self.analyzed_stocks['Confirm_Buy'] == True]) if 'Confirm_Buy' in self.analyzed_stocks.columns else 0,
                'bearish_count': len(self.analyzed_stocks[self.analyzed_stocks['Confirm_Sell'] == True]) if 'Confirm_Sell' in self.analyzed_stocks.columns else 0,
                'divergence_bullish': len(self.analyzed_stocks[self.analyzed_stocks['Bullish_Divergence'] == True]) if 'Bullish_Divergence' in self.analyzed_stocks.columns else 0,
                'divergence_bearish': len(self.analyzed_stocks[self.analyzed_stocks['Bearish_Divergence'] == True]) if 'Bearish_Divergence' in self.analyzed_stocks.columns else 0
            }
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Cached analysis data saved with {len(self.analyzed_stocks)} stocks")
    
    def load_cached_data(self):
        """Load cached analysis data"""
        cache_file = "data/cache/latest_analysis.json"
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.analyzed_stocks = pd.DataFrame(data['stocks'])
                    self.last_update_time = datetime.fromisoformat(data['timestamp'])
                    print(f"✅ Loaded {len(self.analyzed_stocks)} stocks from cache")
                    return True
            except Exception as e:
                print(f"Error loading cache: {e}")
                return False
        return False
    
    def disconnect(self):
        self.yahoo_client.disconnect()
        self.stock_fetcher.disconnect()
