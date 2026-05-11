"""
Interactive Dashboard with Candlestick Charts and Technical Analysis
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import webbrowser
import threading
import time

from src.core.analyzer_hybrid import HybridAnalyzer

class StockDashboard:
    """Interactive dashboard for stock analysis"""
    
    def __init__(self):
        self.analyzer = HybridAnalyzer()
        self.analyzed_stocks = None
        self.current_data = None
        self.app = None
        
    def load_analysis_data(self):
        """Load or run analysis to get stock data"""
        print("\n📊 Loading stock analysis data...")
        
        if self.analyzed_stocks is None:
            confirmed_buy, confirmed_sell = self.analyzer.analyze(
                "HK_STOCKS",
                max_stocks=200,
                top_n=50,
                min_volume=200000,
                force_refresh=False
            )
            
            all_results = pd.DataFrame(self.analyzer.all_results)
            self.analyzed_stocks = all_results
        
        return self.analyzed_stocks
    
    def get_filtered_stocks(self, filter_type):
        """Get stocks based on filter type"""
        if self.analyzed_stocks is None or self.analyzed_stocks.empty:
            return []
        
        if filter_type == "buy":
            # Priority: Bullish Divergence first, then oversold
            filtered = self.analyzed_stocks[
                (self.analyzed_stocks['Confirm_Buy'] == True) | 
                (self.analyzed_stocks['Bullish_Divergence'] == True) |
                (self.analyzed_stocks['Net_Score'] > 20)
            ].nlargest(30, 'Buy_Strength')
        elif filter_type == "sell":
            # Priority: Bearish Divergence first, then overbought
            filtered = self.analyzed_stocks[
                (self.analyzed_stocks['Confirm_Sell'] == True) | 
                (self.analyzed_stocks['Bearish_Divergence'] == True) |
                (self.analyzed_stocks['Net_Score'] < -20)
            ].nsmallest(30, 'Net_Score')
        else:
            filtered = self.analyzed_stocks.nlargest(50, 'Volume_Ratio')
        
        return filtered[['Code', 'Name', 'Price', 'RSI', 'Return_10D', 'Net_Score']].to_dict('records')
    
    def get_candlestick_chart(self, stock_code, days=90):
        """Generate candlestick chart with technical indicators"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        data = self.analyzer.yahoo_client.get_history_kline(
            stock_code,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d'),
            use_cache=True
        )
        
        if data.empty:
            return go.Figure(), None
        
        self.current_data = data
        
        # Calculate current RSI
        close_prices = data['close'].values
        if len(close_prices) >= 15:
            deltas = np.diff(close_prices[-15:])
            gains = deltas[deltas > 0].sum() / 14 if len(deltas[deltas > 0]) > 0 else 0
            losses = abs(deltas[deltas < 0].sum()) / 14 if len(deltas[deltas < 0]) > 0 else 0
            rs = gains / losses if losses != 0 else 100
            current_rsi = 100 - (100 / (1 + rs))
        else:
            current_rsi = 50
        
        # Get stock info
        stock_info = None
        if self.analyzed_stocks is not None and not self.analyzed_stocks.empty:
            stock_match = self.analyzed_stocks[self.analyzed_stocks['Code'] == stock_code]
            if not stock_match.empty:
                stock_info = stock_match.iloc[0].to_dict()
                stock_name = stock_info['Name']
            else:
                stock_name = stock_code
        else:
            stock_name = stock_code
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=(f'{stock_code} - {stock_name}', 'Volume', 'RSI (14)')
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=data['time_key'],
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name='Price',
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Add moving averages
        if len(data) >= 20:
            data['SMA_20'] = data['close'].rolling(window=20).mean()
            fig.add_trace(
                go.Scatter(
                    x=data['time_key'],
                    y=data['SMA_20'],
                    name='SMA 20',
                    line=dict(color='orange', width=1.5)
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
                    line=dict(color='blue', width=1.5)
                ),
                row=1, col=1
            )
        
        # Volume bars
        colors = ['red' if close < open else 'green' for close, open in zip(data['close'], data['open'])]
        fig.add_trace(
            go.Bar(
                x=data['time_key'],
                y=data['volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.5
            ),
            row=2, col=1
        )
        
        # RSI indicator
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        fig.add_trace(
            go.Scatter(
                x=data['time_key'],
                y=data['RSI'],
                name='RSI',
                line=dict(color='purple', width=2)
            ),
            row=3, col=1
        )
        
        # Add RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1, annotation_text="Overbought")
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1, annotation_text="Oversold")
        
        # Update layout
        current_price = data['close'].iloc[-1]
        fig.update_layout(
            title=f'{stock_code} - {stock_name} | Current: ${current_price:.2f} | RSI: {current_rsi:.1f}',
            template='plotly_dark',
            height=800,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig, stock_info
    
    def create_dashboard(self):
        """Create Dash dashboard"""
        
        self.load_analysis_data()
        
        initial_stocks = self.get_filtered_stocks("buy")
        initial_options = [{'label': f"{s['Code']} - {s['Name'][:30]} (${s['Price']:.2f})", 'value': s['Code']} 
                          for s in initial_stocks[:20]]
        
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
        
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col(html.H1("📈 StockMiner - Divergence Trading Dashboard", 
                               className="text-center text-primary mb-4"), width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🎯 Stock Selection"),
                        dbc.CardBody([
                            html.Label("Select Signal Type:", className="fw-bold"),
                            dcc.RadioItems(
                                id='signal-type',
                                options=[
                                    {'label': '🟢 Buy Signals (Divergence/Oversold)', 'value': 'buy'},
                                    {'label': '🔴 Sell Signals (Divergence/Overbought)', 'value': 'sell'},
                                    {'label': '📊 All Active Stocks', 'value': 'all'}
                                ],
                                value='buy',
                                inline=True,
                                className="mb-3"
                            ),
                            html.Label("Select Stock:", className="fw-bold mt-2"),
                            dcc.Dropdown(
                                id='stock-dropdown',
                                options=initial_options,
                                placeholder='Select a stock to analyze...',
                                className="mb-3"
                            ),
                            html.Div(id='stock-info', className="mt-3"),
                        ])
                    ], className="mb-4")
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📊 Technical Analysis Chart"),
                        dbc.CardBody([
                            dcc.Loading(
                                id="loading-chart",
                                type="circle",
                                children=[dcc.Graph(id='candlestick-chart')]
                            )
                        ])
                    ])
                ], width=9)
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📈 Key Indicators"),
                        dbc.CardBody(id='indicators-summary')
                    ])
                ], width=12)
            ], className="mt-3"),
            
            dbc.Row([
                dbc.Col([
                    html.Footer(
                        "⚠️ Divergence signals are leading indicators. Wait for confirmation.",
                        className="text-center text-muted mt-4"
                    )
                ], width=12)
            ])
        ], fluid=True, className="p-4")
        
        @self.app.callback(
            Output('stock-dropdown', 'options'),
            [Input('signal-type', 'value')]
        )
        def update_stock_list(signal_type):
            stocks = self.get_filtered_stocks(signal_type)
            return [{'label': f"{s['Code']} - {s['Name'][:30]} (${s['Price']:.2f})", 'value': s['Code']} 
                    for s in stocks[:50]]
        
        @self.app.callback(
            [Output('candlestick-chart', 'figure'),
             Output('stock-info', 'children'),
             Output('indicators-summary', 'children')],
            [Input('stock-dropdown', 'value')]
        )
        def update_chart(stock_code):
            if not stock_code:
                return go.Figure(), "", ""
            
            fig, stock_info = self.get_candlestick_chart(stock_code)
            
            if stock_info and isinstance(stock_info, dict):
                # Check for divergence
                div_text = ""
                if stock_info.get('Bullish_Divergence'):
                    div_text = f"🔥 BULLISH DIVERGENCE DETECTED (Strength: {stock_info.get('Bullish_Strength', 0)})"
                elif stock_info.get('Bearish_Divergence'):
                    div_text = f"⚠️ BEARISH DIVERGENCE DETECTED (Strength: {stock_info.get('Bearish_Strength', 0)})"
                
                info_card = dbc.Card([
                    dbc.CardBody([
                        html.H5(f"📊 {stock_info['Code']} - {stock_info['Name']}", className="card-title"),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col([html.Strong("Price:"), html.Br(), html.H4(f"${stock_info['Price']:.2f}")], width=4),
                            dbc.Col([html.Strong("RSI:"), html.Br(), html.H4(f"{stock_info['RSI']:.0f}")], width=4),
                            dbc.Col([html.Strong("10D Return:"), html.Br(), html.H4(f"{stock_info['Return_10D']:+.1f}%")], width=4),
                        ]),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col([html.Strong("Rise Score:"), html.P(f"{stock_info['Rise_Score']:.0f}%")], width=6),
                            dbc.Col([html.Strong("Fall Score:"), html.P(f"{stock_info['Fall_Score']:.0f}%")], width=6),
                        ]),
                        html.Hr(),
                        dbc.Alert(div_text, color="warning" if div_text else "secondary"),
                        html.Small(stock_info.get('Signal_Reasons', ''), className="text-muted")
                    ])
                ])
            else:
                info_card = dbc.Card([dbc.CardBody([html.P("No data available")])])
            
            indicators_card = dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([html.H4("Strategy"), html.P("Divergence + RSI + Volume")])), width=6),
                dbc.Col(dbc.Card(dbc.CardBody([html.H4("Action"), html.P("Wait for confirmation candle")])), width=6),
            ])
            
            return fig, info_card, indicators_card
        
        return self.app
    
    def run(self, port=8050):
        print("\n" + "="*60)
        print("🚀 Starting Divergence Trading Dashboard...")
        print("="*60)
        
        app = self.create_dashboard()
        
        def open_browser():
            time.sleep(2)
            webbrowser.open(f'http://localhost:{port}')
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        print(f"\n✅ Dashboard: http://localhost:{port}")
        app.run(debug=False, port=port)
    
    def stop(self):
        self.analyzer.disconnect()

if __name__ == "__main__":
    dashboard = StockDashboard()
    dashboard.run()
