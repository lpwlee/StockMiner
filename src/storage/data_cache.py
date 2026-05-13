"""
Data cache manager for storing stock data locally
"""

import os
import pickle
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class DataCache:
    """Manages local cache of stock data with delta updates"""
    
    def __init__(self, cache_dir="data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.stock_data_file = self.cache_dir / "stock_data.pkl"
        self.metadata_file = self.cache_dir / "metadata.pkl"
        self.last_update_file = self.cache_dir / "last_update.txt"
        
        self.stock_data = self._load_cache()
        self.metadata = self._load_metadata()
        self.last_update = self._load_last_update()
    
    def _load_cache(self) -> Dict:
        if self.stock_data_file.exists():
            try:
                with open(self.stock_data_file, 'rb') as f:
                    data = pickle.load(f)
                logger.info(f"Loaded {len(data)} stocks from cache")
                return data
            except Exception as e:
                logger.error(f"Error loading cache: {e}")
                return {}
        return {}
    
    def _save_cache(self):
        try:
            with open(self.stock_data_file, 'wb') as f:
                pickle.dump(self.stock_data, f)
            logger.info(f"Saved {len(self.stock_data)} stocks to cache")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def _load_metadata(self) -> Dict:
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'rb') as f:
                    return pickle.load(f)
            except:
                return {}
        return {}
    
    def _save_metadata(self):
        try:
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(self.metadata, f)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
    
    def _load_last_update(self) -> Optional[datetime]:
        if self.last_update_file.exists():
            try:
                with open(self.last_update_file, 'r') as f:
                    timestamp = f.read().strip()
                    return datetime.fromisoformat(timestamp)
            except:
                return None
        return None
    
    def get_stock_data(self, code: str) -> Optional[pd.DataFrame]:
        if code in self.stock_data:
            return self.stock_data[code]
        return None
    
    def update_stock_data(self, code: str, data: pd.DataFrame, incremental: bool = True):
        if incremental and code in self.stock_data:
            existing = self.stock_data[code]
            if not existing.empty and not data.empty:
                combined = pd.concat([existing, data], ignore_index=True)
                combined = combined.drop_duplicates(subset=['time_key'])
                combined = combined.sort_values('time_key')
                self.stock_data[code] = combined
            else:
                self.stock_data[code] = data
        else:
            self.stock_data[code] = data
        
        self.metadata[code] = {
            'last_update': datetime.now().isoformat(),
            'rows': len(data),
            'first_date': data['time_key'].min() if not data.empty else None,
            'last_date': data['time_key'].max() if not data.empty else None
        }
        self._save_cache()
        self._save_metadata()
    
    def needs_update(self, code: str, max_age_days: int = 1) -> bool:
        if code not in self.metadata:
            return True
        
        metadata = self.metadata[code]
        last_update = datetime.fromisoformat(metadata['last_update'])
        age = (datetime.now() - last_update).days
        
        return age >= max_age_days
    
    def get_missing_dates(self, code: str, target_end_date: datetime) -> Optional[tuple]:
        if code not in self.metadata:
            return None
        
        last_date_str = self.metadata[code]['last_date']
        if not last_date_str:
            return None
        
        last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
        
        if last_date.date() >= target_end_date.date():
            return None
        
        return (last_date + timedelta(days=1)).strftime('%Y-%m-%d'), target_end_date.strftime('%Y-%m-%d')
    
    def has_stock(self, code: str) -> bool:
        return code in self.stock_data
    
    def get_cache_stats(self) -> Dict:
        total_stocks = len(self.stock_data)
        total_rows = sum(len(df) for df in self.stock_data.values())
        
        cache_size = 0
        if self.stock_data_file.exists():
            cache_size = self.stock_data_file.stat().st_size / (1024 * 1024)
        
        return {
            'total_stocks': total_stocks,
            'total_rows': total_rows,
            'cache_size_mb': cache_size,
            'last_update': self.last_update
        }
    
    def get_data_summary(self) -> pd.DataFrame:
        if not self.metadata:
            return pd.DataFrame()
        
        summaries = []
        for code, meta in self.metadata.items():
            summaries.append({
                'Code': code,
                'Rows': meta.get('rows', 0),
                'First Date': meta.get('first_date', ''),
                'Last Date': meta.get('last_date', ''),
                'Last Update': meta.get('last_update', '')
            })
        
        return pd.DataFrame(summaries)
    
    def clear_cache(self):
        self.stock_data = {}
        self.metadata = {}
        self._save_cache()
        self._save_metadata()
        logger.info("Cache cleared")
    
    def save(self):
        self._save_cache()
        self._save_metadata()
