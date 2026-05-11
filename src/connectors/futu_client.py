from futu import OpenQuoteContext, RET_OK, KLType, AuType, Market as FutuMarket
import pandas as pd
from typing import List, Dict, Tuple
import time

from src.utils.logger import setup_logger
from src.connectors.rate_limiter import RateLimiter

logger = setup_logger(__name__)

class FutuClient:
    def __init__(self, host='127.0.0.1', port=11111):
        self.host = host
        self.port = port
        self.ctx = None
        self.rate_limiter = RateLimiter()
        self.name_cache = {}
    
    def connect(self):
        if self.ctx is None:
            self.ctx = OpenQuoteContext(host=self.host, port=self.port)
            logger.info(f"Connected to FutuOpenD")
        return self.ctx
    
    def disconnect(self):
        if self.ctx:
            self.ctx.close()
            self.ctx = None
    
    def get_stock_list(self, market: str) -> List[str]:
        ctx = self.connect()
        futu_market = FutuMarket.HK if market == "HK_STOCKS" else FutuMarket.US
        ret, data = ctx.get_stock_basicinfo(futu_market, "STOCK")
        
        if ret == RET_OK:
            return [s['code'] for s in data.to_dict('records')]
        return []
    
    def get_market_snapshot(self, codes: List[str]) -> pd.DataFrame:
        self.rate_limiter.wait_if_needed()
        ctx = self.connect()
        ret, data = ctx.get_market_snapshot(codes)
        return data if ret == RET_OK else pd.DataFrame()
    
    def get_history_kline(self, code: str, start: str, end: str) -> pd.DataFrame:
        ctx = self.connect()
        ret, data, _ = ctx.request_history_kline(code, start=start, end=end, 
                                                  ktype=KLType.K_DAY, autype=AuType.QFQ)
        return data if ret == RET_OK else pd.DataFrame()
    
    def get_stock_names(self, codes: List[str]) -> Dict[str, Tuple[str, str]]:
        result = {}
        uncached = [c for c in codes if c not in self.name_cache]
        
        if uncached:
            ctx = self.connect()
            for i in range(0, len(uncached), 50):
                batch = uncached[i:i+50]
                ret, data = ctx.get_stock_quote(batch)
                if ret == RET_OK:
                    for _, row in data.iterrows():
                        code = row.get('code')
                        if code:
                            name_cn = row.get('name_cn', '')
                            name_en = row.get('name_en', '')
                            self.name_cache[code] = (name_cn or name_en or code.split('.')[-1])
                time.sleep(0.1)
        
        for code in codes:
            result[code] = self.name_cache.get(code, code.split('.')[-1])
        return result
