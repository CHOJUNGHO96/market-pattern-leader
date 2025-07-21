"""로깅 설정 모듈"""

import logging
import sys
from typing import Optional
from .config import settings


def setup_logging(log_level: Optional[str] = None) -> logging.Logger:
    """
    애플리케이션 로깅 설정
    
    Args:
        log_level: 로깅 레벨 (기본값: settings.LOG_LEVEL)
        
    Returns:
        설정된 루트 로거
    """
    level = log_level or settings.LOG_LEVEL
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 기존 핸들러 제거
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    # 포맷터 설정
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    # 핸들러 추가
    root_logger.addHandler(console_handler)
    
    # 외부 라이브러리 로깅 레벨 조정
    _configure_third_party_loggers()
    
    return root_logger


def _configure_third_party_loggers():
    """외부 라이브러리 로거 설정"""
    # 외부 라이브러리들의 과도한 로깅 억제
    external_loggers = [
        "yfinance",
        "ccxt", 
        "urllib3",
        "requests",
        "asyncio",
        "matplotlib",
        "pandas"
    ]
    
    for logger_name in external_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    지정된 이름의 로거 반환
    
    Args:
        name: 로거 이름 (보통 __name__)
        
    Returns:
        로거 인스턴스
    """
    return logging.getLogger(name)