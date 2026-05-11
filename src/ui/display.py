from datetime import datetime

class Display:
    @staticmethod
    def show_results(rising, falling, title):
        print("\n" + "="*100)
        print(f"📊 {title}")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*100)
        
        if rising is not None and not rising.empty:
            print(f"\n🟢 TOP {len(rising)} STOCKS LIKELY TO RISE:")
            print("-"*100)
            
            for idx, (_, row) in enumerate(rising.head(10).iterrows(), 1):
                price = row['Price']
                price_str = f"${price:,.0f}" if price >= 1000 else f"${price:.2f}"
                
                signal = "🔥🔥" if row['Rise_Score'] >= 70 else ("🔥" if row['Rise_Score'] >= 60 else "✓")
                
                print(f"  {idx:2}. {row['Code']:8} | {row['Name']:15} | {price_str:>8} | "
                      f"Rise:{row['Rise_Score']:3.0f}% | RSI:{row['RSI']:3.0f} | "
                      f"10D:{row['Return_10D']:+5.1f}% | {signal}")
            
            # Show top pick reasoning
            top = rising.iloc[0]
            if top.get('Reasoning'):
                print(f"\n  📝 Top pick: {top['Code']} - {top['Reasoning']}")
        
        if falling is not None and not falling.empty:
            print(f"\n🔴 TOP {len(falling)} STOCKS LIKELY TO FALL:")
            print("-"*100)
            
            for idx, (_, row) in enumerate(falling.head(10).iterrows(), 1):
                price = row['Price']
                price_str = f"${price:,.0f}" if price >= 1000 else f"${price:.2f}"
                
                signal = "⚠️⚠️" if row['Fall_Score'] >= 70 else ("⚠️" if row['Fall_Score'] >= 60 else "▼")
                
                print(f"  {idx:2}. {row['Code']:8} | {row['Name']:15} | {price_str:>8} | "
                      f"Fall:{row['Fall_Score']:3.0f}% | RSI:{row['RSI']:3.0f} | "
                      f"10D:{row['Return_10D']:+5.1f}% | {signal}")
        
        # Statistics
        print("\n" + "="*100)
        print("📊 SUMMARY")
        print("="*100)
        
        if rising is not None and not rising.empty:
            print(f"  📈 BUY ({len(rising)}): Avg RSI={rising['RSI'].mean():.0f}, Avg 10D={rising['Return_10D'].mean():+.1f}%")
        
        if falling is not None and not falling.empty:
            print(f"  📉 SELL ({len(falling)}): Avg RSI={falling['RSI'].mean():.0f}, Avg 10D={falling['Return_10D'].mean():+.1f}%")
        
        print("\n💡 TIPS: 🔥🔥=Strong Buy, 🔥=Buy, ⚠️⚠️=Strong Sell, ⚠️=Sell")
