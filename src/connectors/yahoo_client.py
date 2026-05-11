"""
Yahoo Finance connector with caching and delta updates
"""

import yfinance as yf
import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import time

from src.utils.logger import setup_logger
from src.storage.data_cache import DataCache

logger = setup_logger(__name__)

class YahooClient:
    """Yahoo Finance client with caching and delta updates"""
    
    def __init__(self):
        self.cache = DataCache()
        self.name_cache = {}
        self.cache_duration = 3600
        self.last_request_time = 0
        
    def _rate_limit(self):
        current_time = time.time()
        if current_time - self.last_request_time < 0.2:
            time.sleep(0.2)
        self.last_request_time = time.time()
    
    def _convert_futu_ticker_to_yahoo(self, code: str) -> str:
        """Convert Futu format to Yahoo Finance format"""
        if code.startswith("HK."):
            number_str = code[3:]
            try:
                num = int(number_str)
                return f"{num:04d}.HK"
            except ValueError:
                return f"{number_str}.HK"
        elif code.startswith("US."):
            return code[3:]
        return code
    
    def get_stock_name(self, code: str) -> str:
        """Get display name for a single stock"""
        ticker = self._convert_futu_ticker_to_yahoo(code)
        
        # Check cache
        if ticker in self.name_cache:
            cache_time = self.name_cache[ticker].get('timestamp', 0)
            if time.time() - cache_time < self.cache_duration:
                return self.name_cache[ticker]['name']
        
        try:
            self._rate_limit()
            stock = yf.Ticker(ticker)
            info = stock.info
            name = info.get('longName', info.get('shortName', ticker))
            
            if not name or name == ticker:
                hist = stock.history(period='5d')
                if not hist.empty:
                    name = f"Stock {ticker}"
                else:
                    name = ticker
            
            self.name_cache[ticker] = {
                'name': name if name else ticker,
                'timestamp': time.time()
            }
            return name if name else ticker
            
        except Exception as e:
            logger.debug(f"Error getting name for {code}: {e}")
            return ticker
    
    def get_stock_names_batch(self, codes: List[str]) -> Dict[str, str]:
        """Get names for multiple stocks with caching"""
        result = {}
        for i, code in enumerate(codes):
            print(f"\r   Fetching names: {i+1}/{len(codes)} - {code}", end="", flush=True)
            result[code] = self.get_stock_name(code)
            time.sleep(0.03)
        print()
        return result
    
    def get_history_kline(self, code: str, start_date: str, end_date: str, use_cache: bool = True) -> pd.DataFrame:
        """Get historical data with caching support"""
        
        # Check cache first
        if use_cache:
            cached_data = self.cache.get_stock_data(code)
            if cached_data is not None and not self.cache.needs_update(code):
                logger.debug(f"Using cached data for {code}")
                return cached_data
        
        # Fetch from Yahoo
        self._rate_limit()
        ticker = self._convert_futu_ticker_to_yahoo(code)
        
        try:
            # If we have cached data, only fetch missing dates
            if use_cache and self.cache.has_stock(code):
                missing_range = self.cache.get_missing_dates(code, datetime.strptime(end_date, '%Y-%m-%d'))
                if missing_range:
                    missing_start, missing_end = missing_range
                    logger.debug(f"Fetching delta for {code}: {missing_start} to {missing_end}")
                    new_data = self._fetch_data(ticker, missing_start, missing_end)
                    
                    if not new_data.empty:
                        # Update cache with new data
                        self.cache.update_stock_data(code, new_data, incremental=True)
                        return self.cache.get_stock_data(code)
                else:
                    # Data is up to date
                    return self.cache.get_stock_data(code)
            
            # Full fetch (no cache or first time)
            data = self._fetch_data(ticker, start_date, end_date)
            
            if not data.empty and use_cache:
                self.cache.update_stock_data(code, data, incremental=False)
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching {code}: {e}")
            return pd.DataFrame()
    
    def _fetch_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Internal method to fetch data from Yahoo"""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date, auto_adjust=False)
            
            if data.empty:
                return pd.DataFrame()
            
            # Format data
            data = data.reset_index()
            data.rename(columns={
                'Date': 'time_key',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            }, inplace=True)
            
            data['time_key'] = pd.to_datetime(data['time_key']).dt.strftime('%Y-%m-%d')
            
            return data
            
        except Exception as e:
            logger.debug(f"Error fetching {ticker}: {e}")
            return pd.DataFrame()
    
    def get_batch_history(self, codes: List[str], days_back: int = 365, use_cache: bool = True) -> Dict[str, pd.DataFrame]:
        """Fetch historical data for multiple stocks with caching"""
        results = {}
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        for i, code in enumerate(codes):
            print(f"\r   Fetching: {i+1}/{len(codes)} - {code} (Cached: {self.cache.has_stock(code)})", end="", flush=True)
            
            data = self.get_history_kline(
                code,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d'),
                use_cache=use_cache
            )
            
            if not data.empty and len(data) >= 5:
                results[code] = data
            
            time.sleep(0.03)
        
        print()
        return results
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return self.cache.get_cache_stats()
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear_cache()
        self.name_cache = {}
    
    def save_cache(self):
        """Save cache to disk"""
        self.cache.save()
    
    def disconnect(self):
        """Save cache before disconnecting"""
        self.cache.save()
