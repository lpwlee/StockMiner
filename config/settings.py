"""
Configuration management system
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class AppConfig:
    """Application configuration"""
    name: str = "Futu Stock Analyzer"
    version: str = "2.0.0"
    environment: str = "production"

@dataclass
class FutuAPIConfig:
    """Futu API configuration"""
    host: str = "127.0.0.1"
    port: int = 11111
    connection_timeout: int = 30
    max_retries: int = 3
    rate_limit_per_second: int = 30

@dataclass
class DataConfig:
    """Data configuration"""
    cache_dir: str = "data/cache"
    report_dir: str = "data/reports"
    log_dir: str = "data/logs"
    historical_days: int = 365
    incremental_update: bool = True
    compression: bool = True

@dataclass
class FilterConfig:
    """Stock filtering configuration"""
    min_volume: int = 1000000
    min_turnover: int = 10000000
    min_price: float = 1.0
    max_price: float = 10000.0
    min_market_cap: float = 1000000000
    min_avg_volume_20d: int = 500000
    max_spread_percent: float = 2.0
    min_days_traded: int = 200

@dataclass
class AnalysisConfig:
    """Analysis configuration"""
    top_n_results: int = 20
    min_history_days: int = 50
    prediction_horizon: int = 10
    confidence_threshold: float = 0.6
    enabled_indicators: list = field(default_factory=lambda: [
        "SMA", "EMA", "RSI", "MACD", "BBANDS", "ATR", "ADX", "OBV", "STOCH"
    ])

@dataclass
class PerformanceConfig:
    """Performance configuration"""
    parallel_processing: bool = True
    max_workers: int = 4
    batch_size: int = 50
    cache_results: bool = True

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_rotation: str = "daily"
    max_files: int = 30

class ConfigurationManager:
    """Central configuration manager"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.config_dir = Path(__file__).parent.parent.parent / "config"
            self.load_configurations()
            self.initialized = True
    
    def load_configurations(self):
        """Load all configuration files"""
        # Load main config
        main_config_path = self.config_dir / "config.yaml"
        if main_config_path.exists():
            with open(main_config_path, 'r') as f:
                main_config = yaml.safe_load(f)
        else:
            main_config = {}
        
        # Initialize config objects
        self.app = AppConfig(**main_config.get('app', {}))
        self.futu_api = FutuAPIConfig(**main_config.get('futu_api', {}))
        self.data = DataConfig(**main_config.get('data', {}))
        self.filters = FilterConfig(**main_config.get('filters', {}))
        self.analysis = AnalysisConfig(**main_config.get('analysis', {}))
        self.performance = PerformanceConfig(**main_config.get('performance', {}))
        self.logging = LoggingConfig(**main_config.get('logging', {}))
        
        # Load scoring weights
        scoring_path = self.config_dir / "scoring_weights.yaml"
        if scoring_path.exists():
            with open(scoring_path, 'r') as f:
                self.scoring_weights = yaml.safe_load(f)
        else:
            self.scoring_weights = {}
        
        # Load indicator configs
        indicators_path = self.config_dir / "indicators.yaml"
        if indicators_path.exists():
            with open(indicators_path, 'r') as f:
                self.indicators_config = yaml.safe_load(f)
        else:
            self.indicators_config = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key"""
        keys = key.split('.')
        current = self.__dict__
        for k in keys:
            if isinstance(current, dict):
                current = current.get(k, default)
            elif hasattr(current, k):
                current = getattr(current, k)
            else:
                return default
            if current is None:
                return default
        return current
    
    def update(self, key: str, value: Any):
        """Update configuration value"""
        keys = key.split('.')
        current = self.__dict__
        for k in keys[:-1]:
            if hasattr(current, k):
                current = getattr(current, k)
            else:
                setattr(current, k, {})
                current = getattr(current, k)
        setattr(current, keys[-1], value)

# Global configuration instance
config = ConfigurationManager()