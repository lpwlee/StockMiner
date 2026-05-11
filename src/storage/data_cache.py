"""
Data cache manager for storing stock data locally
Only loads delta changes on subsequent runs
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
        
        # Cache files
        self.stock_data_file = self.cache_dir / "stock_data.pkl"
        self.metadata_file = self.cache_dir / "metadata.pkl"
        self.last_update_file = self.cache_dir / "last_update.txt"
        
        # Load existing cache
        self.stock_data = self._load_cache()
        self.metadata = self._load_metadata()
        self.last_update = self._load_last_update()
    
    def _load_cache(self) -> Dict:
        """Load cached stock data from disk"""
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
        """Save stock data to disk"""
        try:
            with open(self.stock_data_file, 'wb') as f:
                pickle.dump(self.stock_data, f)
            logger.info(f"Saved {len(self.stock_data)} stocks to cache")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def _load_metadata(self) -> Dict:
        """Load metadata about cached stocks"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'rb') as f:
                    return pickle.load(f)
            except:
                return {}
        return {}
    
    def _save_metadata(self):
        """Save metadata to disk"""
        try:
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(self.metadata, f)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
    
    def _load_last_update(self) -> Optional[datetime]:
        """Load last update timestamp"""
        if self.last_update_file.exists():
            try:
                with open(self.last_update_file, 'r') as f:
                    timestamp = f.read().strip()
                    return datetime.fromisoformat(timestamp)
            except:
                return None
        return None
    
    def _save_last_update(self):
        """Save current update timestamp"""
        try:
            with open(self.last_update_file, 'w') as f:
                f.write(datetime.now().isoformat())
        except Exception as e:
            logger.error(f"Error saving last update: {e}")
    
    def get_stock_data(self, code: str) -> Optional[pd.DataFrame]:
        """Get cached data for a specific stock"""
        if code in self.stock_data:
            return self.stock_data[code]
        return None
    
    def update_stock_data(self, code: str, data: pd.DataFrame, incremental: bool = True):
        """Update cached data for a stock"""
        if incremental and code in self.stock_data:
            # Merge with existing data
            existing = self.stock_data[code]
            if not existing.empty and not data.empty:
                # Combine and deduplicate
                combined = pd.concat([existing, data], ignore_index=True)
                combined = combined.drop_duplicates(subset=['time_key'])
                combined = combined.sort_values('time_key')
                self.stock_data[code] = combined
            else:
                self.stock_data[code] = data
        else:
            # Full replacement
            self.stock_data[code] = data
        
        # Update metadata
        self.metadata[code] = {
            'last_update': datetime.now().isoformat(),
            'rows': len(data),
            'first_date': data['time_key'].min() if not data.empty else None,
            'last_date': data['time_key'].max() if not data.empty else None
        }
    
    def needs_update(self, code: str, max_age_days: int = 1) -> bool:
        """Check if a stock needs to be updated"""
        if code not in self.metadata:
            return True
        
        metadata = self.metadata[code]
        last_update = datetime.fromisoformat(metadata['last_update'])
        age = (datetime.now() - last_update).days
        
        return age >= max_age_days
    
    def get_missing_dates(self, code: str, target_end_date: datetime) -> Optional[tuple]:
        """Get date range for missing data"""
        if code not in self.metadata:
            return None
        
        last_date_str = self.metadata[code]['last_date']
        if not last_date_str:
            return None
        
        last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
        
        if last_date.date() >= target_end_date.date():
            return None  # No missing data
        
        # Return start date for missing data (day after last cached)
        return (last_date + timedelta(days=1)).strftime('%Y-%m-%d'), target_end_date.strftime('%Y-%m-%d')
    
    def has_stock(self, code: str) -> bool:
        """Check if stock exists in cache"""
        return code in self.stock_data
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        total_stocks = len(self.stock_data)
        total_rows = sum(len(df) for df in self.stock_data.values())
        
        return {
            'total_stocks': total_stocks,
            'total_rows': total_rows,
            'cache_size_mb': self._get_cache_size(),
            'last_update': self.last_update
        }
    
    def _get_cache_size(self) -> float:
        """Get cache file size in MB"""
        if self.stock_data_file.exists():
            return self.stock_data_file.stat().st_size / (1024 * 1024)
        return 0
    
    def clear_cache(self):
        """Clear all cached data"""
        self.stock_data = {}
        self.metadata = {}
        self._save_cache()
        self._save_metadata()
        logger.info("Cache cleared")
    
    def save(self):
        """Save all cached data"""
        self._save_cache()
        self._save_metadata()
        self._save_last_update()
    
    def get_data_summary(self) -> pd.DataFrame:
        """Get summary of cached data"""
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
