from typing import List
from src.connectors.futu_client import FutuClient
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class StockScanner:
    def __init__(self, client: FutuClient):
        self.client = client
        self.min_volume = 300000
        self.all_scanned_stocks = []  # Track all scanned stocks
    
    def scan_active_stocks(self, market: str, max_stocks: int = None) -> List[str]:
        logger.info(f"Scanning {market} for active stocks...")
        
        all_stocks = self.client.get_stock_list(market)
        total = len(all_stocks)
        logger.info(f"Total stocks in market: {total}")
        
        print(f"\n📋 Scanning all {total} stocks...")
        
        active = []
        self.all_scanned_stocks = []  # Reset tracking
        batch_size = 30
        
        for i in range(0, total, batch_size):
            batch = all_stocks[i:i+batch_size]
            snapshot = self.client.get_market_snapshot(batch)
            
            if not snapshot.empty:
                # Track all scanned stocks with their volume
                for _, row in snapshot.iterrows():
                    code = row.get('code')
                    volume = row.get('volume', 0)
                    price = row.get('last_price', 0)
                    self.all_scanned_stocks.append({
                        'code': code,
                        'volume': volume,
                        'price': price,
                        'active': volume >= self.min_volume and price >= 0.5
                    })
                
                filtered = snapshot[
                    (snapshot['volume'] >= self.min_volume) & 
                    (snapshot['last_price'] >= 0.5)
                ]
                active.extend(filtered['code'].tolist())
            
            pct = min(i + batch_size, total) / total * 100
            print(f"\r   Progress: {min(i+batch_size, total)}/{total} ({pct:.1f}%) - Found {len(active)} active", end="", flush=True)
        
        print()
        logger.info(f"Found {len(active)} active stocks out of {total} total")
        
        # Save complete scan results
        self.save_scan_results(market)
        
        if max_stocks and len(active) > max_stocks:
            return active[:max_stocks]
        return active
    
    def save_scan_results(self, market: str):
        """Save complete scan results to CSV"""
        import pandas as pd
        from datetime import datetime
        
        if not self.all_scanned_stocks:
            return
        
        df = pd.DataFrame(self.all_scanned_stocks)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/reports/scan_results_{market}_{timestamp}.csv"
        
        import os
        os.makedirs("data/reports", exist_ok=True)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        active_count = len(df[df['active'] == True])
        print(f"\n💾 Scan results saved to: {filename}")
        print(f"   Total scanned: {len(df)} | Active: {active_count} | Inactive: {len(df)-active_count}")
    
    def show_all_scanned(self):
        """Display all scanned stocks"""
        if not self.all_scanned_stocks:
            print("\n⚠️ No scan data available. Run a scan first.")
            return
        
        print("\n" + "="*120)
        print(f"📋 COMPLETE SCAN RESULTS - {len(self.all_scanned_stocks)} STOCKS")
        print("="*120)
        print(f"{'No.':<5} {'Code':<12} {'Volume':<15} {'Price':<10} {'Status':<10}")
        print("-"*120)
        
        for idx, stock in enumerate(self.all_scanned_stocks[:100], 1):  # Show first 100
            status = "✅ ACTIVE" if stock['active'] else "❌ Inactive"
            volume_str = f"{stock['volume']:,}"
            price_str = f"${stock['price']:.2f}" if stock['price'] >= 1 else f"${stock['price']:.4f}"
            
            print(f"{idx:<5} {stock['code']:<12} {volume_str:<15} {price_str:<10} {status}")
        
        if len(self.all_scanned_stocks) > 100:
            print(f"\n... and {len(self.all_scanned_stocks) - 100} more stocks")
            print(f"   Full list saved to CSV file in data/reports/")
        
        print("="*120)
        active_count = len([s for s in self.all_scanned_stocks if s['active']])
        print(f"✅ TOTAL: {len(self.all_scanned_stocks)} stocks scanned")
        print(f"   Active (volume ≥ {self.min_volume:,}): {active_count}")
        print(f"   Inactive: {len(self.all_scanned_stocks) - active_count}")
