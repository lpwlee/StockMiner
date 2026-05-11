"""
Report generation for analysis results
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
from pathlib import Path

from ..models.stock_data import MarketAnalysis
from ..config.settings import config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class ReportGenerator:
    """Generate reports in various formats"""
    
    def __init__(self):
        self.report_dir = Path(config.data.report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
    
    def print_console_report(self, analysis: MarketAnalysis):
        """Print formatted report to console"""
        print("\n" + "="*100)
        print(f"📊 ANALYSIS RESULTS: {analysis.market}")
        print(f"📅 Generated: {analysis.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Analysis Duration: {analysis.analysis_duration:.2f} seconds")
        print(f"📈 Total Stocks Analyzed: {analysis.total_stocks_analyzed}")
        print("="*100)
        
        # Summary statistics
        stats = analysis.get_summary_statistics()
        print(f"\n📊 SUMMARY STATISTICS:")
        print(f"   Bullish Signals: {stats['bullish_count']}")
        print(f"   Bearish Signals: {stats['bearish_count']}")
        print(f"   Neutral Signals: {stats['neutral_count']}")
        print(f"   Avg Rise Score: {stats['avg_rise_score']:.1f}")
        print(f"   Avg Fall Score: {stats['avg_fall_score']:.1f}")
        
        # Rising stocks
        if analysis.rising_stocks:
            print(f"\n🟢 TOP STOCKS LIKELY TO RISE (Next {config.analysis.prediction_horizon} days):")
            print("─" * 100)
            print(f"{'Code':<12} {'Name':<25} {'Price':<10} {'Rise%':<8} {'RSI':<8} {'10D%':<8} {'Confidence':<10}")
            print("─" * 100)
            
            for stock in analysis.rising_stocks[:10]:
                print(f"{stock.stock_code:<12} {stock.stock_name[:25]:<25} "
                      f"${stock.current_price:<9.2f} {stock.rise_score:<8.1f} "
                      f"{stock.indicators.rsi_14:<8.1f} "
                      f"{stock.indicators.return_10d if stock.indicators.return_10d else 0:<+7.1f}% "
                      f"{stock.confidence*100:<9.1f}%")
        
        # Falling stocks
        if analysis.falling_stocks:
            print(f"\n🔴 TOP STOCKS LIKELY TO FALL (Next {config.analysis.prediction_horizon} days):")
            print("─" * 100)
            print(f"{'Code':<12} {'Name':<25} {'Price':<10} {'Fall%':<8} {'RSI':<8} {'10D%':<8} {'Confidence':<10}")
            print("─" * 100)
            
            for stock in analysis.falling_stocks[:10]:
                print(f"{stock.stock_code:<12} {stock.stock_name[:25]:<25} "
                      f"${stock.current_price:<9.2f} {stock.fall_score:<8.1f} "
                      f"{stock.indicators.rsi_14:<8.1f} "
                      f"{stock.indicators.return_10d if stock.indicators.return_10d else 0:<+7.1f}% "
                      f"{stock.confidence*100:<9.1f}%")
        
        print("\n" + "="*100)
        print("\n💡 LEGEND:")
        print("   Rise%: Predicted rise probability (0-100%)")
        print("   Fall%: Predicted fall probability (0-100%)")
        print("   RSI: Relative Strength Index (<30 oversold, >70 overbought)")
        print("   10D%: 10-day price return")
        print("   Confidence: Score difference confidence level")
    
    def generate_json_report(self, analysis: MarketAnalysis) -> str:
        """Generate JSON report"""
        report = {
            'metadata': {
                'market': analysis.market,
                'analysis_date': analysis.analysis_date.isoformat(),
                'analysis_duration': analysis.analysis_duration,
                'total_stocks': analysis.total_stocks_analyzed,
                'prediction_horizon': config.analysis.prediction_horizon
            },
            'summary': analysis.get_summary_statistics(),
            'rising_stocks': [
                {
                    'code': s.stock_code,
                    'name': s.stock_name,
                    'price': s.current_price,
                    'rise_score': s.rise_score,
                    'confidence': s.confidence,
                    'indicators': s.indicators.to_dict()
                }
                for s in analysis.rising_stocks
            ],
            'falling_stocks': [
                {
                    'code': s.stock_code,
                    'name': s.stock_name,
                    'price': s.current_price,
                    'fall_score': s.fall_score,
                    'confidence': s.confidence,
                    'indicators': s.indicators.to_dict()
                }
                for s in analysis.falling_stocks
            ]
        }
        
        return json.dumps(report, indent=2, default=str)
    
    def generate_csv_report(self, analysis: MarketAnalysis, output_file: Optional[str] = None):
        """Generate CSV report"""
        if not output_file:
            output_file = self.report_dir / f"{analysis.market}_{analysis.analysis_date.strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Combine all results
        all_stocks = []
        
        for stock in analysis.rising_stocks:
            data = {
                'type': 'RISING',
                'code': stock.stock_code,
                'name': stock.stock_name,
                'price': stock.current_price,
                'score': stock.rise_score,
                'confidence': stock.confidence,
                **stock.indicators.to_dict()
            }
            all_stocks.append(data)
        
        for stock in analysis.falling_stocks:
            data = {
                'type': 'FALLING',
                'code': stock.stock_code,
                'name': stock.stock_name,
                'price': stock.current_price,
                'score': stock.fall_score,
                'confidence': stock.confidence,
                **stock.indicators.to_dict()
            }
            all_stocks.append(data)
        
        df = pd.DataFrame(all_stocks)
        df.to_csv(output_file, index=False)
        logger.info(f"CSV report saved to {output_file}")
        return output_file
    
    def generate_html_report(self, analysis: MarketAnalysis, output_file: Optional[str] = None):
        """Generate HTML report with charts"""
        if not output_file:
            output_file = self.report_dir / f"{analysis.market}_{analysis.analysis_date.strftime('%Y%m%d_%H%M%S')}.html"
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Futu Stock Analysis - {analysis.market}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                .rising {{ background-color: #e8f5e9; }}
                .falling {{ background-color: #ffebee; }}
                .score-high {{ color: #4CAF50; font-weight: bold; }}
                .score-low {{ color: #f44336; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>🚀 Futu Stock Analysis Report</h1>
            <div class="summary">
                <h2>Analysis Summary</h2>
                <p><strong>Market:</strong> {analysis.market}</p>
                <p><strong>Analysis Date:</strong> {analysis.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Duration:</strong> {analysis.analysis_duration:.2f} seconds</p>
                <p><strong>Total Stocks:</strong> {analysis.total_stocks_analyzed}</p>
                <p><strong>Prediction Horizon:</strong> {config.analysis.prediction_horizon} days</p>
            </div>
            
            <h2>📈 Rising Stocks Prediction</h2>
            <table>
                <tr>
                    <th>Code</th>
                    <th>Name</th>
                    <th>Price</th>
                    <th>Rise Score</th>
                    <th>RSI</th>
                    <th>10D Return</th>
                    <th>Confidence</th>
                </tr>
                {self._generate_html_rows(analysis.rising_stocks[:20], 'rising')}
            </table>
            
            <h2>📉 Falling Stocks Prediction</h2>
            <table>
                <tr>
                    <th>Code</th>
                    <th>Name</th>
                    <th>Price</th>
                    <th>Fall Score</th>
                    <th>RSI</th>
                    <th>10D Return</th>
                    <th>Confidence</th>
                </tr>
                {self._generate_html_rows(analysis.falling_stocks[:20], 'falling')}
            </table>
            
            <footer>
                <hr>
                <p>Generated by Futu Stock Analyzer v{config.app.version} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </footer>
        </body>
        </html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        logger.info(f"HTML report saved to {output_file}")
        return output_file
    
    def _generate_html_rows(self, stocks, type_):
        """Generate HTML table rows"""
        rows = []
        for stock in stocks:
            row_class = 'rising' if type_ == 'rising' else 'falling'
            score = stock.rise_score if type_ == 'rising' else stock.fall_score
            score_class = 'score-high' if score > 70 else 'score-low' if score < 30 else ''
            
            rows.append(f"""
            <tr class="{row_class}">
                <td>{stock.stock_code}</td>
                <td>{stock.stock_name[:30]}</td>
                <td>${stock.current_price:.2f}</td>
                <td class="{score_class}">{score:.1f}</td>
                <td>{stock.indicators.rsi_14:.1f if stock.indicators.rsi_14 else 'N/A'}</td>
                <td>{stock.indicators.return_10d:+.1f}%</td>
                <td>{stock.confidence*100:.1f}%</td>
            </tr>
            """)
        return '\n'.join(rows)