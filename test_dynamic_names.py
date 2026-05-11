"""
Test script for dynamic company name loading
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.connectors.futu_connector import FutuConnector

def test_dynamic_names():
    """Test dynamic name fetching"""
    print("="*60)
    print("Testing Dynamic Company Name Loading")
    print("="*60)
    
    connector = FutuConnector()
    
    # Test single stock name fetch
    test_stocks = ['HK.00005', 'HK.00700', 'HK.09988', 'HK.00001']
    
    print("\n1. Testing single stock name fetch:")
    print("-"*60)
    for code in test_stocks:
        name_en, name_cn = connector.get_stock_name(code)
        print(f"{code}:")
        print(f"   English: {name_en}")
        print(f"   Chinese: {name_cn}")
        print(f"   Display: {name_en} / {name_cn}" if name_en and name_cn else (name_en or name_cn))
    
    # Test batch name fetch
    print("\n2. Testing batch name fetch (10 stocks):")
    print("-"*60)
    batch_stocks = ['HK.00001', 'HK.00002', 'HK.00003', 'HK.00005', 'HK.00006', 
                    'HK.00011', 'HK.00012', 'HK.00016', 'HK.00017', 'HK.00027']
    
    name_map = connector.get_batch_stock_names(batch_stocks)
    
    for code, (name_en, name_cn) in name_map.items():
        print(f"{code}: {name_en} / {name_cn}")
    
    # Test cache
    print("\n3. Testing cache (should fetch from cache now):")
    print("-"*60)
    start_time = __import__('time').time()
    for code in test_stocks:
        name_en, name_cn = connector.get_stock_name(code)
    elapsed = __import__('time').time() - start_time
    print(f"Cache fetch time: {elapsed:.3f} seconds (should be very fast)")
    
    # Cache statistics
    print(f"\n4. Cache Statistics:")
    print("-"*60)
    print(f"Total cached names: {len(connector.name_cache)}")
    print(f"Cache duration: {connector.cache_duration} seconds")
    
    connector.release_connection()
    
    print("\n✅ Dynamic name loading test completed!")

if __name__ == "__main__":
    # Check connection first
    from src.connectors.futu_connector import FutuConnector
    temp_connector = FutuConnector()
    
    if temp_connector.check_connection():
        test_dynamic_names()
    else:
        print("❌ Cannot connect to FutuOpenD. Please start FutuOpenD first.")
        print("\nTroubleshooting:")
        print("1. Make sure FutuOpenD is running")
        print("2. Check if port 11111 is accessible")
        print("3. Run: python test_futu_connection.py")
