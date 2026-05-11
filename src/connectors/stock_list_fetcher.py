"""
Dynamic stock list fetcher from Futu - No quota consumption
"""

from futu import OpenQuoteContext, RET_OK, Market as FutuMarket
from typing import List, Dict, Optional
import time
import pandas as pd

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class StockListFetcher:
    """Fetch dynamic stock lists from Futu - no historical data quota used"""
    
    def __init__(self, host='127.0.0.1', port=11111):
        self.host = host
        self.port = port
        self.ctx = None
        
    def connect(self):
        if self.ctx is None:
            self.ctx = OpenQuoteContext(host=self.host, port=self.port)
        return self.ctx
    
    def disconnect(self):
        if self.ctx:
            self.ctx.close()
            self.ctx = None
    
    def get_all_hk_stocks(self) -> List[str]:
        """Get ALL Hong Kong stocks from Futu"""
        ctx = self.connect()
        
        try:
            ret, data = ctx.get_stock_basicinfo(FutuMarket.HK, "STOCK")
            
            if ret == RET_OK and len(data) > 0:
                stock_codes = data['code'].tolist()
                logger.info(f"Retrieved {len(stock_codes)} HK stocks from Futu (no quota used)")
                return stock_codes
            else:
                logger.error(f"Failed to get HK stock list: {data}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching HK stock list: {e}")
            return []
    
    def get_all_us_stocks(self) -> List[str]:
        """Get ALL US stocks from Futu"""
        ctx = self.connect()
        
        try:
            ret, data = ctx.get_stock_basicinfo(FutuMarket.US, "STOCK")
            
            if ret == RET_OK and len(data) > 0:
                stock_codes = data['code'].tolist()
                logger.info(f"Retrieved {len(stock_codes)} US stocks from Futu (no quota used)")
                return stock_codes
            else:
                logger.error(f"Failed to get US stock list: {data}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching US stock list: {e}")
            return []
    
    def get_market_snapshot(self, stock_codes: List[str]) -> Optional[pd.DataFrame]:
        """Get market snapshot with error handling"""
        if not stock_codes:
            return pd.DataFrame()
        
        ctx = self.connect()
        
        try:
            ret, data = ctx.get_market_snapshot(stock_codes)
            if ret == RET_OK and data is not None:
                return data
            else:
                logger.debug(f"Snapshot failed for batch: {ret}")
                return pd.DataFrame()
        except Exception as e:
            logger.debug(f"Error getting snapshot: {e}")
            return pd.DataFrame()
    
    def get_filtered_stocks(self, market: str, min_volume: int = 300000, max_stocks: int = None) -> List[str]:
        """Get stocks that meet volume criteria"""
        if market == "HK_STOCKS":
            all_stocks = self.get_all_hk_stocks()
        else:
            all_stocks = self.get_all_us_stocks()
        
        if not all_stocks:
            logger.error(f"No stocks found for {market}")
            return []
        
        # Filter by volume
        filtered = []
        batch_size = 50
        total = len(all_stocks)
        
        print(f"\n   Checking {total} stocks for activity...")
        
        for i in range(0, total, batch_size):
            batch = all_stocks[i:i+batch_size]
            snapshot = self.get_market_snapshot(batch)
            
            if snapshot is not None and not snapshot.empty and 'volume' in snapshot.columns:
                try:
                    high_volume = snapshot[
                        (snapshot['volume'] >= min_volume) & 
                        (snapshot['last_price'] >= 0.5)
                    ]
                    filtered.extend(high_volume['code'].tolist())
                except Exception as e:
                    logger.debug(f"Error filtering batch: {e}")
            
            percent = min(i + batch_size, total) / total * 100
            print(f"\r   Progress: {min(i+batch_size, total)}/{total} ({percent:.1f}%) - Found {len(filtered)} active", end="", flush=True)
            
            # Small delay to avoid rate limiting
            time.sleep(0.05)
        
        print()
        logger.info(f"Found {len(filtered)} active stocks out of {total} total")
        
        if max_stocks and len(filtered) > max_stocks:
            return filtered[:max_stocks]
        return filtered
