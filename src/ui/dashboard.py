"""
Dashboard - Dark mode optimized with readable filters
"""

import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from datetime import datetime
import webbrowser
import threading
import time
import json
import os
import re

from src.core.analyzer_hybrid import HybridAnalyzer
from src.ui.components.sorting import sort_stocks, get_sort_options
from src.ui.components.filtering import filter_stocks, get_filter_options
from src.ui.components.display import create_stock_table, create_stock_info_card, create_dropdown_options
from src.ui.components.charts import create_candlestick_chart

# Global state
analysis_lock = threading.Lock()
analysis_in_progress = False
analysis_complete = False
analysis_data = None

class StockDashboard:
    def __init__(self):
        self.analyzer = HybridAnalyzer()
        self.app = None
        self.stock_list = []
        self.bilingual_names = {}
        self.load_cached_data()
        self.load_cached_names()
    
    def load_cached_data(self):
        """Load cached analysis data"""
        global analysis_data
        self.analyzer.load_cached_data()
        if self.analyzer.analyzed_stocks is not None:
            analysis_data = self.analyzer.analyzed_stocks
            print(f"✅ Loaded {len(analysis_data)} stocks from cache")
    
    def load_cached_names(self):
        """Load cached company names"""
        cache_file = "data/cache/company_names.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.bilingual_names = json.load(f)
                print(f"✅ Loaded {len(self.bilingual_names)} bilingual company names")
                return True
            except Exception as e:
                print(f"Error loading names: {e}")
        return False
    
    def get_display_name(self, code):
        """Get bilingual display name"""
        if code in self.bilingual_names:
            name = self.bilingual_names[code]
            return name if name else code.split('.')[-1]
        return code.split('.')[-1]
    
    def run_full_analysis(self):
        """Run complete analysis in background"""
        global analysis_in_progress, analysis_complete, analysis_data
        
        with analysis_lock:
            if analysis_in_progress:
                return
            analysis_in_progress = True
            analysis_complete = False
        
        try:
            if not self.stock_list:
                self.stock_list = self.analyzer.get_active_stock_list(min_volume=200000)
                print(f"✅ Found {len(self.stock_list)} active stocks")
            
            if not self.bilingual_names:
                self.bilingual_names = self.analyzer.fetch_company_names(self.stock_list)
                with open("data/cache/company_names.json", "w", encoding='utf-8') as f:
                    json.dump(self.bilingual_names, f, ensure_ascii=False, indent=2)
                print(f"✅ Fetched {len(self.bilingual_names)} bilingual company names")
            
            simple_names = {code: self.get_display_name(code) for code in self.stock_list}
            
            self.analyzer.analyze(
                "HK_STOCKS",
                self.stock_list,
                simple_names,
                force_refresh=False
            )
            
            analysis_data = self.analyzer.analyzed_stocks
            analysis_complete = True
            
        except Exception as e:
            print(f"Analysis error: {e}")
            analysis_complete = False
        finally:
            analysis_in_progress = False
    
    def get_filtered_sorted_stocks(self, filter_type, sort_by):
        """Get filtered and sorted stocks"""
        global analysis_data
        if analysis_data is None or analysis_data.empty:
            return []
        
        df = analysis_data
        filtered = filter_stocks(df, filter_type)
        sorted_df = sort_stocks(filtered, sort_by)
        sorted_df['Display_Name'] = sorted_df['Code'].apply(self.get_display_name)
        
        result_cols = ['Code', 'Display_Name', 'Price', 'RSI', 'Return_10D', 
                       'Rise_Score', 'Fall_Score', 'Net_Score', 
                       'Divergence_Type', 'Divergence_Strength', 
                       'Signal_Type', 'Signal_Strength']
        
        return sorted_df[result_cols].to_dict('records')
    
    def get_chart_and_info(self, stock_code):
        """Get chart and info for a stock"""
        global analysis_data
        if not stock_code:
            return None, None
        
        end_date = datetime.now()
        start_date = end_date - pd.Timedelta(days=120)
        
        data = self.analyzer.yahoo_client.get_history_kline(
            stock_code,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d'),
            use_cache=True
        )
        
        if data.empty:
            return None, None
        
        stock_info = None
        display_name = self.get_display_name(stock_code)
        
        if analysis_data is not None:
            match = analysis_data[analysis_data['Code'] == stock_code]
            if not match.empty:
                stock_info = match.iloc[0].to_dict()
        
        fig = create_candlestick_chart(data, stock_code, display_name, stock_info)
        
        return fig, stock_info
    
    def create_dashboard(self):
        """Create Dash dashboard with readable dark mode controls"""
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
        
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col(html.H1("📈 StockMiner - Divergence Trading Dashboard", 
                               className="text-center text-primary mb-3"), width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🎮 Control Panel", style={"color": "#ffffff", "backgroundColor": "#2c3e50"}),
                        dbc.CardBody([
                            html.H6("Analysis Control", className="fw-bold text-center mb-3", style={"color": "#ffffff"}),
                            dbc.Button("🚀 Run Complete Analysis", id="analyze-btn", 
                                      color="success", className="w-100 mb-3", size="lg"),
                            html.Div(id="status-text", className="text-info small text-center mb-3"),
                            
                            html.Hr(style={"borderColor": "#444"}),
                            
                            html.H6("Filter & Sort", className="fw-bold mb-2", style={"color": "#ffffff"}),
                            html.Label("Filter by:", className="fw-bold small", style={"color": "#aaaaaa"}),
                            dcc.RadioItems(
                                id='filter-type',
                                options=get_filter_options(),
                                value='buy',
                                inline=True,
                                className="mb-2",
                                labelStyle={"color": "#ffffff", "marginRight": "15px"},
                                inputStyle={"marginRight": "5px"}
                            ),
                            
                            html.Label("Sort by:", className="fw-bold small mt-2", style={"color": "#aaaaaa"}),
                            dcc.Dropdown(
                                id='sort-by',
                                options=get_sort_options(),
                                value='divergence_strength',
                                className="mb-3",
                                style={
                                    'backgroundColor': '#2c3e50',
                                    'color': '#ffffff',
                                    'border': '1px solid #555'
                                }
                            ),
                            
                            html.Hr(style={"borderColor": "#444"}),
                            
                            html.Label("Select Stock:", className="fw-bold", style={"color": "#ffffff"}),
                            dcc.Dropdown(
                                id='stock-dropdown', 
                                placeholder='Select a stock...',
                                style={
                                    'backgroundColor': '#2c3e50',
                                    'color': '#ffffff',
                                    'border': '1px solid #555'
                                }
                            ),
                        ])
                    ], className="mb-4", style={"backgroundColor": "#1e1e1e", "border": "1px solid #444"})
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📊 Divergence Chart", style={"color": "#ffffff", "backgroundColor": "#2c3e50"}),
                        dbc.CardBody([
                            dcc.Graph(id='chart', config={'responsive': True})
                        ])
                    ], style={"backgroundColor": "#1e1e1e", "border": "1px solid #444"})
                ], width=9)
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📈 Stock List - Click on Stock Code to Load Chart", style={"color": "#ffffff", "backgroundColor": "#2c3e50"}),
                        dbc.CardBody([
                            html.Div(id='stock-list-table', className="table-responsive"),
                            html.Div(id='stock-info')
                        ])
                    ], style={"backgroundColor": "#1e1e1e", "border": "1px solid #444"})
                ], width=12)
            ], className="mt-3"),
        ], fluid=True, className="p-4", style={"backgroundColor": "#121212"})
        
        # Main callback for updates
        @self.app.callback(
            [Output('status-text', 'children'),
             Output('stock-dropdown', 'options'),
             Output('stock-list-table', 'children'),
             Output('analyze-btn', 'disabled')],
            [Input('analyze-btn', 'n_clicks'),
             Input('filter-type', 'value'),
             Input('sort-by', 'value')]
        )
        def update_all(analyze_clicks, filter_type, sort_by):
            global analysis_in_progress, analysis_complete, analysis_data
            
            ctx = callback_context
            trigger = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'none'
            
            if trigger == 'analyze-btn' and not analysis_in_progress and not analysis_complete:
                thread = threading.Thread(target=self.run_full_analysis)
                thread.start()
                return "🔄 Analysis started! Check console for progress.", [], html.P("Analyzing... Please wait."), True
            
            if analysis_in_progress:
                return "🔄 Analysis in progress...", [], html.P("Analyzing stocks..."), True
            
            if (analysis_complete or analysis_data is not None) and analysis_data is not None:
                stocks = self.get_filtered_sorted_stocks(filter_type, sort_by)
                options = create_dropdown_options(stocks)
                stock_table, _ = create_stock_table(stocks)
                total = len(analysis_data)
                showing = len(stocks)
                return f"✅ Ready - {showing} stocks showing ({total} total)", options, stock_table, False
            
            return "Click 'Run Complete Analysis' to start", [], html.P("No data. Run analysis first."), False
        
        # Callback to handle button clicks
        @self.app.callback(
            Output('stock-dropdown', 'value'),
            [Input({'type': 'stock-btn', 'index': dash.ALL}, 'n_clicks')],
            prevent_initial_call=True
        )
        def handle_button_clicks(n_clicks_list):
            ctx = callback_context
            if ctx.triggered:
                trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
                match = re.search(r'"index":"([^"]+)"', trigger_id)
                if match:
                    stock_code = match.group(1).replace('-', '.')
                    print(f"Button clicked: {stock_code}")
                    return stock_code
            return dash.no_update
        
        # Callback for dropdown selection
        @self.app.callback(
            [Output('chart', 'figure'),
             Output('stock-info', 'children')],
            [Input('stock-dropdown', 'value')]
        )
        def update_chart_from_dropdown(stock_code):
            if not stock_code:
                return {}, html.P("Select a stock from the dropdown to view details", className="text-muted")
            
            fig, stock_info = self.get_chart_and_info(stock_code)
            
            if fig is None:
                return {}, html.P(f"No data available for {stock_code}", className="text-warning")
            
            info_card = create_stock_info_card(stock_info, self.get_display_name(stock_code))
            
            return fig, info_card
        
        return self.app
    
    def run(self, port=8050):
        print("\n" + "="*70)
        print("🚀 StockMiner Dashboard - Dark Mode Optimized")
        print("="*70)
        
        app = self.create_dashboard()
        
        def open_browser():
            time.sleep(2)
            webbrowser.open(f'http://localhost:{port}')
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        print(f"\n✅ Dashboard: http://localhost:{port}")
        print("\n📊 Instructions:")
        print("   • Use dropdown to select stocks - chart loads automatically")
        print("   • Click on blue underlined stock codes in the table - also loads chart")
        print("   • Filter and sort using the controls above")
        print("\n   Press Ctrl+C to stop\n")
        
        app.run(debug=False, port=port)

if __name__ == "__main__":
    dashboard = StockDashboard()
    dashboard.run()
