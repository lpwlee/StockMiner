"""
Chart generation with dark mode colors
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.indicators.divergence import find_swing_points

def find_divergence_points(data, lookback=60):
    """Find divergence points for charting"""
    if data.empty or len(data) < 20:
        return [], []
    
    prices = data['close'].values
    dates = data['time_key'].values
    
    # Calculate RSI
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    rsi_values = rsi.fillna(50).values
    
    price_highs, price_lows = find_swing_points(prices, order=3)
    
    bullish_divergence = []
    bearish_divergence = []
    
    if len(price_lows) >= 2:
        for i in range(1, len(price_lows)):
            idx1 = price_lows[i-1]
            idx2 = price_lows[i]
            
            if idx1 < len(prices) and idx2 < len(prices):
                if prices[idx2] < prices[idx1] and rsi_values[idx2] > rsi_values[idx1]:
                    bullish_divergence.append({
                        'price_idx1': idx1, 'price_idx2': idx2,
                        'price1': prices[idx1], 'price2': prices[idx2],
                        'rsi1': rsi_values[idx1], 'rsi2': rsi_values[idx2],
                        'date1': dates[idx1], 'date2': dates[idx2],
                        'strength': min(3, int(abs(prices[idx2] - prices[idx1]) / prices[idx1] * 10))
                    })
    
    if len(price_highs) >= 2:
        for i in range(1, len(price_highs)):
            idx1 = price_highs[i-1]
            idx2 = price_highs[i]
            
            if idx1 < len(prices) and idx2 < len(prices):
                if prices[idx2] > prices[idx1] and rsi_values[idx2] < rsi_values[idx1]:
                    bearish_divergence.append({
                        'price_idx1': idx1, 'price_idx2': idx2,
                        'price1': prices[idx1], 'price2': prices[idx2],
                        'rsi1': rsi_values[idx1], 'rsi2': rsi_values[idx2],
                        'date1': dates[idx1], 'date2': dates[idx2],
                        'strength': min(3, int(abs(prices[idx2] - prices[idx1]) / prices[idx1] * 10))
                    })
    
    return bullish_divergence, bearish_divergence

def create_candlestick_chart(data, stock_code, display_name, stock_info=None):
    """Create candlestick chart with divergence lines - Dark mode optimized"""
    if data.empty:
        return go.Figure()
    
    # Calculate RSI
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # Find divergence points
    bullish_div, bearish_div = find_divergence_points(data)
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(f'{stock_code} - {display_name}', 'Volume', 'RSI (14)')
    )
    
    # Candlestick chart - dark mode colors
    fig.add_trace(
        go.Candlestick(
            x=data['time_key'],
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name='Price',
            increasing_line_color='#00ff88',
            decreasing_line_color='#ff6666',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Add moving averages with better visibility
    if len(data) >= 20:
        data['SMA_20'] = data['close'].rolling(window=20).mean()
        fig.add_trace(
            go.Scatter(
                x=data['time_key'], 
                y=data['SMA_20'], 
                name='SMA 20',
                line=dict(color='#ffa500', width=1.5)
            ),
            row=1, col=1
        )
    
    if len(data) >= 50:
        data['SMA_50'] = data['close'].rolling(window=50).mean()
        fig.add_trace(
            go.Scatter(
                x=data['time_key'], 
                y=data['SMA_50'], 
                name='SMA 50',
                line=dict(color='#00bfff', width=1.5)
            ),
            row=1, col=1
        )
    
    # Volume bars with better colors
    colors = ['#ff6666' if close < open else '#00ff88' for close, open in zip(data['close'], data['open'])]
    fig.add_trace(
        go.Bar(
            x=data['time_key'],
            y=data['volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.5,
            showlegend=False
        ),
        row=2, col=1
    )
    
    # RSI line
    fig.add_trace(
        go.Scatter(
            x=data['time_key'],
            y=data['RSI'],
            name='RSI',
            line=dict(color='#c84bff', width=2)
        ),
        row=3, col=1
    )
    
    # Draw BULLISH DIVERGENCE with lime green
    for div in bullish_div:
        fig.add_trace(
            go.Scatter(
                x=[div['date1'], div['date2']],
                y=[div['price1'], div['price2']],
                mode='lines+markers',
                line=dict(color='#00ff88', width=2, dash='dash'),
                marker=dict(size=10, symbol='arrow-up', color='#00ff88'),
                showlegend=False
            ),
            row=1, col=1
        )
        fig.add_annotation(
            x=div['date2'],
            y=div['price2'],
            text=f"🟢 BULLISH DIV (S{div['strength']})",
            showarrow=True,
            arrowhead=2,
            arrowcolor="#00ff88",
            ax=20,
            ay=-40,
            bgcolor="rgba(0,255,136,0.2)",
            font=dict(size=10, color="#00ff88"),
            borderwidth=1,
            borderpad=4,
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=[div['date1'], div['date2']],
                y=[div['rsi1'], div['rsi2']],
                mode='lines+markers',
                line=dict(color='#00ff88', width=2, dash='dash'),
                marker=dict(size=8, color='#00ff88'),
                showlegend=False
            ),
            row=3, col=1
        )
    
    # Draw BEARISH DIVERGENCE with red
    for div in bearish_div:
        fig.add_trace(
            go.Scatter(
                x=[div['date1'], div['date2']],
                y=[div['price1'], div['price2']],
                mode='lines+markers',
                line=dict(color='#ff6666', width=2, dash='dash'),
                marker=dict(size=10, symbol='arrow-down', color='#ff6666'),
                showlegend=False
            ),
            row=1, col=1
        )
        fig.add_annotation(
            x=div['date2'],
            y=div['price2'],
            text=f"🔴 BEARISH DIV (S{div['strength']})",
            showarrow=True,
            arrowhead=2,
            arrowcolor="#ff6666",
            ax=20,
            ay=40,
            bgcolor="rgba(255,102,102,0.2)",
            font=dict(size=10, color="#ff6666"),
            borderwidth=1,
            borderpad=4,
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=[div['date1'], div['date2']],
                y=[div['rsi1'], div['rsi2']],
                mode='lines+markers',
                line=dict(color='#ff6666', width=2, dash='dash'),
                marker=dict(size=8, color='#ff6666'),
                showlegend=False
            ),
            row=3, col=1
        )
    
    # Add RSI levels with better visibility
    fig.add_hline(y=70, line_dash="dash", line_color="#ff6666", row=3, col=1, annotation_text="Overbought")
    fig.add_hline(y=30, line_dash="dash", line_color="#00ff88", row=3, col=1, annotation_text="Oversold")
    fig.add_hrect(y0=70, y1=100, fillcolor="#ff6666", opacity=0.1, row=3, col=1)
    fig.add_hrect(y0=0, y1=30, fillcolor="#00ff88", opacity=0.1, row=3, col=1)
    
    current_price = data['close'].iloc[-1]
    current_rsi = data['RSI'].iloc[-1] if not pd.isna(data['RSI'].iloc[-1]) else 50
    
    # Dark mode layout
    fig.update_layout(
        title=dict(
            text=f'{stock_code} - {display_name} | Price: ${current_price:.2f} | RSI: {current_rsi:.1f}',
            font=dict(color='#ffffff')
        ),
        template='plotly_dark',
        height=900,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#ffffff')),
        paper_bgcolor='#1e1e1e',
        plot_bgcolor='#1e1e1e',
        xaxis=dict(gridcolor='#333333'),
        yaxis=dict(gridcolor='#333333')
    )
    
    fig.update_xaxes(title_text="Date", row=2, col=1, color='#ffffff')
    fig.update_xaxes(title_text="Date", row=3, col=1, color='#ffffff')
    fig.update_yaxes(title_text="Price (HKD)", row=1, col=1, color='#ffffff')
    fig.update_yaxes(title_text="Volume", row=2, col=1, color='#ffffff')
    fig.update_yaxes(title_text="RSI", row=3, col=1, color='#ffffff')
    
    # Add divergence legend
    if bullish_div or bearish_div:
        fig.add_annotation(
            x=0.02,
            y=0.98,
            xref="paper",
            yref="paper",
            text="📊 Divergence Legend:<br>🟢 Bullish: Price ↓ RSI ↑ = Buy Signal<br>🔴 Bearish: Price ↑ RSI ↓ = Sell Signal<br>💪 Strength S1-S3 (S3=Strongest)",
            showarrow=False,
            font=dict(size=10, color="#ffffff"),
            bgcolor="rgba(0,0,0,0.8)",
            bordercolor="#444",
            borderwidth=1
        )
    
    return fig
