"""
Simple Working Dashboard - No Complexity
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import webbrowser
import threading
import time
import json
import os

# Import your existing modules
from src.core.analyzer_hybrid import HybridAnalyzer
from src.indicators.divergence import find_swing_points

class SimpleDashboard:
    def __init__(self):
        self.analyzer = HybridAnalyzer()
        self.app = None
        self.stock_data = None
        self.load_cached_data()
    
    def load_cached_data(self):
        """Load cached analysis data"""
        cache_file = "data/cache/latest_analysis.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.stock_data = pd.DataFrame(data['stocks'])
                print(f"✅ Loaded {len(self.stock_data)} stocks from cache")
                return True
            except:
                pass
        return False
    
    def get_candlestick_chart(self, stock_code):
        """Simple candlestick chart"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=120)
        
        # Get data
        data = self.analyzer.yahoo_client.get_history_kline(
            stock_code,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d'),
            use_cache=True
        )
        
        if data.empty:
            return go.Figure()
        
        # Calculate RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Create figure
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.7, 0.3],
            subplot_titles=(f'{stock_code}', 'RSI')
        )
        
        # Candlestick
        fig.add_trace(
            go.Candlestick(
                x=data['time_key'],
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name='Price'
            ),
            row=1, col=1
        )
        
        # RSI
        fig.add_trace(
            go.Scatter(x=data['time_key'], y=rsi, name='RSI', line=dict(color='purple', width=2)),
            row=2, col=1
        )
        
        # RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1, annotation_text="Overbought")
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1, annotation_text="Oversold")
        
        current_price = data['close'].iloc[-1]
        current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
        
        fig.update_layout(
            title=f'{stock_code} | Price: ${current_price:.2f} | RSI: {current_rsi:.1f}',
            template='plotly_dark',
            height=600,
            xaxis_title='Date',
            yaxis_title='Price'
        )
        
        return fig
    
    def create_dashboard(self):
        """Create simple working dashboard"""
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
        
        # Get stock list for dropdown
        stock_options = []
        if self.stock_data is not None:
            stock_options = [{'label': f"{row['Code']} - {row.get('Name', row['Code'])}", 'value': row['Code']} 
                           for _, row in self.stock_data.head(200).iterrows()]
        
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col(html.H1("📈 StockMiner", className="text-center text-primary my-4"), width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Select Stock"),
                        dbc.CardBody([
                            dcc.Dropdown(
                                id='stock-selector',
                                options=stock_options,
                                placeholder='Choose a stock...',
                                className="mb-3"
                            ),
                            html.Div(id='stock-info', className="mt-2")
                        ])
                    ])
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Price Chart"),
                        dbc.CardBody([
                            dcc.Graph(id='price-chart')
                        ])
                    ])
                ], width=9)
            ])
        ], fluid=True)
        
        # Simple callback - just update chart when stock selected
        @self.app.callback(
            [Output('price-chart', 'figure'),
             Output('stock-info', 'children')],
            [Input('stock-selector', 'value')]
        )
        def update_chart(stock_code):
            if not stock_code:
                return go.Figure(), "Select a stock to view chart"
            
            # Get chart
            fig = self.get_candlestick_chart(stock_code)
            
            # Get stock info from cached data
            stock_info = ""
            if self.stock_data is not None:
                stock_row = self.stock_data[self.stock_data['Code'] == stock_code]
                if not stock_row.empty:
                    row = stock_row.iloc[0]
                    stock_info = html.Div([
                        html.Strong("Company: "), html.Span(row.get('Name', 'N/A')), html.Br(),
                        html.Strong("Price: "), html.Span(f"${row.get('Price', 0):.2f}"), html.Br(),
                        html.Strong("RSI: "), html.Span(f"{row.get('RSI', 0):.1f}"), html.Br(),
                        html.Strong("10D Return: "), html.Span(f"{row.get('Return_10D', 0):+.1f}%")
                    ])
            
            return fig, stock_info
        
        return self.app
    
    def run(self, port=8050):
        print("\n" + "="*60)
        print("🚀 Simple Stock Dashboard")
        print("="*60)
        
        app = self.create_dashboard()
        
        def open_browser():
            time.sleep(2)
            webbrowser.open(f'http://localhost:{port}')
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        print(f"\n✅ Dashboard: http://localhost:{port}")
        print("\nSimply select a stock from the dropdown to see the chart!")
        print("\nPress Ctrl+C to stop\n")
        
        app.run(debug=False, port=port)

if __name__ == "__main__":
    dashboard = SimpleDashboard()
    dashboard.run()
