"""PatternLeader 백엔드 메인 애플리케이션"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from src.api.v1.endpoints.analysis import router as analysis_router
from src.api.v1.endpoints.market import router as market_router
from src.core.config import settings
from src.core.logging import setup_logging, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리"""
    # 시작 시 초기화
    logger = setup_logging(settings.LOG_LEVEL)
    logger.info(f"PatternLeader 백엔드 시작 - 버전: {settings.VERSION}")
    logger.info(f"디버그 모드: {settings.DEBUG}")
    logger.info(f"로그 레벨: {settings.LOG_LEVEL}")
    
    yield
    
    # 종료 시 정리
    logger.info("PatternLeader 백엔드 종료")


def create_app() -> FastAPI:
    """FastAPI 애플리케이션 생성"""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="시장 심리 분석을 위한 KDE 기반 분석 API",
        docs_url="/docs" if settings.DEBUG else None,  # 프로덕션에서는 문서 비활성화
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # CORS 미들웨어
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # 신뢰할 수 있는 호스트 미들웨어 (보안)
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", settings.HOST]
        )
    
    # API 라우터 등록
    app.include_router(
        analysis_router,
        prefix=settings.API_V1_PREFIX,
        dependencies=[]  # 필요 시 전역 의존성 추가
    )
    
    app.include_router(
        market_router,
        prefix=settings.API_V1_PREFIX,
        dependencies=[]
    )
    
    # 루트 엔드포인트
    @app.get("/")
    async def root():
        """루트 엔드포인트"""
        return {
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "running",
            "docs": "/docs" if settings.DEBUG else "disabled",
            "api_prefix": settings.API_V1_PREFIX
        }
    
    # 헬스체크 엔드포인트
    @app.get("/health")
    async def health():
        """간단한 헬스체크"""
        return {"status": "healthy", "service": settings.PROJECT_NAME}
    
    return app


# 애플리케이션 인스턴스 생성
app = create_app()


if __name__ == "__main__":
    """개발 서버 실행"""
    logger = get_logger(__name__)
    logger.info(f"개발 서버 시작: http://{settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.DEBUG
    )