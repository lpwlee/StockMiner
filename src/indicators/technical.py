"""
Technical indicators with better error handling
"""

import numpy as np
import pandas as pd

def calculate_rsi(close_prices, period=14):
    """Calculate RSI with error handling"""
    if len(close_prices) < period + 1:
        return 50.0
    
    try:
        deltas = np.diff(close_prices[-period-1:])
        gains = deltas[deltas > 0].sum() / period if len(deltas[deltas > 0]) > 0 else 0
        losses = abs(deltas[deltas < 0].sum()) / period if len(deltas[deltas < 0]) > 0 else 0
        
        if losses == 0:
            return 100.0
        rs = gains / losses
        return float(100 - (100 / (1 + rs)))
    except:
        return 50.0

def calculate_returns(close_prices):
    """Calculate returns with error handling"""
    close = close_prices[-1]
    returns = {}
    
    try:
        returns['return_5d'] = float((close / close_prices[-6] - 1) * 100) if len(close_prices) >= 6 else 0
    except:
        returns['return_5d'] = 0
    
    try:
        returns['return_10d'] = float((close / close_prices[-11] - 1) * 100) if len(close_prices) >= 11 else 0
    except:
        returns['return_10d'] = 0
    
    try:
        returns['return_20d'] = float((close / close_prices[-21] - 1) * 100) if len(close_prices) >= 21 else 0
    except:
        returns['return_20d'] = 0
    
    return returns

def calculate_volume_ratio(volumes):
    """Calculate volume ratio with error handling"""
    if len(volumes) < 20:
        return 1.0
    
    try:
        avg_volume = np.mean(volumes[-20:])
        return float(volumes[-1] / avg_volume) if avg_volume > 0 else 1.0
    except:
        return 1.0

def calculate_indicators(data: pd.DataFrame) -> dict:
    """Calculate all technical indicators with error handling"""
    if data.empty or len(data) < 5:
        return {}
    
    try:
        close = data['close'].values
        volumes = data['volume'].values
        
        indicators = {
            'price': float(close[-1]),
            'rsi': calculate_rsi(close),
            **calculate_returns(close),
            'volume_ratio': calculate_volume_ratio(volumes),
        }
        
        # Add moving averages if enough data
        if len(close) >= 20:
            indicators['sma_20'] = float(np.mean(close[-20:]))
        if len(close) >= 50:
            indicators['sma_50'] = float(np.mean(close[-50:]))
        
        return indicators
    except Exception as e:
        logger.debug(f"Error calculating indicators: {e}")
        return {}
