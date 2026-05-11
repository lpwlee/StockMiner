from dataclasses import dataclass
from typing import Optional

@dataclass
class StockInfo:
    code: str
    name: str
    price: float
    rsi: float
    return_10d: float
    return_20d: float
    volume_ratio: float
    
@dataclass
class AnalysisResult:
    code: str
    name: str
    price: float
    score: float
    rsi: float
    return_10d: float
    signal: str
    reasoning: str
