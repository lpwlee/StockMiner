"""
Sorting logic for stocks
"""

import pandas as pd

def calculate_sorting_metrics(df):
    """Calculate additional metrics for sorting"""
    if df.empty:
        return df
    
    df_copy = df.copy()
    
    # Calculate divergence strength
    df_copy['Divergence_Strength'] = 0
    df_copy['Divergence_Type'] = 'None'
    
    if 'Bullish_Divergence' in df_copy.columns:
        bullish_mask = df_copy['Bullish_Divergence'] == True
        df_copy.loc[bullish_mask, 'Divergence_Strength'] = df_copy.loc[bullish_mask, 'Bullish_Strength']
        df_copy.loc[bullish_mask, 'Divergence_Type'] = 'Bullish'
    
    if 'Bearish_Divergence' in df_copy.columns:
        bearish_mask = df_copy['Bearish_Divergence'] == True
        df_copy.loc[bearish_mask, 'Divergence_Strength'] = df_copy.loc[bearish_mask, 'Bearish_Strength']
        df_copy.loc[bearish_mask, 'Divergence_Type'] = 'Bearish'
    
    # Calculate signal strength
    df_copy['Signal_Strength'] = df_copy[['Rise_Score', 'Fall_Score']].max(axis=1)
    df_copy['Signal_Type'] = df_copy.apply(
        lambda x: 'BUY' if x['Rise_Score'] > x['Fall_Score'] 
        else 'SELL' if x['Fall_Score'] > x['Rise_Score'] 
        else 'NEUTRAL', axis=1
    )
    
    return df_copy

def sort_stocks(df, sort_by):
    """Sort stocks by specified criteria"""
    if df.empty:
        return df
    
    # Calculate metrics first
    df_sorted = calculate_sorting_metrics(df)
    
    # Apply sorting
    if sort_by == 'code':
        df_sorted = df_sorted.sort_values('Code')
    elif sort_by == 'divergence_strength':
        # Sort by divergence strength (highest first), then by type (bullish first)
        df_sorted = df_sorted.sort_values(
            ['Divergence_Strength', 'Divergence_Type'], 
            ascending=[False, True]
        )
    elif sort_by == 'buy_signal':
        df_sorted = df_sorted.sort_values('Rise_Score', ascending=False)
    elif sort_by == 'sell_signal':
        df_sorted = df_sorted.sort_values('Fall_Score', ascending=False)
    elif sort_by == 'signal_strength':
        df_sorted = df_sorted.sort_values('Signal_Strength', ascending=False)
    elif sort_by == 'rsi_oversold':
        df_sorted = df_sorted.sort_values('RSI', ascending=True)
    elif sort_by == 'rsi_overbought':
        df_sorted = df_sorted.sort_values('RSI', ascending=False)
    elif sort_by == 'momentum':
        df_sorted = df_sorted.sort_values('Return_10D', ascending=False)
    elif sort_by == 'volume':
        df_sorted = df_sorted.sort_values('Volume_Ratio', ascending=False)
    else:
        df_sorted = df_sorted.sort_values('Code')
    
    return df_sorted

def get_sort_options():
    """Return available sorting options"""
    return [
        {'label': '📋 Stock Code (A-Z)', 'value': 'code'},
        {'label': '⚡ Strongest Divergence', 'value': 'divergence_strength'},
        {'label': '🟢 Strongest Buy Signal', 'value': 'buy_signal'},
        {'label': '🔴 Strongest Sell Signal', 'value': 'sell_signal'},
        {'label': '🎯 Overall Signal Strength', 'value': 'signal_strength'},
        {'label': '📉 Most Oversold (RSI < 30)', 'value': 'rsi_oversold'},
        {'label': '📈 Most Overbought (RSI > 70)', 'value': 'rsi_overbought'},
        {'label': '🚀 Best Momentum (10D Return)', 'value': 'momentum'},
        {'label': '📊 Highest Volume', 'value': 'volume'}
    ]
