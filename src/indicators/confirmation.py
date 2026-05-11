"""
Confirmation signals for buy and sell decisions with divergence
"""

def get_confirm_buy_signal(row):
    """
    Generate confirmed buy signal based on multiple indicators
    Now includes divergence detection
    """
    reasons = []
    strength = 0
    
    # RSI conditions (oversold)
    rsi = row['RSI']
    if rsi < 25:
        reasons.append(f"Extremely oversold (RSI={rsi:.0f})")
        strength += 3
    elif rsi < 30:
        reasons.append(f"Oversold (RSI={rsi:.0f})")
        strength += 2
    elif rsi < 35:
        reasons.append(f"Near oversold (RSI={rsi:.0f})")
        strength += 1
    
    # Price drop conditions
    return_10d = row['Return_10D']
    if return_10d < -8:
        reasons.append(f"Sharp drop ({return_10d:+.1f}% in 10 days)")
        strength += 3
    elif return_10d < -5:
        reasons.append(f"Significant drop ({return_10d:+.1f}% in 10 days)")
        strength += 2
    elif return_10d < -3:
        reasons.append(f"Moderate drop ({return_10d:+.1f}% in 10 days)")
        strength += 1
    
    # Volume confirmation (capitulation)
    vol_ratio = row.get('Volume_Ratio', 1)
    if vol_ratio > 2.0 and return_10d < 0:
        reasons.append(f"High volume capitulation ({vol_ratio:.1f}x)")
        strength += 3
    elif vol_ratio > 1.5 and return_10d < 0:
        reasons.append(f"High volume drop ({vol_ratio:.1f}x)")
        strength += 2
    
    # Rise score confirmation
    rise_score = row['Rise_Score']
    if rise_score >= 75:
        reasons.append(f"Strong rise signal ({rise_score:.0f}%)")
        strength += 3
    elif rise_score >= 65:
        reasons.append(f"Good rise signal ({rise_score:.0f}%)")
        strength += 2
    elif rise_score >= 55:
        reasons.append(f"Moderate rise signal ({rise_score:.0f}%)")
        strength += 1
    
    # Net score confirmation
    net_score = row['Net_Score']
    if net_score > 30:
        reasons.append(f"Strong net score ({net_score:+.0f})")
        strength += 2
    elif net_score > 15:
        reasons.append(f"Good net score ({net_score:+.0f})")
        strength += 1
    
    # ★ NEW: Bullish Divergence (Strongest signal)
    if row.get('Bullish_Divergence', False):
        div_strength = row.get('Bullish_Strength', 1)
        if div_strength >= 3:
            reasons.append("🔥 Strong Bullish Divergence (Major reversal signal)")
            strength += 5
        elif div_strength >= 2:
            reasons.append("✅ Bullish Divergence Detected")
            strength += 3
        else:
            reasons.append("Bullish Divergence Detected")
            strength += 2
    
    # Determine if confirmed buy
    is_confirm_buy = strength >= 5 and len(reasons) >= 2
    
    # Determine confidence level
    if strength >= 10 or (row.get('Bullish_Divergence', False) and strength >= 7):
        confidence = "HIGH"
    elif strength >= 5:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"
    
    return is_confirm_buy, strength, confidence, reasons


def get_confirm_sell_signal(row):
    """
    Generate confirmed sell signal based on multiple indicators
    Now includes divergence detection
    """
    reasons = []
    strength = 0
    
    # RSI conditions (overbought)
    rsi = row['RSI']
    if rsi > 80:
        reasons.append(f"Extremely overbought (RSI={rsi:.0f})")
        strength += 3
    elif rsi > 75:
        reasons.append(f"Very overbought (RSI={rsi:.0f})")
        strength += 2
    elif rsi > 70:
        reasons.append(f"Overbought (RSI={rsi:.0f})")
        strength += 1
    
    # Price rally conditions
    return_10d = row['Return_10D']
    if return_10d > 15:
        reasons.append(f"Sharp rally ({return_10d:+.1f}% in 10 days)")
        strength += 3
    elif return_10d > 10:
        reasons.append(f"Strong rally ({return_10d:+.1f}% in 10 days)")
        strength += 2
    elif return_10d > 7:
        reasons.append(f"Significant rally ({return_10d:+.1f}% in 10 days)")
        strength += 1
    
    # Volume confirmation (distribution)
    vol_ratio = row.get('Volume_Ratio', 1)
    if vol_ratio > 2.0 and return_10d > 0:
        reasons.append(f"High volume rally ({vol_ratio:.1f}x)")
        strength += 3
    elif vol_ratio > 1.5 and return_10d > 0:
        reasons.append(f"High volume up move ({vol_ratio:.1f}x)")
        strength += 2
    
    # Fall score confirmation
    fall_score = row['Fall_Score']
    if fall_score >= 75:
        reasons.append(f"Strong fall signal ({fall_score:.0f}%)")
        strength += 3
    elif fall_score >= 65:
        reasons.append(f"Good fall signal ({fall_score:.0f}%)")
        strength += 2
    elif fall_score >= 55:
        reasons.append(f"Moderate fall signal ({fall_score:.0f}%)")
        strength += 1
    
    # Net score confirmation (negative)
    net_score = row['Net_Score']
    if net_score < -30:
        reasons.append(f"Strong net score ({net_score:+.0f})")
        strength += 2
    elif net_score < -15:
        reasons.append(f"Good net score ({net_score:+.0f})")
        strength += 1
    
    # ★ NEW: Bearish Divergence (Strongest signal)
    if row.get('Bearish_Divergence', False):
        div_strength = row.get('Bearish_Strength', 1)
        if div_strength >= 3:
            reasons.append("🔥 Strong Bearish Divergence (Major reversal signal)")
            strength += 5
        elif div_strength >= 2:
            reasons.append("⚠️ Bearish Divergence Detected")
            strength += 3
        else:
            reasons.append("Bearish Divergence Detected")
            strength += 2
    
    # Determine if confirmed sell
    is_confirm_sell = strength >= 5 and len(reasons) >= 2
    
    # Determine confidence level
    if strength >= 10 or (row.get('Bearish_Divergence', False) and strength >= 7):
        confidence = "HIGH"
    elif strength >= 5:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"
    
    return is_confirm_sell, strength, confidence, reasons


def get_signal_summary(row):
    """Get comprehensive signal summary including divergence"""
    is_buy, buy_strength, buy_confidence, buy_reasons = get_confirm_buy_signal(row)
    is_sell, sell_strength, sell_confidence, sell_reasons = get_confirm_sell_signal(row)
    
    # Prioritize divergence signals
    if row.get('Bullish_Divergence', False) and not row.get('Bearish_Divergence', False):
        return {
            'action': 'DIVERGENCE BUY',
            'confidence': 'HIGH' if row.get('Bullish_Strength', 0) >= 2 else 'MEDIUM',
            'strength': row.get('Bullish_Strength', 0) + 3,
            'reasons': [f"Bullish Divergence detected"] + buy_reasons[:2],
            'color': '🟢'
        }
    elif row.get('Bearish_Divergence', False) and not row.get('Bullish_Divergence', False):
        return {
            'action': 'DIVERGENCE SELL',
            'confidence': 'HIGH' if row.get('Bearish_Strength', 0) >= 2 else 'MEDIUM',
            'strength': row.get('Bearish_Strength', 0) + 3,
            'reasons': [f"Bearish Divergence detected"] + sell_reasons[:2],
            'color': '🔴'
        }
    elif is_buy and buy_strength > sell_strength:
        return {
            'action': 'CONFIRM BUY',
            'confidence': buy_confidence,
            'strength': buy_strength,
            'reasons': buy_reasons,
            'color': '🟢'
        }
    elif is_sell and sell_strength > buy_strength:
        return {
            'action': 'CONFIRM SELL',
            'confidence': sell_confidence,
            'strength': sell_strength,
            'reasons': sell_reasons,
            'color': '🔴'
        }
    elif is_buy or buy_strength > 3:
        return {
            'action': 'WEAK BUY',
            'confidence': 'LOW',
            'strength': buy_strength,
            'reasons': buy_reasons[:2],
            'color': '🟡'
        }
    elif is_sell or sell_strength > 3:
        return {
            'action': 'WEAK SELL',
            'confidence': 'LOW',
            'strength': sell_strength,
            'reasons': sell_reasons[:2],
            'color': '🟡'
        }
    else:
        return {
            'action': 'NEUTRAL',
            'confidence': 'NONE',
            'strength': 0,
            'reasons': [],
            'color': '⚪'
        }
