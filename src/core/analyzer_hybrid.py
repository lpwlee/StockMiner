"""
Hybrid analyzer with divergence detection
"""

import pandas as pd
import numpy as np
from datetime import datetime
import time
import os

from src.connectors.stock_list_fetcher import StockListFetcher
from src.connectors.yahoo_client import YahooClient
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
        self.all_results = []
    
    def analyze(self, market, max_stocks=None, top_n=20, show_all=False, min_volume=300000, force_refresh=False):
        """Analyze stocks with divergence detection"""
        logger.info(f"Analyzing {market}")
        
        self.all_results = []
        
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
        
        print(f"\n📊 {mode} MODE: Analyzing {total_to_analyze} active stocks")
        
        # Get names
        print(f"\n📝 Fetching company names...")
        names = self.yahoo_client.get_stock_names_batch(stock_list)
        
        # Fetch data and analyze
        print(f"\n📈 Fetching historical data and analyzing...")
        
        results = []
        end_date = datetime.now()
        start_date = end_date - pd.Timedelta(days=365)
        
        for i, code in enumerate(stock_list):
            print(f"\r   Progress: {i+1}/{total_to_analyze} - Analyzed: {len(results)}", end="", flush=True)
            
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
                    'Name': names.get(code, code.split('.')[-1]),
                    'Price': indicators.get('price', 0),
                    'Rise_Score': rise_score,
                    'Fall_Score': fall_score,
                    'RSI': indicators.get('rsi', 50),
                    'Return_10D': indicators.get('return_10d', 0),
                    'Return_20D': indicators.get('return_20d', 0),
                    'Volume_Ratio': indicators.get('volume_ratio', 1),
                    'Data_Days': len(data),
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
        self.stock_fetcher.disconnect()
        self.yahoo_client.save_cache()
        
        print(f"\n   ✅ Analysis Complete!")
        print(f"   📊 Successfully analyzed: {len(self.all_results)} stocks")
        
        if not self.all_results:
            print("❌ No stocks were successfully analyzed")
            return None, None
        
        df = pd.DataFrame(self.all_results)
        
        # Create enhanced filters
        divergence_buy = df[df['Bullish_Divergence'] == True].nlargest(top_n, 'Bullish_Strength')
        divergence_sell = df[df['Bearish_Divergence'] == True].nlargest(top_n, 'Bearish_Strength')
        confirmed_buy = df[df['Confirm_Buy'] == True].nlargest(top_n, 'Buy_Strength')
        confirmed_sell = df[df['Confirm_Sell'] == True].nlargest(top_n, 'Sell_Strength')
        
        # Save results
        self.save_results(df, market, mode)
        
        # Display results with divergence
        self.display_divergence_signals(divergence_buy, divergence_sell, confirmed_buy, confirmed_sell, df, len(stock_list))
        
        return confirmed_buy, confirmed_sell
    
    def display_divergence_signals(self, div_buy, div_sell, conf_buy, conf_sell, df, total_scanned):
        """Display signals with divergence priority"""
        print("\n" + "="*100)
        print(f"  🎯 DIVERGENCE & CONFIRMED SIGNALS")
        print("="*100)
        print(f"  Total Scanned: {total_scanned:,} | Analyzed: {len(df):,}")
        print("="*100)
        
        # Display Bullish Divergence (Strongest signal)
        if not div_buy.empty:
            print(f"\n🟢🟢 BULLISH DIVERGENCE DETECTED ({len(div_buy)} stocks) - STRONG BUY SIGNAL")
            print("-"*100)
            for idx, (_, row) in enumerate(div_buy.head(10).iterrows(), 1):
                print(f"  {idx}. {row['Code']} - {row['Name'][:35]}")
                print(f"     RSI: {row['RSI']:.0f} | 10D: {row['Return_10D']:+.1f}% | Strength: {row['Bullish_Strength']}")
                print(f"     Divergence: {row['Bullish_Div_Desc'][:50]}")
        
        # Display Bearish Divergence
        if not div_sell.empty:
            print(f"\n🔴🔴 BEARISH DIVERGENCE DETECTED ({len(div_sell)} stocks) - STRONG SELL SIGNAL")
            print("-"*100)
            for idx, (_, row) in enumerate(div_sell.head(10).iterrows(), 1):
                print(f"  {idx}. {row['Code']} - {row['Name'][:35]}")
                print(f"     RSI: {row['RSI']:.0f} | 10D: {row['Return_10D']:+.1f}% | Strength: {row['Bearish_Strength']}")
                print(f"     Divergence: {row['Bearish_Div_Desc'][:50]}")
        
        # Display regular confirmed signals (no divergence)
        conf_buy_no_div = conf_buy[~conf_buy['Bullish_Divergence']]
        if not conf_buy_no_div.empty:
            print(f"\n🟢 CONFIRMED BUY SIGNALS (No Divergence) - {len(conf_buy_no_div)} stocks")
            print("-"*80)
            for idx, (_, row) in enumerate(conf_buy_no_div.head(10).iterrows(), 1):
                print(f"  {idx}. {row['Code']} - {row['Name'][:35]}: RSI={row['RSI']:.0f}, 10D={row['Return_10D']:+.1f}%")
        
        conf_sell_no_div = conf_sell[~conf_sell['Bearish_Divergence']]
        if not conf_sell_no_div.empty:
            print(f"\n🔴 CONFIRMED SELL SIGNALS (No Divergence) - {len(conf_sell_no_div)} stocks")
            print("-"*80)
            for idx, (_, row) in enumerate(conf_sell_no_div.head(10).iterrows(), 1):
                print(f"  {idx}. {row['Code']} - {row['Name'][:35]}: RSI={row['RSI']:.0f}, 10D={row['Return_10D']:+.1f}%")
        
        # Trading tips
        print("\n" + "="*100)
        print("💡 DIVERGENCE TRADING TIPS:")
        print("  • Bullish Divergence: Price makes LOWER low, RSI makes HIGHER low = Reversal UP")
        print("  • Bearish Divergence: Price makes HIGHER high, RSI makes LOWER high = Reversal DOWN")
        print("  • Strong Divergence (strength 3): High probability trade")
        print("  • Always wait for confirmation (candle close) before entering")
        print("="*100)
    
    def save_results(self, df, market, mode):
        """Save results to CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("data/reports", exist_ok=True)
        
        filename = f"data/reports/hybrid_{market}_{mode}_{timestamp}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n💾 Full results saved to: {filename}")
    
    def disconnect(self):
        self.yahoo_client.disconnect()
        self.stock_fetcher.disconnect()
