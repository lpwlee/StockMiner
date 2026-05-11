"""
Divergence detection for technical analysis
Bullish Divergence: Price makes lower low, RSI makes higher low (BUY signal)
Bearish Divergence: Price makes higher high, RSI makes lower high (SELL signal)
"""

import numpy as np
from typing import Dict, List, Tuple, Optional

def find_swing_points(prices: np.ndarray, order: int = 5) -> Tuple[List[int], List[int]]:
    """
    Find swing highs and lows in price series
    order: number of points to check on each side
    """
    highs_idx = []
    lows_idx = []
    
    for i in range(order, len(prices) - order):
        # Check for swing high
        is_high = True
        for j in range(1, order + 1):
            if prices[i] <= prices[i - j] or prices[i] <= prices[i + j]:
                is_high = False
                break
        if is_high:
            highs_idx.append(i)
        
        # Check for swing low
        is_low = True
        for j in range(1, order + 1):
            if prices[i] >= prices[i - j] or prices[i] >= prices[i + j]:
                is_low = False
                break
        if is_low:
            lows_idx.append(i)
    
    return highs_idx, lows_idx

def detect_bullish_divergence(prices: np.ndarray, rsi: np.ndarray, lookback: int = 20) -> Dict:
    """
    Detect Bullish Divergence: Price lower low, RSI higher low
    Returns: {
        'detected': bool,
        'strength': int (1-3),
        'description': str,
        'price_ll': float,
        'rsi_hs': float
    }
    """
    if len(prices) < lookback or len(rsi) < lookback:
        return {'detected': False, 'strength': 0, 'description': ''}
    
    # Get recent data
    recent_prices = prices[-lookback:]
    recent_rsi = rsi[-lookback:]
    
    # Find swing lows in price
    _, price_lows_idx = find_swing_points(recent_prices, order=3)
    
    if len(price_lows_idx) < 2:
        return {'detected': False, 'strength': 0, 'description': ''}
    
    # Get last two swing lows
    price_low1_idx = price_lows_idx[-2]
    price_low2_idx = price_lows_idx[-1]
    
    price_low1 = recent_prices[price_low1_idx]
    price_low2 = recent_prices[price_low2_idx]
    
    # Check if price made lower low
    if price_low2 >= price_low1:
        return {'detected': False, 'strength': 0, 'description': ''}
    
    # Check RSI at these points
    rsi_at_low1 = recent_rsi[price_low1_idx]
    rsi_at_low2 = recent_rsi[price_low2_idx]
    
    # Bullish divergence: price lower low, RSI higher low
    if rsi_at_low2 > rsi_at_low1:
        strength = 1
        description = "Bullish Divergence Detected"
        
        # Calculate strength based on how significant
        price_change = abs((price_low2 - price_low1) / price_low1 * 100)
        rsi_change = rsi_at_low2 - rsi_at_low1
        
        if price_change > 5 and rsi_change > 10:
            strength = 3
            description = "Strong Bullish Divergence - Major reversal signal"
        elif price_change > 3 or rsi_change > 5:
            strength = 2
            description = "Moderate Bullish Divergence"
        
        return {
            'detected': True,
            'strength': strength,
            'type': 'BULLISH',
            'description': description,
            'price_low1': price_low1,
            'price_low2': price_low2,
            'rsi_low1': rsi_at_low1,
            'rsi_low2': rsi_at_low2,
            'price_change_pct': price_change,
            'rsi_change': rsi_change
        }
    
    return {'detected': False, 'strength': 0, 'description': ''}

def detect_bearish_divergence(prices: np.ndarray, rsi: np.ndarray, lookback: int = 20) -> Dict:
    """
    Detect Bearish Divergence: Price higher high, RSI lower high
    Returns: {
        'detected': bool,
        'strength': int (1-3),
        'description': str
    }
    """
    if len(prices) < lookback or len(rsi) < lookback:
        return {'detected': False, 'strength': 0, 'description': ''}
    
    # Get recent data
    recent_prices = prices[-lookback:]
    recent_rsi = rsi[-lookback:]
    
    # Find swing highs in price
    price_highs_idx, _ = find_swing_points(recent_prices, order=3)
    
    if len(price_highs_idx) < 2:
        return {'detected': False, 'strength': 0, 'description': ''}
    
    # Get last two swing highs
    price_high1_idx = price_highs_idx[-2]
    price_high2_idx = price_highs_idx[-1]
    
    price_high1 = recent_prices[price_high1_idx]
    price_high2 = recent_prices[price_high2_idx]
    
    # Check if price made higher high
    if price_high2 <= price_high1:
        return {'detected': False, 'strength': 0, 'description': ''}
    
    # Check RSI at these points
    rsi_at_high1 = recent_rsi[price_high1_idx]
    rsi_at_high2 = recent_rsi[price_high2_idx]
    
    # Bearish divergence: price higher high, RSI lower high
    if rsi_at_high2 < rsi_at_high1:
        strength = 1
        description = "Bearish Divergence Detected"
        
        # Calculate strength based on how significant
        price_change = abs((price_high2 - price_high1) / price_high1 * 100)
        rsi_change = rsi_at_high1 - rsi_at_high2
        
        if price_change > 5 and rsi_change > 10:
            strength = 3
            description = "Strong Bearish Divergence - Major reversal signal"
        elif price_change > 3 or rsi_change > 5:
            strength = 2
            description = "Moderate Bearish Divergence"
        
        return {
            'detected': True,
            'strength': strength,
            'type': 'BEARISH',
            'description': description,
            'price_high1': price_high1,
            'price_high2': price_high2,
            'rsi_high1': rsi_at_high1,
            'rsi_high2': rsi_at_high2,
            'price_change_pct': price_change,
            'rsi_change': rsi_change
        }
    
    return {'detected': False, 'strength': 0, 'description': ''}

def calculate_divergence(data, lookback: int = 20) -> Tuple[Dict, Dict]:
    """
    Calculate both bullish and bearish divergence
    Returns: (bullish_div, bearish_div)
    """
    if data.empty or len(data) < lookback:
        return {'detected': False}, {'detected': False}
    
    prices = data['close'].values
    close_prices = data['close'].values
    
    # Calculate RSI if not already in data
    if 'RSI' in data.columns:
        rsi = data['RSI'].values
    else:
        # Calculate RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi = rsi.fillna(50).values
    
    bullish = detect_bullish_divergence(prices, rsi, lookback)
    bearish = detect_bearish_divergence(prices, rsi, lookback)
    
    return bullish, bearish
