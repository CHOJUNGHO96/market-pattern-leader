"""시장 심리 분석 API 엔드포인트"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import Optional, List
import logging
from urllib.parse import unquote

from src.models.analysis_result import (
    AnalysisResponse, QuickAnalysisResponse, VisualizationData,
    ErrorResponse, SymbolValidationResponse, HealthCheckResponse
)
from src.services.analysis_engine import AnalysisEngine
from src.core.logging import get_logger
from src.core.config import settings

# 라우터 및 서비스 초기화
router = APIRouter(prefix="/analysis", tags=["Analysis"])
analysis_engine = AnalysisEngine()
logger = get_logger(__name__)


@router.get("/psychology/{symbol}", response_model=AnalysisResponse)
async def analyze_market_psychology(
    symbol: str = Path(..., description="종목 코드 (예: AAPL, BTC/USDT)"),
    market_type: str = Query(..., pattern="^(stock|crypto)$", description="시장 타입"),
    period: str = Query("3mo", pattern="^(1mo|3mo|6mo|1y)$", description="분석 기간"),
    exchange: Optional[str] = Query(None, description="거래소 (암호화폐만 해당)")
):
    """
    시장 심리 분석 API
    
    주어진 종목의 시장 심리를 KDE 분포 분석을 통해 계산하고,
    매수/관망/매도 비율, 감정 지수, 리스크 레벨 등을 제공합니다.
    
    Args:
        symbol: 종목 코드 (예: AAPL, BTC/USDT)
        market_type: 시장 타입 (stock, crypto)
        period: 분석 기간 (1mo, 3mo, 6mo, 1y)
        exchange: 거래소 (암호화폐만 해당)
    
    Returns:
        심리 분석 결과 및 시각화 데이터
        
    Raises:
        HTTPException: 분석 실패 시
    """
    try:
        logger.info(f"심리 분석 요청: {symbol} ({market_type}, {period})")
        
        # 심볼 URL 디코딩 및 정규화
        symbol = unquote(symbol).upper().strip()
        
        # 분석 실행
        result = await analysis_engine.analyze(
            symbol=symbol,
            market_type=market_type,
            period=period,
            exchange=exchange
        )
        
        logger.info(f"심리 분석 성공: {symbol}")
        return result
        
    except ValueError as e:
        logger.warning(f"잘못된 요청: {symbol}, 오류: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"심리 분석 실패: {symbol}, 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="분석 중 오류가 발생했습니다")


@router.get("/quick/{symbol}", response_model=QuickAnalysisResponse)
async def quick_analyze(
    symbol: str = Path(..., description="종목 코드"),
    market_type: str = Query("crypto", pattern="^(stock|crypto)$", description="시장 타입"),
    period: str = Query("3mo", pattern="^(1mo|3mo|6mo|1y)$", description="분석 기간")
):
    """
    빠른 심리 분석 (간소화된 응답)
    
    기본적인 심리 분석 결과만 빠르게 제공합니다.
    대시보드나 간단한 조회용으로 적합합니다.
    
    Args:
        symbol: 종목 코드
        market_type: 시장 타입
        period: 분석 기간
        
    Returns:
        간소화된 심리 분석 결과
    """
    try:
        logger.info(f"빠른 분석 요청: {symbol}")
        
        symbol = unquote(symbol).upper().strip()
        
        result = await analysis_engine.quick_analyze(
            symbol=symbol,
            market_type=market_type,
            period=period
        )
        
        logger.info(f"빠른 분석 성공: {symbol}")
        return result
        
    except ValueError as e:
        logger.warning(f"빠른 분석 잘못된 요청: {symbol}, 오류: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"빠른 분석 실패: {symbol}, 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="분석 중 오류가 발생했습니다")


@router.get("/distribution/{symbol}", response_model=VisualizationData)
async def get_distribution_data(
    symbol: str = Path(..., description="종목 코드"),
    market_type: str = Query(..., pattern="^(stock|crypto)$", description="시장 타입"),
    period: str = Query("3mo", pattern="^(1mo|3mo|6mo|1y)$", description="분석 기간")
):
    """
    분포 곡선 시각화용 원시 데이터 제공
    
    KDE 분포 곡선을 그리기 위한 X, Y 좌표와
    현재 위치, 과매수/과매도 구간 정보를 제공합니다.
    
    Args:
        symbol: 종목 코드
        market_type: 시장 타입
        period: 분석 기간
        
    Returns:
        시각화용 데이터
    """
    try:
        logger.info(f"분포 데이터 요청: {symbol}")
        
        symbol = unquote(symbol).upper().strip()
        
        viz_data = await analysis_engine.get_distribution_data(
            symbol=symbol,
            market_type=market_type,
            period=period
        )
        
        logger.info(f"분포 데이터 조회 성공: {symbol}")
        return viz_data
        
    except ValueError as e:
        logger.warning(f"분포 데이터 잘못된 요청: {symbol}, 오류: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"분포 데이터 조회 실패: {symbol}, 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="분포 데이터 조회 중 오류가 발생했습니다")


@router.get("/validate/{symbol}", response_model=SymbolValidationResponse)
async def validate_symbol(
    symbol: str = Path(..., description="검증할 종목 코드"),
    market_type: str = Query(..., pattern="^(stock|crypto)$", description="시장 타입")
):
    """
    심볼 유효성 검증
    
    주어진 심볼이 해당 시장에서 거래 가능한지 확인합니다.
    
    Args:
        symbol: 검증할 심볼
        market_type: 시장 타입
        
    Returns:
        검증 결과
    """
    try:
        logger.info(f"심볼 검증 요청: {symbol} ({market_type})")
        
        symbol = unquote(symbol).upper().strip()
        
        is_valid = await analysis_engine.validate_symbol(symbol, market_type)
        
        message = f"'{symbol}'은(는) 유효한 {market_type} 심볼입니다." if is_valid else f"'{symbol}'은(는) 유효하지 않은 심볼입니다."
        
        response = SymbolValidationResponse(
            symbol=symbol,
            is_valid=is_valid,
            market_type=market_type,
            message=message
        )
        
        logger.info(f"심볼 검증 완료: {symbol}, 유효성: {is_valid}")
        return response
        
    except Exception as e:
        logger.error(f"심볼 검증 실패: {symbol}, 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="심볼 검증 중 오류가 발생했습니다")


@router.get("/symbols", response_model=List[str])
async def get_supported_symbols(
    market_type: str = Query(..., pattern="^(stock|crypto)$", description="시장 타입"),
    limit: int = Query(50, ge=1, le=200, description="최대 심볼 개수")
):
    """
    지원되는 심볼 목록 조회
    
    현재 분석 가능한 인기 종목들의 목록을 제공합니다.
    
    Args:
        market_type: 시장 타입
        limit: 최대 반환할 심볼 개수
        
    Returns:
        지원되는 심볼 목록
    """
    try:
        logger.info(f"지원 심볼 목록 요청: {market_type}, 제한: {limit}")
        
        symbols = await analysis_engine.get_supported_symbols(market_type, limit)
        
        logger.info(f"지원 심볼 목록 조회 성공: {len(symbols)}개")
        return symbols
        
    except Exception as e:
        logger.error(f"지원 심볼 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="심볼 목록 조회 중 오류가 발생했습니다")


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    서비스 헬스체크
    
    분석 서비스의 상태와 각 구성요소의 건강성을 확인합니다.
    
    Returns:
        헬스체크 결과
    """
    try:
        logger.debug("헬스체크 요청")
        
        health_status = await analysis_engine.health_check()
        
        response = HealthCheckResponse(
            status=health_status["status"],
            version=health_status["version"],
            services=health_status["services"],
            uptime_seconds=health_status["uptime_seconds"]
        )
        
        logger.debug(f"헬스체크 완료: {health_status['status']}")
        return response
        
    except Exception as e:
        logger.error(f"헬스체크 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="헬스체크 중 오류가 발생했습니다")


@router.delete("/cache")
async def invalidate_cache(
    symbol: Optional[str] = Query(None, description="특정 심볼의 캐시만 삭제"),
    market_type: Optional[str] = Query(None, pattern="^(stock|crypto)$", description="특정 시장의 캐시만 삭제")
):
    """
    캐시 무효화
    
    분석 결과 캐시를 삭제합니다. 관리자 기능입니다.
    
    Args:
        symbol: 특정 심볼 (선택사항)
        market_type: 특정 시장 타입 (선택사항)
        
    Returns:
        무효화된 캐시 개수
    """
    try:
        logger.info(f"캐시 무효화 요청: symbol={symbol}, market_type={market_type}")
        
        count = await analysis_engine.invalidate_cache(symbol, market_type)
        
        logger.info(f"캐시 무효화 완료: {count}개 항목")
        return {"message": f"{count}개의 캐시 항목이 무효화되었습니다", "count": count}
        
    except Exception as e:
        logger.error(f"캐시 무효화 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="캐시 무효화 중 오류가 발생했습니다")


@router.get("/cache/stats")
async def get_cache_stats():
    """
    캐시 통계 조회
    
    현재 캐시 상태와 통계 정보를 제공합니다.
    
    Returns:
        캐시 통계 정보
    """
    try:
        logger.debug("캐시 통계 요청")
        
        stats = analysis_engine.get_cache_stats()
        
        logger.debug("캐시 통계 조회 완료")
        return stats
        
    except Exception as e:
        logger.error(f"캐시 통계 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="캐시 통계 조회 중 오류가 발생했습니다")


# 에러 핸들러는 main.py에서 앱 레벨로 처리