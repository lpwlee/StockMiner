"""
Display formatting for stocks and tables - Dark mode optimized
"""

import dash_bootstrap_components as dbc
from dash import html

def create_stock_table(stocks_df):
    """Create HTML table with clickable stock codes - Dark mode optimized"""
    if not stocks_df or len(stocks_df) == 0:
        return html.P("No stocks found. Run analysis first.", className="text-light"), []
    
    total_count = len(stocks_df)
    stock_codes = []
    
    table_header = [
        html.Thead(html.Tr([
            html.Th("Code", style={"position": "sticky", "top": 0, "background": "#1e1e1e", "color": "#ffffff", "zIndex": 1}),
            html.Th("Company", style={"position": "sticky", "top": 0, "background": "#1e1e1e", "color": "#ffffff", "zIndex": 1}),
            html.Th("Price", style={"position": "sticky", "top": 0, "background": "#1e1e1e", "color": "#ffffff", "zIndex": 1}),
            html.Th("RSI", style={"position": "sticky", "top": 0, "background": "#1e1e1e", "color": "#ffffff", "zIndex": 1}),
            html.Th("10D%", style={"position": "sticky", "top": 0, "background": "#1e1e1e", "color": "#ffffff", "zIndex": 1}),
            html.Th("Rise%", style={"position": "sticky", "top": 0, "background": "#1e1e1e", "color": "#ffffff", "zIndex": 1}),
            html.Th("Fall%", style={"position": "sticky", "top": 0, "background": "#1e1e1e", "color": "#ffffff", "zIndex": 1}),
            html.Th("Signal", style={"position": "sticky", "top": 0, "background": "#1e1e1e", "color": "#ffffff", "zIndex": 1}),
            html.Th("Divergence", style={"position": "sticky", "top": 0, "background": "#1e1e1e", "color": "#ffffff", "zIndex": 1})
        ]))
    ]
    
    table_rows = []
    for stock in stocks_df:
        stock_codes.append(stock['Code'])
        
        # Determine signal badge with better colors for dark mode
        if stock['Signal_Type'] == 'BUY':
            signal_badge = html.Span("🟢 BUY", style={"color": "#00ff88", "fontWeight": "bold"})
        elif stock['Signal_Type'] == 'SELL':
            signal_badge = html.Span("🔴 SELL", style={"color": "#ff4444", "fontWeight": "bold"})
        else:
            signal_badge = html.Span("⚪ NEUTRAL", style={"color": "#aaaaaa"})
        
        # Divergence display with better colors
        if stock['Divergence_Type'] == 'Bullish':
            div_display = html.Span(f"🟢 Bullish (S{stock['Divergence_Strength']})", style={"color": "#00ff88"})
        elif stock['Divergence_Type'] == 'Bearish':
            div_display = html.Span(f"🔴 Bearish (S{stock['Divergence_Strength']})", style={"color": "#ff6666"})
        else:
            div_display = html.Span("None", style={"color": "#888888"})
        
        # Price color based on performance
        price_color = "#00ff88" if stock['Return_10D'] > 0 else "#ff6666" if stock['Return_10D'] < 0 else "#ffffff"
        
        # RSI color coding
        rsi = stock['RSI']
        if rsi < 30:
            rsi_color = "#00ff88"  # Oversold - green
        elif rsi > 70:
            rsi_color = "#ff6666"  # Overbought - red
        else:
            rsi_color = "#ffffff"  # Neutral - white
        
        # Create button with pattern-matching ID
        button_id = {"type": "stock-btn", "index": stock['Code'].replace('.', '-')}
        
        clickable_code = html.Button(
            stock['Code'],
            id=button_id,
            n_clicks=0,
            style={
                'background': 'none',
                'border': 'none',
                'color': '#00bfff',
                'cursor': 'pointer',
                'text-decoration': 'underline',
                'font-family': 'monospace',
                'font-size': '12px',
                'padding': '0',
                'margin': '0'
            },
            title=f"Click to load chart for {stock['Code']}"
        )
        
        row = html.Tr([
            html.Td(clickable_code, style={"color": "#00bfff"}),
            html.Td(stock['Display_Name'][:50], title=stock['Display_Name'], style={"color": "#ffffff"}),
            html.Td(f"${stock['Price']:.2f}", style={"color": price_color}),
            html.Td(f"{stock['RSI']:.0f}", style={"color": rsi_color, "fontWeight": "bold"}),
            html.Td(f"{stock['Return_10D']:+.1f}%", style={"color": price_color}),
            html.Td(f"{stock['Rise_Score']:.0f}%", style={"color": "#00ff88"}),
            html.Td(f"{stock['Fall_Score']:.0f}%", style={"color": "#ff6666"}),
            html.Td(signal_badge),
            html.Td(div_display)
        ])
        table_rows.append(row)
    
    table_body = [html.Tbody(table_rows)]
    
    info_bar = html.Div([
        html.Small(f"📊 Total: {total_count} stocks", className="text-info fw-bold"),
        html.Small(" | Click on stock code to load chart", className="text-light ms-2")
    ], className="mb-2")
    
    # Dark mode table styling
    table_container = html.Div([
        info_bar,
        dbc.Table(table_header + table_body, bordered=True, hover=True, 
                  striped=True, size="sm", className="table-dark", 
                  style={"fontSize": "12px", "color": "#ffffff", "backgroundColor": "#1e1e1e"})
    ], style={"maxHeight": "600px", "overflowY": "auto", "border": "1px solid #444", "borderRadius": "5px", "backgroundColor": "#1e1e1e"})
    
    return table_container, stock_codes

def create_stock_info_card(stock_info, display_name):
    """Create stock information card - Dark mode optimized"""
    if not stock_info:
        return dbc.Card([dbc.CardBody([html.P("No data available", className="text-muted")])], className="bg-dark text-light")
    
    # Divergence badge with better colors
    div_badge = ""
    if stock_info.get('Bullish_Divergence'):
        div_badge = dbc.Badge("🔥 BULLISH DIVERGENCE", color="success", className="mb-2 w-100")
    elif stock_info.get('Bearish_Divergence'):
        div_badge = dbc.Badge("⚠️ BEARISH DIVERGENCE", color="danger", className="mb-2 w-100")
    
    # RSI color coding
    rsi = stock_info.get('RSI', 50)
    if rsi < 30:
        rsi_color = "#00ff88"
        rsi_text = f"{rsi:.0f} (Oversold)"
    elif rsi > 70:
        rsi_color = "#ff6666"
        rsi_text = f"{rsi:.0f} (Overbought)"
    else:
        rsi_color = "#ffffff"
        rsi_text = f"{rsi:.0f}"
    
    # Return color coding
    return_val = stock_info.get('Return_10D', 0)
    return_color = "#00ff88" if return_val > 0 else "#ff6666" if return_val < 0 else "#ffffff"
    
    return dbc.Card([
        dbc.CardBody([
            html.H5(f"{stock_info['Code']} - {display_name}", className="card-title", style={"color": "#00bfff"}),
            div_badge,
            html.Hr(style={"borderColor": "#444"}),
            dbc.Row([
                dbc.Col([html.Strong("Price:", style={"color": "#aaaaaa"}), html.P(f"${stock_info['Price']:.2f}", style={"color": "#ffffff"})], width=3),
                dbc.Col([html.Strong("RSI:", style={"color": "#aaaaaa"}), html.P(rsi_text, style={"color": rsi_color, "fontWeight": "bold"})], width=3),
                dbc.Col([html.Strong("10D Return:", style={"color": "#aaaaaa"}), html.P(f"{return_val:+.1f}%", style={"color": return_color})], width=3),
                dbc.Col([html.Strong("Volume Ratio:", style={"color": "#aaaaaa"}), html.P(f"{stock_info.get('Volume_Ratio', 1):.1f}x", style={"color": "#ffffff"})], width=3),
            ]),
            html.Hr(style={"borderColor": "#444"}),
            html.Div([
                html.Strong("Divergence Details:", className="text-info"),
                html.Br(),
                html.Small(stock_info.get('Bullish_Div_Desc', '') or stock_info.get('Bearish_Div_Desc', 'No divergence detected'), style={"color": "#aaaaaa"}),
                html.Br(),
                html.Strong("Trading Signals:", className="text-info mt-2"),
                html.Br(),
                html.Small(stock_info.get('Signal_Reasons', 'No signals'), style={"color": "#aaaaaa"})
            ])
        ])
    ], className="bg-dark text-light", style={"border": "1px solid #444"})

def create_dropdown_options(stocks):
    """Create dropdown options from stocks"""
    return [{'label': f"{s['Code']} - {s['Display_Name'][:40]} (${s['Price']:.2f})", 'value': s['Code']} 
            for s in stocks] if stocks else []
