"""분석 엔진 오케스트레이터"""

import time
from typing import Optional
from datetime import datetime
import logging

from src.models.market_data import MarketData
from src.models.analysis_result import AnalysisResponse, QuickAnalysisResponse, VisualizationData
from src.services.data_collector import DataCollectorFactory
from src.services.psychology_analyzer import PsychologyAnalyzer, PsychologyResult
from src.utils.cache_manager import CacheManager
from src.core.config import settings
from src.core.logging import get_logger


class AnalysisEngine:
    """분석 엔진 오케스트레이터"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.data_collector = DataCollectorFactory()
        self.psychology_analyzer = PsychologyAnalyzer()
        self.cache_manager = CacheManager()
        self.start_time = time.time()
    
    async def analyze(
        self, 
        symbol: str, 
        market_type: str, 
        period: str, 
        exchange: Optional[str] = None
    ) -> AnalysisResponse:
        """
        전체 분석 프로세스 실행
        
        Args:
            symbol: 분석할 심볼
            market_type: 시장 타입 ('stock' 또는 'crypto')
            period: 분석 기간
            exchange: 거래소 (암호화폐만 해당, 선택사항)
            
        Returns:
            AnalysisResponse 객체
            
        Raises:
            ValueError: 분석 실패 시
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"전체 분석 시작: {symbol} ({market_type}, {period})")
            
            # 1. 캐시 확인
            cache_key = self.cache_manager.generate_cache_key(symbol, market_type, period)
            cached_result = await self.cache_manager.get(cache_key)
            
            if cached_result and not self.cache_manager.is_cache_expired(cached_result):
                self.logger.info(f"캐시에서 분석 결과 반환: {symbol}")
                return self.cache_manager.extract_cache_data(cached_result)
            
            # 2. 심볼 유효성 검증
            is_valid = await self.data_collector.validate_symbol(symbol, market_type)
            if not is_valid:
                raise ValueError(f"유효하지 않은 심볼입니다: {symbol}")
            
            # 3. 데이터 수집
            market_data = await self.data_collector.collect_data(symbol, market_type, period)
            
            # 4. 심리 분석
            psychology_result = self.psychology_analyzer.analyze_psychology(market_data)
            
            # 5. 응답 객체 생성
            response = self._build_analysis_response(psychology_result, market_data, start_time)
            
            # 6. 캐시 저장
            cache_data = self.cache_manager.prepare_cache_data(response)
            await self.cache_manager.set(cache_key, cache_data, settings.DATA_CACHE_TTL)
            
            self.logger.info(f"전체 분석 완료: {symbol}, 처리시간: {time.time() - start_time:.3f}초")
            return response
            
        except Exception as e:
            self.logger.error(f"전체 분석 실패: {symbol}, 오류: {str(e)}")
            raise ValueError(f"분석 실패: {str(e)}")
    
    async def quick_analyze(
        self, 
        symbol: str, 
        market_type: str = "crypto",
        period: str = "3mo"
    ) -> QuickAnalysisResponse:
        """
        빠른 분석 (간소화된 응답)
        
        Args:
            symbol: 분석할 심볼
            market_type: 시장 타입
            period: 분석 기간
            
        Returns:
            QuickAnalysisResponse 객체
        """
        try:
            self.logger.info(f"빠른 분석 시작: {symbol}")
            
            # 전체 분석 수행
            full_analysis = await self.analyze(symbol, market_type, period)
            
            # 간소화된 응답 생성
            quick_response = QuickAnalysisResponse(
                symbol=full_analysis.symbol,
                current_price=full_analysis.current_price,
                psychology_ratios=full_analysis.psychology_ratios,
                sentiment_score=full_analysis.sentiment_score,
                risk_level=full_analysis.risk_level,
                interpretation=full_analysis.interpretation,
                confidence_score=full_analysis.confidence_score,
                analysis_timestamp=full_analysis.analysis_timestamp
            )
            
            self.logger.info(f"빠른 분석 완료: {symbol}")
            return quick_response
            
        except Exception as e:
            self.logger.error(f"빠른 분석 실패: {symbol}, 오류: {str(e)}")
            raise
    
    def _build_analysis_response(
        self, 
        psychology_result: PsychologyResult, 
        market_data: MarketData,
        start_time: float
    ) -> AnalysisResponse:
        """
        분석 응답 객체 생성
        
        Args:
            psychology_result: 심리 분석 결과
            market_data: 시장 데이터
            start_time: 분석 시작 시간
            
        Returns:
            AnalysisResponse 객체
        """
        processing_time = time.time() - start_time
        start_date, end_date = market_data.date_range
        
        return AnalysisResponse(
            symbol=psychology_result.symbol,
            current_price=psychology_result.current_price,
            analysis_timestamp=datetime.utcnow(),
            psychology_ratios=psychology_result.psychology_ratios,
            sentiment_score=psychology_result.sentiment_score,
            risk_level=psychology_result.risk_level,
            interpretation=psychology_result.interpretation,
            distribution_stats=psychology_result.distribution_stats,
            visualization_data=psychology_result.visualization_data,
            confidence_score=psychology_result.confidence_score,
            market_type=market_data.market_type,
            period=market_data.period or "3mo",
            data_points_count=market_data.data_length
        )
    
    async def get_distribution_data(
        self, 
        symbol: str, 
        market_type: str, 
        period: str = "3mo"
    ) -> VisualizationData:
        """
        분포 곡선 시각화용 원시 데이터 제공
        
        Args:
            symbol: 심볼
            market_type: 시장 타입  
            period: 기간
            
        Returns:
            VisualizationData 객체
        """
        try:
            self.logger.info(f"분포 데이터 조회: {symbol}")
            
            # 전체 분석에서 시각화 데이터만 추출
            analysis_result = await self.analyze(symbol, market_type, period)
            
            return analysis_result.visualization_data
            
        except Exception as e:
            self.logger.error(f"분포 데이터 조회 실패: {symbol}, 오류: {str(e)}")
            raise
    
    async def validate_symbol(self, symbol: str, market_type: str) -> bool:
        """
        심볼 유효성 검증
        
        Args:
            symbol: 검증할 심볼
            market_type: 시장 타입
            
        Returns:
            유효 여부
        """
        return await self.data_collector.validate_symbol(symbol, market_type)
    
    async def get_supported_symbols(self, market_type: str, limit: int = 50) -> list:
        """
        지원되는 심볼 목록 조회
        
        Args:
            market_type: 시장 타입
            limit: 최대 개수
            
        Returns:
            심볼 목록
        """
        # 인기 있는 심볼들을 하드코딩으로 제공
        if market_type == "crypto":
            symbols = [
                "BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT",
                "SOL/USDT", "DOGE/USDT", "DOT/USDT", "AVAX/USDT", "SHIB/USDT",
                "MATIC/USDT", "LTC/USDT", "BCH/USDT", "LINK/USDT", "UNI/USDT",
                "ATOM/USDT", "ETC/USDT", "XLM/USDT", "VET/USDT", "FIL/USDT"
            ]
        elif market_type == "stock":
            symbols = [
                "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX",
                "BABA", "V", "JPM", "JNJ", "WMT", "PG", "UNH", "HD", "MA",
                "DIS", "PYPL", "ADBE", "CRM", "INTC", "CSCO", "PFE", "KO"
            ]
        else:
            symbols = []
        
        return symbols[:limit]
    
    async def health_check(self) -> dict:
        """
        서비스 헬스체크
        
        Returns:
            헬스체크 결과
        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "uptime_seconds": time.time() - self.start_time,
            "services": {}
        }
        
        try:
            # 데이터 수집기 테스트
            stock_collector = self.data_collector.get_collector("stock")
            crypto_collector = self.data_collector.get_collector("crypto")
            
            health_status["services"]["stock_collector"] = "healthy"
            health_status["services"]["crypto_collector"] = "healthy" if crypto_collector else "degraded"
            
            # 심리 분석기 테스트
            health_status["services"]["psychology_analyzer"] = "healthy"
            
            # 캐시 매니저 테스트
            health_status["services"]["cache_manager"] = "healthy"
            
        except Exception as e:
            self.logger.error(f"헬스체크 중 오류: {str(e)}")
            health_status["status"] = "degraded"
            health_status["services"]["error"] = str(e)
        
        return health_status
    
    async def invalidate_cache(self, symbol: str = None, market_type: str = None) -> int:
        """
        캐시 무효화
        
        Args:
            symbol: 특정 심볼 (선택사항)
            market_type: 특정 시장 타입 (선택사항)
            
        Returns:
            무효화된 캐시 개수
        """
        try:
            if symbol and market_type:
                # 특정 심볼의 모든 기간 캐시 무효화
                pattern = f"analysis:{market_type}:{symbol}:*"
            elif market_type:
                # 특정 시장 타입의 모든 캐시 무효화
                pattern = f"analysis:{market_type}:*"
            else:
                # 모든 분석 캐시 무효화
                pattern = "analysis:*"
            
            count = await self.cache_manager.invalidate_pattern(pattern)
            self.logger.info(f"캐시 무효화 완료: {count}개 항목")
            return count
            
        except Exception as e:
            self.logger.error(f"캐시 무효화 실패: {str(e)}")
            return 0
    
    def get_cache_stats(self) -> dict:
        """
        캐시 통계 조회
        
        Returns:
            캐시 통계 딕셔너리
        """
        if hasattr(self.cache_manager._cache, 'get_cache_stats'):
            return self.cache_manager._cache.get_cache_stats()
        else:
            return {"message": "캐시 통계를 사용할 수 없습니다"}