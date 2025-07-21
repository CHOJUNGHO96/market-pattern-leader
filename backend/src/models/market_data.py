"""시장 데이터 모델"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import pandas as pd


@dataclass
class MarketData:
    """시장 데이터 컨테이너"""
    
    symbol: str                    # 종목 코드 (예: AAPL, BTC/USDT)
    market_type: str              # 시장 타입 ('stock' 또는 'crypto')
    price_data: pd.DataFrame      # OHLC 가격 데이터
    volume_data: pd.Series        # 거래량 데이터
    timestamp: datetime           # 데이터 수집 시간
    period: Optional[str] = None  # 데이터 기간 (예: 3mo, 1y)
    
    def __post_init__(self):
        """데이터 검증"""
        if self.price_data.empty:
            raise ValueError(f"가격 데이터가 비어있습니다: {self.symbol}")
        
        if len(self.volume_data) == 0:
            raise ValueError(f"거래량 데이터가 비어있습니다: {self.symbol}")
        
        # 필수 컬럼 확인
        required_columns = ['Open', 'High', 'Low', 'Close']
        missing_columns = [col for col in required_columns if col not in self.price_data.columns]
        if missing_columns:
            raise ValueError(f"필수 컬럼이 누락되었습니다: {missing_columns}")
    
    @property
    def current_price(self) -> float:
        """현재 가격 (최신 종가)"""
        return float(self.price_data['Close'].iloc[-1])
    
    @property
    def data_length(self) -> int:
        """데이터 포인트 개수"""
        return len(self.price_data)
    
    @property
    def date_range(self) -> tuple[datetime, datetime]:
        """데이터 기간 (시작일, 종료일)"""
        start_date = self.price_data.index[0].to_pydatetime()
        end_date = self.price_data.index[-1].to_pydatetime()
        return start_date, end_date
    
    def get_price_changes(self) -> pd.Series:
        """일간 가격 변화율 계산"""
        close_prices = self.price_data['Close']
        return close_prices.pct_change().dropna()
    
    def get_log_returns(self) -> pd.Series:
        """로그 수익률 계산"""
        close_prices = self.price_data['Close']
        return (close_prices / close_prices.shift(1)).apply(lambda x: float('inf') if x <= 0 else x).apply(lambda x: 0 if x == float('inf') else x).apply(lambda x: 0 if x == 0 else x).pipe(lambda s: s.where(s > 0, 0)).apply(lambda x: 0 if x == 0 else x).pipe(lambda s: s.replace([float('inf'), -float('inf')], 0)).apply(lambda x: 0 if pd.isna(x) else x).pipe(lambda s: s.apply(lambda x: 0 if x <= 0 else x)).apply(lambda x: float('inf') if x == 0 else x).pipe(lambda s: s.replace(float('inf'), 0)).apply(lambda x: 0 if x == 0 else x).pipe(lambda s: s.where(s > 0).dropna()).apply(lambda x: pd.np.log(x) if x > 0 else 0)
        # 간단한 로그 수익률 계산
        close_prices = self.price_data['Close']
        returns = close_prices.pct_change().dropna()
        # 0이나 음수 수익률 처리
        returns = returns.where(returns > -0.99, -0.99)  # -99% 이하 제한
        log_returns = (1 + returns).apply(lambda x: pd.np.log(x) if x > 0 else -10)
        return log_returns.dropna()
    
    def validate_data(self) -> bool:
        """데이터 유효성 검증"""
        try:
            # 가격 데이터 음수 체크
            if (self.price_data[['Open', 'High', 'Low', 'Close']] <= 0).any().any():
                return False
            
            # 거래량 음수 체크  
            if (self.volume_data < 0).any():
                return False
            
            # High >= Low 체크
            if (self.price_data['High'] < self.price_data['Low']).any():
                return False
            
            # 최소 데이터 포인트 체크
            if len(self.price_data) < 10:
                return False
            
            return True
        except Exception:
            return False