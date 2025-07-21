"""API 의존성 관리"""

from fastapi import HTTPException, Request
from typing import Optional
import time
from collections import defaultdict

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

# 간단한 메모리 기반 요청 제한기
_request_counts = defaultdict(list)


async def rate_limiter(request: Request) -> None:
    """
    요청 속도 제한
    
    Args:
        request: FastAPI Request 객체
        
    Raises:
        HTTPException: 요청 제한 초과 시
    """
    if not settings.RATE_LIMIT:
        return
    
    # 클라이언트 IP 주소 가져오기
    client_ip = request.client.host
    current_time = time.time()
    
    # 1분 이전의 요청들 제거
    minute_ago = current_time - 60
    _request_counts[client_ip] = [
        req_time for req_time in _request_counts[client_ip] 
        if req_time > minute_ago
    ]
    
    # 현재 요청 수 확인
    current_requests = len(_request_counts[client_ip])
    
    if current_requests >= settings.RATE_LIMIT:
        logger.warning(f"요청 제한 초과: {client_ip}, 요청 수: {current_requests}")
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate Limit Exceeded",
                "message": f"분당 최대 {settings.RATE_LIMIT}회 요청 가능합니다",
                "retry_after": 60
            }
        )
    
    # 현재 요청 기록
    _request_counts[client_ip].append(current_time)


async def validate_market_type(market_type: str) -> str:
    """
    시장 타입 검증
    
    Args:
        market_type: 시장 타입
        
    Returns:
        검증된 시장 타입
        
    Raises:
        HTTPException: 잘못된 시장 타입
    """
    valid_types = ["stock", "crypto"]
    
    if market_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 시장 타입입니다. 가능한 값: {', '.join(valid_types)}"
        )
    
    return market_type


async def validate_period(period: str) -> str:
    """
    분석 기간 검증
    
    Args:
        period: 분석 기간
        
    Returns:
        검증된 분석 기간
        
    Raises:
        HTTPException: 잘못된 기간
    """
    valid_periods = ["1mo", "3mo", "6mo", "1y"]
    
    if period not in valid_periods:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 분석 기간입니다. 가능한 값: {', '.join(valid_periods)}"
        )
    
    return period


async def validate_symbol(symbol: str) -> str:
    """
    심볼 형식 검증
    
    Args:
        symbol: 심볼
        
    Returns:
        정규화된 심볼
        
    Raises:
        HTTPException: 잘못된 심볼 형식
    """
    if not symbol or len(symbol.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="심볼이 비어있습니다"
        )
    
    # 심볼 정규화
    normalized_symbol = symbol.upper().strip()
    
    # 기본적인 형식 검증
    if len(normalized_symbol) > 20:
        raise HTTPException(
            status_code=400,
            detail="심볼이 너무 깁니다 (최대 20자)"
        )
    
    # 특수문자 검증 (알파벳, 숫자, /, - 만 허용)
    allowed_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/-")
    if not all(c in allowed_chars for c in normalized_symbol):
        raise HTTPException(
            status_code=400,
            detail="심볼에 허용되지 않는 문자가 포함되어 있습니다"
        )
    
    return normalized_symbol


def get_cache_key_generator():
    """
    캐시 키 생성기 팩토리
    
    Returns:
        캐시 키 생성 함수
    """
    def generate_key(symbol: str, market_type: str, period: str) -> str:
        return f"analysis:{market_type}:{symbol}:{period}"
    
    return generate_key


async def check_service_health() -> bool:
    """
    서비스 상태 확인
    
    Returns:
        서비스 정상 여부
    """
    # 실제 구현에서는 데이터베이스, 외부 API 등의 상태를 확인
    # 현재는 항상 True 반환
    return True


class RequestValidator:
    """요청 검증 클래스"""
    
    @staticmethod
    async def validate_analysis_request(
        symbol: str,
        market_type: str, 
        period: str
    ) -> tuple[str, str, str]:
        """
        분석 요청 전체 검증
        
        Args:
            symbol: 심볼
            market_type: 시장 타입
            period: 기간
            
        Returns:
            검증된 (symbol, market_type, period) 튜플
        """
        validated_symbol = await validate_symbol(symbol)
        validated_market_type = await validate_market_type(market_type)
        validated_period = await validate_period(period)
        
        return validated_symbol, validated_market_type, validated_period
    
    @staticmethod
    def validate_limit(limit: int, max_limit: int = 200) -> int:
        """
        제한 수량 검증
        
        Args:
            limit: 요청된 제한 수량
            max_limit: 최대 허용 제한
            
        Returns:
            검증된 제한 수량
            
        Raises:
            HTTPException: 잘못된 제한 값
        """
        if limit < 1:
            raise HTTPException(
                status_code=400,
                detail="제한 수량은 1 이상이어야 합니다"
            )
        
        if limit > max_limit:
            raise HTTPException(
                status_code=400,
                detail=f"제한 수량은 {max_limit} 이하여야 합니다"
            )
        
        return limit


# 전역 검증기 인스턴스
request_validator = RequestValidator()