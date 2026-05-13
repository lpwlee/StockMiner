"""
Company name fetcher with frequent progress updates
"""

import json
import os
import time
from typing import Dict, List
from src.connectors.yahoo_client import YahooClient
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class CompanyNameFetcher:
    def __init__(self):
        self.yahoo_client = YahooClient()
        self.cache_file = "data/cache/company_names.json"
        self.names_cache = {}
        self.load_cache()
    
    def load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.names_cache = json.load(f)
                print(f"✅ Loaded {len(self.names_cache)} cached company names")
            except Exception as e:
                print(f"Error loading name cache: {e}")
                self.names_cache = {}
    
    def save_cache(self):
        try:
            os.makedirs("data/cache", exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.names_cache, f, ensure_ascii=False, indent=2)
            print(f"✅ Saved {len(self.names_cache)} company names to cache")
        except Exception as e:
            print(f"Error saving name cache: {e}")
    
    def get_name(self, code: str, force_refresh: bool = False) -> str:
        if not force_refresh and code in self.names_cache:
            return self.names_cache[code]
        
        try:
            name = self.yahoo_client.get_stock_name(code)
            self.names_cache[code] = name
            return name
        except Exception as e:
            logger.debug(f"Error getting name for {code}: {e}")
            return code
    
    def fetch_all_names(self, stock_codes: List[str], progress_callback=None) -> Dict[str, str]:
        results = {}
        total = len(stock_codes)
        
        # Get cached names
        for code in stock_codes:
            if code in self.names_cache:
                results[code] = self.names_cache[code]
        
        # Fetch missing names
        missing = [code for code in stock_codes if code not in results]
        
        if missing:
            print(f"\n📝 Fetching {len(missing)} missing company names...")
            
            for i, code in enumerate(missing):
                percent = int((i / len(missing)) * 100)
                
                # Update progress every fetch (more frequent)
                if progress_callback:
                    progress_callback(percent, f"Fetching {i+1}/{len(missing)}: {code}")
                
                name = self.get_name(code, force_refresh=True)
                results[code] = name
                
                # Save every 20 names
                if (i + 1) % 20 == 0:
                    self.save_cache()
                    if progress_callback:
                        progress_callback(percent, f"Saved {i+1} names...")
                
                time.sleep(0.05)
            
            self.save_cache()
        
        if progress_callback:
            progress_callback(100, f"Complete! {len(results)} names cached")
        
        return results
    
    def get_cached_count(self) -> int:
        return len(self.names_cache)
    
    def clear_cache(self):
        self.names_cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        print("✅ Company name cache cleared")
