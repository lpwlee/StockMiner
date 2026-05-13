"""
Filtering logic for stocks - with improved labels for dark mode
"""

def filter_stocks(df, filter_type):
    """Filter stocks by type with better logic"""
    if df.empty:
        return df
    
    if filter_type == "buy":
        filtered = df[
            ((df['Confirm_Buy'] == True) | (df['Bullish_Divergence'] == True)) &
            (df['Fall_Score'] < 70) &
            (df['Bearish_Divergence'] == False)
        ]
    elif filter_type == "sell":
        filtered = df[
            ((df['Confirm_Sell'] == True) | (df['Bearish_Divergence'] == True)) &
            (df['Rise_Score'] < 70) &
            (df['Bullish_Divergence'] == False)
        ]
    elif filter_type == "divergence":
        filtered = df[
            (df['Bullish_Divergence'] == True) | 
            (df['Bearish_Divergence'] == True)
        ]
    else:  # "all"
        filtered = df
    
    print(f"Filter '{filter_type}' returned {len(filtered)} stocks")
    return filtered

def get_filter_options():
    """Return available filtering options with icons for dark mode"""
    return [
        {'label': ' 🟢 Strong Buy (Bullish)', 'value': 'buy'},
        {'label': ' 🔴 Strong Sell (Bearish)', 'value': 'sell'},
        {'label': ' 🔄 Any Divergence', 'value': 'divergence'},
        {'label': ' 📊 All Stocks', 'value': 'all'}
    ]
