"""
Futu API Connector with dynamic company name fetching - Fixed Name Extraction
"""

from futu import OpenQuoteContext, RET_OK, KLType, AuType, Market as FutuMarket
import pandas as pd
from typing import List, Dict, Optional, Tuple
import time
from functools import wraps
import socket

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def retry_on_failure(max_retries: int = 3, delay: float = 2.0):
    """Decorator for retrying failed API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    result = func(*args, **kwargs)
                    if result is not None:
                        return result
                    elif attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}, retrying...")
                        time.sleep(delay * (attempt + 1))
                    else:
                        return result
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"All retries failed for {func.__name__}: {e}")
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying...")
                    time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator

class FutuConnector:
    """Singleton connector for Futu API"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.host = "127.0.0.1"
            self.port = 11111
            self._current_ctx = None
            self.connection_attempts = 0
            self.name_cache = {}  # Cache for stock names
            self.stock_info_cache = {}  # Cache for full stock info
            self.cache_duration = 3600  # Cache names for 1 hour
            self.last_cache_update = {}
            self.initialized = True
            logger.info(f"FutuConnector initialized for {self.host}:{self.port}")
    
    def check_connection(self) -> bool:
        """Check if FutuOpenD is running and accepting connections"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug(f"Connection check failed: {e}")
            return False
    
    def get_connection(self):
        """Get or create a connection context"""
        if not self.check_connection():
            error_msg = f"Cannot connect to FutuOpenD at {self.host}:{self.port}. Please ensure FutuOpenD is running."
            logger.error(error_msg)
            raise ConnectionError(error_msg)
        
        if self._current_ctx is None:
            try:
                self._current_ctx = OpenQuoteContext(host=self.host, port=self.port)
                self.connection_attempts = 0
                logger.info(f"Connected to FutuOpenD at {self.host}:{self.port}")
            except Exception as e:
                logger.error(f"Failed to create connection: {e}")
                raise
        
        return self._current_ctx
    
    def release_connection(self):
        """Release the current connection"""
        if self._current_ctx:
            try:
                self._current_ctx.close()
                logger.info("Released Futu connection")
            except Exception as e:
                logger.warning(f"Error releasing connection: {e}")
            finally:
                self._current_ctx = None
    
    @retry_on_failure(max_retries=2)
    def get_stock_basic_info(self, market: str) -> List[Dict]:
        """Get basic information for stocks in a market"""
        try:
            ctx = self.get_connection()
            
            if market == "HK_STOCKS":
                ret, data = ctx.get_stock_basicinfo(FutuMarket.HK, "STOCK")
            elif market == "US_STOCKS":
                ret, data = ctx.get_stock_basicinfo(FutuMarket.US, "STOCK")
            else:
                logger.warning(f"Unknown market: {market}")
                return []
            
            if ret == RET_OK and len(data) > 0:
                stocks = data.to_dict('records')
                logger.info(f"Retrieved {len(stocks)} stocks for {market}")
                
                # Cache stock names for future use - check all possible name fields
                for stock in stocks:
                    code = stock.get('code')
                    if code:
                        # Try different field names that Futu might use
                        name_en = stock.get('name_en') or stock.get('name') or stock.get('stock_name') or ''
                        name_cn = stock.get('name_cn') or stock.get('chinese_name') or ''
                        
                        # If still empty, try to extract from 'name' field that might contain Chinese
                        if not name_en and 'name' in stock:
                            name = stock['name']
                            # Check if name contains Chinese characters
                            if any('\u4e00' <= char <= '\u9fff' for char in name):
                                name_cn = name
                            else:
                                name_en = name
                        
                        self.stock_info_cache[code] = stock
                        self.name_cache[code] = {
                            'name_en': name_en,
                            'name_cn': name_cn,
                            'market': market,
                            'timestamp': time.time()
                        }
                        
                        # Debug: print first few names to verify
                        if len(self.name_cache) <= 5:
                            logger.debug(f"Cached: {code} -> EN: '{name_en}', CN: '{name_cn}'")
                
                return stocks
            else:
                logger.warning(f"Failed to get stock info for {market}: {data if ret != RET_OK else 'No data'}")
                return []
        except ConnectionError as e:
            logger.error(f"Connection error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting stock info: {e}")
            return []
    
    def _extract_name_from_row(self, row, code: str) -> Tuple[str, str]:
        """Extract English and Chinese names from a data row"""
        name_en = ''
        name_cn = ''
        
        # Try different field names
        for field in ['name_en', 'name', 'stock_name', 'english_name']:
            if field in row and row[field]:
                val = str(row[field])
                # Check if it contains Chinese characters
                if any('\u4e00' <= char <= '\u9fff' for char in val):
                    if not name_cn:
                        name_cn = val
                else:
                    if not name_en:
                        name_en = val
        
        for field in ['name_cn', 'chinese_name', 'cn_name']:
            if field in row and row[field]:
                name_cn = str(row[field])
                break
        
        # If still no names, use code
        if not name_en and not name_cn:
            code_num = code.split('.')[-1] if '.' in code else code
            name_en = f"Stock {code_num}"
            name_cn = f"股票 {code_num}"
        
        return name_en, name_cn
    
    @retry_on_failure(max_retries=2)
    def get_stock_name(self, stock_code: str, force_refresh: bool = False) -> Tuple[str, str]:
        """Dynamically fetch stock name from API or cache"""
        # Check cache first
        if not force_refresh and stock_code in self.name_cache:
            cache_entry = self.name_cache[stock_code]
            if time.time() - cache_entry.get('timestamp', 0) < self.cache_duration:
                return cache_entry.get('name_en', ''), cache_entry.get('name_cn', '')
        
        try:
            ctx = self.get_connection()
            
            # Method 1: Get stock quote which includes name
            ret, quote_data = ctx.get_stock_quote([stock_code])
            if ret == RET_OK and len(quote_data) > 0:
                row = quote_data.iloc[0]
                name_en, name_cn = self._extract_name_from_row(row, stock_code)
                
                if name_en or name_cn:
                    self.name_cache[stock_code] = {
                        'name_en': name_en,
                        'name_cn': name_cn,
                        'timestamp': time.time()
                    }
                    return name_en, name_cn
            
            # Method 2: Try stock basic info
            market = "HK_STOCKS" if stock_code.startswith("HK.") else "US_STOCKS"
            ret, basic_data = ctx.get_stock_basicinfo(
                FutuMarket.HK if market == "HK_STOCKS" else FutuMarket.US, 
                "STOCK"
            )
            
            if ret == RET_OK:
                stock_info = basic_data[basic_data['code'] == stock_code]
                if len(stock_info) > 0:
                    row = stock_info.iloc[0]
                    name_en, name_cn = self._extract_name_from_row(row, stock_code)
                    
                    self.name_cache[stock_code] = {
                        'name_en': name_en,
                        'name_cn': name_cn,
                        'timestamp': time.time()
                    }
                    return name_en, name_cn
            
            # Return fallback
            return self._get_fallback_name(stock_code)
                
        except Exception as e:
            logger.error(f"Error fetching name for {stock_code}: {e}")
            return self._get_fallback_name(stock_code)
    
    def _get_fallback_name(self, stock_code: str) -> Tuple[str, str]:
        """Generate fallback names when API fails"""
        code_num = stock_code.split('.')[-1] if '.' in stock_code else stock_code
        name_en = f"Stock {code_num}"
        name_cn = f"股票 {code_num}"
        return name_en, name_cn
    
    @retry_on_failure(max_retries=2)
    def get_batch_stock_names(self, stock_codes: List[str]) -> Dict[str, Tuple[str, str]]:
        """Fetch names for multiple stocks in batch"""
        result = {}
        uncached_codes = []
        
        # Check cache first
        for code in stock_codes:
            if code in self.name_cache:
                cache_entry = self.name_cache[code]
                if time.time() - cache_entry.get('timestamp', 0) < self.cache_duration:
                    result[code] = (cache_entry.get('name_en', ''), cache_entry.get('name_cn', ''))
                else:
                    uncached_codes.append(code)
            else:
                uncached_codes.append(code)
        
        if not uncached_codes:
            return result
        
        # Fetch from API
        try:
            ctx = self.get_connection()
            
            # Get stock quotes for uncached codes
            for i in range(0, len(uncached_codes), 50):
                batch = uncached_codes[i:i+50]
                ret, quote_data = ctx.get_stock_quote(batch)
                
                if ret == RET_OK and len(quote_data) > 0:
                    for _, row in quote_data.iterrows():
                        code = row.get('code', '')
                        if code in uncached_codes:
                            name_en, name_cn = self._extract_name_from_row(row, code)
                            result[code] = (name_en, name_cn)
                            self.name_cache[code] = {
                                'name_en': name_en,
                                'name_cn': name_cn,
                                'timestamp': time.time()
                            }
                
                time.sleep(0.1)
            
            # Handle any remaining codes
            for code in uncached_codes:
                if code not in result:
                    fallback_en, fallback_cn = self._get_fallback_name(code)
                    result[code] = (fallback_en, fallback_cn)
                    self.name_cache[code] = {
                        'name_en': fallback_en,
                        'name_cn': fallback_cn,
                        'timestamp': time.time()
                    }
                    
        except Exception as e:
            logger.error(f"Error batch fetching names: {e}")
            for code in uncached_codes:
                fallback_en, fallback_cn = self._get_fallback_name(code)
                result[code] = (fallback_en, fallback_cn)
        
        return result
    
    @retry_on_failure(max_retries=2)
    def get_market_snapshot(self, stock_codes: List[str]) -> pd.DataFrame:
        """Get market snapshot for multiple stocks"""
        try:
            if not stock_codes:
                return pd.DataFrame()
            
            ctx = self.get_connection()
            ret, data = ctx.get_market_snapshot(stock_codes)
            
            if ret == RET_OK:
                return data
            else:
                logger.warning(f"Failed to get market snapshot: {data}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error getting market snapshot: {e}")
            return pd.DataFrame()
    
    @retry_on_failure(max_retries=2)
    def get_history_kline(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get historical K-line data"""
        try:
            ctx = self.get_connection()
            ret, data, _ = ctx.request_history_kline(
                stock_code, 
                start=start_date, 
                end=end_date,
                ktype=KLType.K_DAY, 
                autype=AuType.QFQ, 
                max_count=1000
            )
            
            if ret == RET_OK and len(data) > 0:
                return data
            else:
                logger.debug(f"No data for {stock_code}: {data if ret != RET_OK else 'Empty'}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error getting history for {stock_code}: {e}")
            return pd.DataFrame()
    
    def clear_name_cache(self):
        """Clear the name cache to force fresh fetches"""
        self.name_cache.clear()
        self.stock_info_cache.clear()
        logger.info("Name cache cleared")
    
    def __enter__(self):
        """Context manager entry"""
        self.get_connection()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release_connection()
