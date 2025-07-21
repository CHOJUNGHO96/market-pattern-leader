"""데이터 수집 서비스"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

import yfinance as yf
import ccxt
import pandas as pd

from src.models.market_data import MarketData
from src.core.config import settings
from src.core.logging import get_logger


class DataCollectorInterface(ABC):
    """데이터 수집기 인터페이스"""
    
    @abstractmethod
    async def collect_data(self, symbol: str, period: str) -> MarketData:
        """
        데이터 수집 메서드
        
        Args:
            symbol: 종목 코드
            period: 데이터 기간
            
        Returns:
            MarketData 객체
        """
        pass
    
    @abstractmethod
    async def validate_symbol(self, symbol: str) -> bool:
        """
        심볼 유효성 검증
        
        Args:
            symbol: 검증할 심볼
            
        Returns:
            유효 여부
        """
        pass


class StockDataCollector(DataCollectorInterface):
    """Yahoo Finance를 통한 주식 데이터 수집기"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    async def collect_data(self, symbol: str, period: str = "3mo") -> MarketData:
        """
        주식 데이터 수집
        
        Args:
            symbol: 주식 심볼 (예: AAPL, TSLA)
            period: 데이터 기간 (1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            MarketData 객체
            
        Raises:
            ValueError: 데이터 수집 실패 시
        """
        try:
            self.logger.info(f"주식 데이터 수집 시작: {symbol}, 기간: {period}")
            
            # 비동기로 yfinance 호출
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                self.executor,
                self._fetch_stock_data,
                symbol,
                period
            )
            
            if data is None or data.empty:
                raise ValueError(f"주식 데이터를 가져올 수 없습니다: {symbol}")
            
            # 데이터 검증
            if len(data) < 10:
                raise ValueError(f"충분한 데이터가 없습니다: {symbol} (데이터 포인트: {len(data)})")
            
            # MarketData 객체 생성
            market_data = MarketData(
                symbol=symbol,
                market_type="stock",
                price_data=data[['Open', 'High', 'Low', 'Close']],
                volume_data=data['Volume'],
                timestamp=datetime.utcnow(),
                period=period
            )
            
            # 데이터 유효성 검증
            if not market_data.validate_data():
                raise ValueError(f"수집된 데이터가 유효하지 않습니다: {symbol}")
            
            self.logger.info(f"주식 데이터 수집 완료: {symbol}, 포인트 수: {len(data)}")
            return market_data
            
        except Exception as e:
            self.logger.error(f"주식 데이터 수집 실패: {symbol}, 오류: {str(e)}")
            raise ValueError(f"주식 데이터 수집 실패: {str(e)}")
    
    def _fetch_stock_data(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """
        실제 yfinance 데이터 수집 (동기 방식)
        
        Args:
            symbol: 주식 심볼
            period: 데이터 기간
            
        Returns:
            DataFrame 또는 None
        """
        try:
            # yfinance Ticker 객체 생성
            ticker = yf.Ticker(symbol)
            
            # 히스토리 데이터 가져오기
            data = ticker.history(
                period=period,
                auto_adjust=True,  # 분할/배당 조정
                prepost=True,      # 시간외 거래 포함
                timeout=settings.YFINANCE_TIMEOUT
            )
            
            if data.empty:
                return None
            
            # 결측값 처리
            data = data.dropna()
            
            # 이상치 필터링 (가격이 0 이하인 경우)
            data = data[data['Close'] > 0]
            
            return data
            
        except Exception as e:
            self.logger.error(f"yfinance 데이터 수집 오류: {symbol}, {str(e)}")
            return None
    
    async def validate_symbol(self, symbol: str) -> bool:
        """
        주식 심볼 유효성 검증
        
        Args:
            symbol: 검증할 주식 심볼
            
        Returns:
            유효 여부
        """
        try:
            loop = asyncio.get_event_loop()
            is_valid = await loop.run_in_executor(
                self.executor,
                self._validate_stock_symbol,
                symbol
            )
            return is_valid
        except Exception as e:
            self.logger.error(f"주식 심볼 검증 실패: {symbol}, {str(e)}")
            return False
    
    def _validate_stock_symbol(self, symbol: str) -> bool:
        """
        실제 주식 심볼 검증 (동기 방식)
        
        Args:
            symbol: 주식 심볼
            
        Returns:
            유효 여부
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 기본적인 정보가 있는지 확인
            return info is not None and len(info) > 0 and 'symbol' in info
            
        except Exception:
            return False


class CryptoDataCollector(DataCollectorInterface):
    """CCXT를 통한 암호화폐 데이터 수집기"""
    
    def __init__(self, exchange_name: str = 'binance'):
        self.logger = get_logger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        try:
            # CCXT 거래소 객체 생성
            exchange_class = getattr(ccxt, exchange_name)
            self.exchange = exchange_class({
                'apiKey': None,  # 공개 데이터만 사용
                'secret': None,
                'timeout': settings.CCXT_TIMEOUT,
                'enableRateLimit': True,
                'sandbox': False
            })
            self.exchange_name = exchange_name
            self.logger.info(f"암호화폐 거래소 초기화 완료: {exchange_name}")
            
        except Exception as e:
            self.logger.error(f"암호화폐 거래소 초기화 실패: {exchange_name}, {str(e)}")
            self.exchange = None
    
    async def collect_data(self, symbol: str, period: str = "1d") -> MarketData:
        """
        암호화폐 데이터 수집
        
        Args:
            symbol: 암호화폐 심볼 (예: BTC/USDT, ETH/USDT)
            period: 데이터 기간 (ccxt에서는 timeframe 방식 사용)
            
        Returns:
            MarketData 객체
            
        Raises:
            ValueError: 데이터 수집 실패 시
        """
        if not self.exchange:
            raise ValueError("암호화폐 거래소가 초기화되지 않았습니다")
        
        try:
            self.logger.info(f"암호화폐 데이터 수집 시작: {symbol}, 기간: {period}")
            
            # 기간을 일수로 변환
            days = self._period_to_days(period)
            
            # 비동기로 CCXT 호출
            loop = asyncio.get_event_loop()
            ohlcv_data = await loop.run_in_executor(
                self.executor,
                self._fetch_crypto_data,
                symbol,
                days
            )
            
            if not ohlcv_data or len(ohlcv_data) < 10:
                raise ValueError(f"충분한 암호화폐 데이터를 가져올 수 없습니다: {symbol}")
            
            # DataFrame으로 변환
            df = self._ohlcv_to_dataframe(ohlcv_data)
            
            # MarketData 객체 생성
            market_data = MarketData(
                symbol=symbol,
                market_type="crypto",
                price_data=df[['Open', 'High', 'Low', 'Close']],
                volume_data=df['Volume'],
                timestamp=datetime.utcnow(),
                period=period
            )
            
            # 데이터 유효성 검증
            if not market_data.validate_data():
                raise ValueError(f"수집된 암호화폐 데이터가 유효하지 않습니다: {symbol}")
            
            self.logger.info(f"암호화폐 데이터 수집 완료: {symbol}, 포인트 수: {len(df)}")
            return market_data
            
        except Exception as e:
            self.logger.error(f"암호화폐 데이터 수집 실패: {symbol}, 오류: {str(e)}")
            raise ValueError(f"암호화폐 데이터 수집 실패: {str(e)}")
    
    def _fetch_crypto_data(self, symbol: str, days: int) -> Optional[list]:
        """
        실제 CCXT 데이터 수집 (동기 방식)
        
        Args:
            symbol: 암호화폐 심볼
            days: 수집할 일수
            
        Returns:
            OHLCV 데이터 리스트 또는 None
        """
        try:
            # 시작 시간 계산 (milliseconds)
            since = int((datetime.utcnow() - timedelta(days=days)).timestamp() * 1000)
            
            # OHLCV 데이터 수집
            ohlcv = self.exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe='1d',  # 일봉 데이터
                since=since,
                limit=days
            )
            
            return ohlcv
            
        except Exception as e:
            self.logger.error(f"CCXT 데이터 수집 오류: {symbol}, {str(e)}")
            return None
    
    def _ohlcv_to_dataframe(self, ohlcv_data: list) -> pd.DataFrame:
        """
        OHLCV 데이터를 DataFrame으로 변환
        
        Args:
            ohlcv_data: CCXT OHLCV 데이터
            
        Returns:
            변환된 DataFrame
        """
        df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        
        # 타임스탬프를 인덱스로 변환
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        # 숫자형으로 변환
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            df[col] = pd.to_numeric(df[col])
        
        # 결측값 제거
        df = df.dropna()
        
        return df
    
    def _period_to_days(self, period: str) -> int:
        """
        기간 문자열을 일수로 변환
        
        Args:
            period: 기간 문자열 (예: 1mo, 3mo, 1y)
            
        Returns:
            일수
        """
        period_mapping = {
            '1mo': 30,
            '3mo': 90,
            '6mo': 180,
            '1y': 365,
            '2y': 730
        }
        
        return period_mapping.get(period, 90)  # 기본값: 3개월
    
    async def validate_symbol(self, symbol: str) -> bool:
        """
        암호화폐 심볼 유효성 검증
        
        Args:
            symbol: 검증할 암호화폐 심볼
            
        Returns:
            유효 여부
        """
        if not self.exchange:
            return False
        
        try:
            loop = asyncio.get_event_loop()
            is_valid = await loop.run_in_executor(
                self.executor,
                self._validate_crypto_symbol,
                symbol
            )
            return is_valid
        except Exception as e:
            self.logger.error(f"암호화폐 심볼 검증 실패: {symbol}, {str(e)}")
            return False
    
    def _validate_crypto_symbol(self, symbol: str) -> bool:
        """
        실제 암호화폐 심볼 검증 (동기 방식)
        
        Args:
            symbol: 암호화폐 심볼
            
        Returns:
            유효 여부
        """
        try:
            # 마켓 정보 로드
            markets = self.exchange.load_markets()
            return symbol in markets
            
        except Exception:
            return False


class DataCollectorFactory:
    """데이터 수집기 팩토리"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._collectors = {}
    
    def get_collector(self, market_type: str) -> DataCollectorInterface:
        """
        시장 타입에 따른 데이터 수집기 반환
        
        Args:
            market_type: 시장 타입 ('stock' 또는 'crypto')
            
        Returns:
            DataCollectorInterface 구현체
            
        Raises:
            ValueError: 지원하지 않는 시장 타입
        """
        if market_type not in self._collectors:
            if market_type == "stock":
                self._collectors[market_type] = StockDataCollector()
            elif market_type == "crypto":
                self._collectors[market_type] = CryptoDataCollector()
            else:
                raise ValueError(f"지원하지 않는 시장 타입: {market_type}")
        
        return self._collectors[market_type]
    
    async def validate_symbol(self, symbol: str, market_type: str) -> bool:
        """
        심볼 유효성 검증
        
        Args:
            symbol: 검증할 심볼
            market_type: 시장 타입
            
        Returns:
            유효 여부
        """
        try:
            collector = self.get_collector(market_type)
            return await collector.validate_symbol(symbol)
        except Exception as e:
            self.logger.error(f"심볼 검증 실패: {symbol}, {market_type}, {str(e)}")
            return False
    
    async def collect_data(self, symbol: str, market_type: str, period: str) -> MarketData:
        """
        데이터 수집
        
        Args:
            symbol: 심볼
            market_type: 시장 타입
            period: 기간
            
        Returns:
            MarketData 객체
        """
        collector = self.get_collector(market_type)
        return await collector.collect_data(symbol, period)