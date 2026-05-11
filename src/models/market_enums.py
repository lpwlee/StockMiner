from enum import Enum

class Market(Enum):
    HK_STOCKS = "HK_STOCKS"
    US_STOCKS = "US_STOCKS"
    
    @property
    def display_name(self):
        return "Hong Kong Stocks" if self == Market.HK_STOCKS else "US Stocks"
