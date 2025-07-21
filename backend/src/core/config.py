"""애플리케이션 설정 관리"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 애플리케이션 기본 설정
    PROJECT_NAME: str = "PatternLeader"
    VERSION: str = "1.0.0"
    DEBUG: bool = True  # 디버그 모드 활성화
    LOG_LEVEL: str = "INFO"
    
    # API 설정
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "localhost"
    PORT: int = 8000
    
    # 데이터 수집 설정
    DATA_CACHE_TTL: int = 900  # 15분 캐시
    MAX_DATA_POINTS: int = 1000
    DEFAULT_PERIOD: str = "3mo"
    
    # 외부 API 설정
    YFINANCE_TIMEOUT: int = 30
    CCXT_TIMEOUT: int = 30000
    
    # 보안 설정
    RATE_LIMIT: int = 100  # 분당 요청 수
    CORS_ORIGINS: list = ["*"]
    
    # 캐시 설정
    CACHE_TYPE: str = "memory"  # memory, redis
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None
    REDIS_PASSWORD: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 전역 설정 인스턴스
settings = Settings()