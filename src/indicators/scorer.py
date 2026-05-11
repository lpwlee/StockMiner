from typing import Tuple

def calculate_scores(indicators: dict) -> Tuple[float, float, str]:
    rise_score = 50.0
    fall_score = 50.0
    reasons_rise = []
    reasons_fall = []
    
    rsi = indicators.get('rsi', 50)
    ret_10d = indicators.get('return_10d', 0)
    vol_ratio = indicators.get('volume_ratio', 1)
    
    # RSI signals
    if rsi < 30:
        rise_score += 20
        reasons_rise.append(f"Oversold RSI={rsi:.0f}")
    elif rsi < 40:
        rise_score += 10
        reasons_rise.append(f"Near oversold RSI={rsi:.0f}")
    elif rsi > 70:
        fall_score += 20
        reasons_fall.append(f"Overbought RSI={rsi:.0f}")
    elif rsi > 60:
        fall_score += 10
        reasons_fall.append(f"Near overbought RSI={rsi:.0f}")
    
    # Return signals
    if ret_10d < -5:
        rise_score += 15
        reasons_rise.append(f"Drop {ret_10d:+.1f}%")
    elif ret_10d < -2:
        rise_score += 8
        reasons_rise.append(f"Dip {ret_10d:+.1f}%")
    elif ret_10d > 10:
        fall_score += 15
        reasons_fall.append(f"Rally {ret_10d:+.1f}%")
    elif ret_10d > 5:
        fall_score += 8
        reasons_fall.append(f"Rise {ret_10d:+.1f}%")
    
    # Volume signals
    if vol_ratio > 1.5:
        if ret_10d < 0:
            rise_score += 10
            reasons_rise.append(f"High volume {vol_ratio:.1f}x")
        else:
            fall_score += 10
            reasons_fall.append(f"High volume {vol_ratio:.1f}x")
    
    rise_score = max(0, min(100, rise_score))
    fall_score = max(0, min(100, fall_score))
    
    reasoning = ""
    if reasons_rise:
        reasoning += f"📈 {', '.join(reasons_rise[:2])}"
    if reasons_fall:
        if reasoning:
            reasoning += " | "
        reasoning += f"📉 {', '.join(reasons_fall[:2])}"
    
    return rise_score, fall_score, reasoning
