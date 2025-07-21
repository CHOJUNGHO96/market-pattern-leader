"""시장 데이터 관련 API 엔드포인트"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
import logging

from src.core.logging import get_logger

# 라우터 초기화
router = APIRouter(prefix="/market", tags=["Market"])
logger = get_logger(__name__)


@router.get("/types")
async def get_market_types():
    """
    지원되는 시장 타입 목록 조회
    
    Returns:
        시장 타입 목록과 설명
    """
    try:
        logger.debug("시장 타입 목록 요청")
        
        market_types = [
            {
                "value": "stock",
                "label": "주식",
                "description": "Yahoo Finance를 통한 주식 시장 데이터",
                "examples": ["AAPL", "TSLA", "GOOGL", "MSFT"]
            },
            {
                "value": "crypto", 
                "label": "암호화폐",
                "description": "Binance를 통한 암호화폐 시장 데이터",
                "examples": ["BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT"]
            }
        ]
        
        logger.debug("시장 타입 목록 조회 완료")
        return {"market_types": market_types}
        
    except Exception as e:
        logger.error(f"시장 타입 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="시장 타입 조회 중 오류가 발생했습니다")


@router.get("/periods")
async def get_analysis_periods():
    """
    지원되는 분석 기간 목록 조회
    
    Returns:
        분석 기간 목록과 설명
    """
    try:
        logger.debug("분석 기간 목록 요청")
        
        periods = [
            {
                "value": "1mo",
                "label": "1개월",
                "description": "최근 1개월간의 데이터로 분석",
                "recommended_for": "단기 트레이딩"
            },
            {
                "value": "3mo",
                "label": "3개월", 
                "description": "최근 3개월간의 데이터로 분석 (기본값)",
                "recommended_for": "일반적인 투자 분석"
            },
            {
                "value": "6mo",
                "label": "6개월",
                "description": "최근 6개월간의 데이터로 분석",
                "recommended_for": "중기 투자 분석"
            },
            {
                "value": "1y",
                "label": "1년",
                "description": "최근 1년간의 데이터로 분석",
                "recommended_for": "장기 트렌드 분석"
            }
        ]
        
        logger.debug("분석 기간 목록 조회 완료")
        return {"periods": periods}
        
    except Exception as e:
        logger.error(f"분석 기간 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="분석 기간 조회 중 오류가 발생했습니다")


@router.get("/risk-levels")
async def get_risk_levels():
    """
    리스크 레벨 설명 조회
    
    Returns:
        리스크 레벨별 설명
    """
    try:
        logger.debug("리스크 레벨 설명 요청")
        
        risk_levels = [
            {
                "level": "low",
                "label": "낮음",
                "color": "#22c55e",  # green
                "description": "안정적인 시장 상황으로 리스크가 낮습니다",
                "recommendation": "일반적인 투자 전략을 적용할 수 있습니다"
            },
            {
                "level": "medium", 
                "label": "보통",
                "color": "#eab308",  # yellow
                "description": "중간 수준의 리스크가 있어 주의가 필요합니다",
                "recommendation": "신중한 접근과 분할 투자를 고려하세요"
            },
            {
                "level": "high",
                "label": "높음", 
                "color": "#f97316",  # orange
                "description": "높은 리스크 상황으로 각별한 주의가 필요합니다",
                "recommendation": "리스크 관리와 손실 제한을 우선시하세요"
            },
            {
                "level": "extreme",
                "label": "극도",
                "color": "#ef4444",  # red
                "description": "극도로 높은 리스크 상황입니다",
                "recommendation": "투자를 중단하거나 매우 보수적으로 접근하세요"
            }
        ]
        
        logger.debug("리스크 레벨 설명 조회 완료")
        return {"risk_levels": risk_levels}
        
    except Exception as e:
        logger.error(f"리스크 레벨 설명 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="리스크 레벨 조회 중 오류가 발생했습니다")


@router.get("/sentiment-ranges")
async def get_sentiment_ranges():
    """
    감정 지수 범위 설명 조회
    
    Returns:
        감정 지수별 설명
    """
    try:
        logger.debug("감정 지수 범위 요청")
        
        sentiment_ranges = [
            {
                "range": "extreme_fear",
                "min": -1.0,
                "max": -0.6,
                "label": "극도 공포",
                "emoji": "😱",
                "color": "#dc2626",
                "description": "시장에 극도의 공포 심리가 팽배한 상태",
                "opportunity": "역발상 투자 기회일 수 있음"
            },
            {
                "range": "fear",
                "min": -0.6,
                "max": -0.2,
                "label": "공포",
                "emoji": "😰", 
                "color": "#f97316",
                "description": "시장 참여자들이 불안해하는 상태",
                "opportunity": "저점 매수 기회 검토"
            },
            {
                "range": "neutral",
                "min": -0.2,
                "max": 0.2,
                "label": "중립",
                "emoji": "😐",
                "color": "#6b7280",
                "description": "감정적으로 균형잡힌 상태",
                "opportunity": "추세 확인 후 방향성 결정"
            },
            {
                "range": "greed",
                "min": 0.2,
                "max": 0.6,
                "label": "탐욕",
                "emoji": "😤",
                "color": "#f59e0b",
                "description": "시장에 탐욕 심리가 커지는 상태",
                "opportunity": "추격매수 주의, 이익 실현 고려"
            },
            {
                "range": "extreme_greed",
                "min": 0.6,
                "max": 1.0,
                "label": "극도 탐욕",
                "emoji": "🤑",
                "color": "#dc2626",
                "description": "시장에 극도의 탐욕 심리가 팽배한 상태",
                "opportunity": "과열 구간, 매도 타이밍 고려"
            }
        ]
        
        logger.debug("감정 지수 범위 조회 완료")
        return {"sentiment_ranges": sentiment_ranges}
        
    except Exception as e:
        logger.error(f"감정 지수 범위 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="감정 지수 범위 조회 중 오류가 발생했습니다")


@router.get("/psychology-info")
async def get_psychology_info():
    """
    심리 분석 방법론 설명
    
    Returns:
        심리 분석 알고리즘 설명
    """
    try:
        logger.debug("심리 분석 정보 요청")
        
        psychology_info = {
            "methodology": {
                "name": "KDE 기반 심리 분석",
                "description": "커널 밀도 추정(KDE)을 사용하여 가격 변화율의 확률 분포를 계산하고, 현재 위치를 기반으로 투자자 심리를 추정합니다"
            },
            "components": {
                "buyers": {
                    "label": "매수자",
                    "description": "현재 가격에서 매수 의사를 가진 투자자 비율",
                    "calculation": "과매도 구간에서 높게, 과매수 구간에서 낮게 계산"
                },
                "holders": {
                    "label": "관망자", 
                    "description": "매수도 매도도 하지 않고 관망하는 투자자 비율",
                    "calculation": "시장 불확실성이 높을 때 증가"
                },
                "sellers": {
                    "label": "매도자",
                    "description": "현재 가격에서 매도 의사를 가진 투자자 비율", 
                    "calculation": "과매수 구간에서 높게, 과매도 구간에서 낮게 계산"
                }
            },
            "zones": {
                "oversold": {
                    "label": "과매도 구간",
                    "threshold": "-2σ 이하",
                    "description": "통계적으로 과도하게 하락한 구간"
                },
                "normal": {
                    "label": "정상 구간", 
                    "threshold": "-2σ ~ +2σ",
                    "description": "일반적인 가격 변동 범위"
                },
                "overbought": {
                    "label": "과매수 구간",
                    "threshold": "+2σ 이상", 
                    "description": "통계적으로 과도하게 상승한 구간"
                }
            },
            "limitations": [
                "과거 데이터를 기반으로 한 통계적 분석으로 미래를 보장하지 않습니다",
                "외부 요인(뉴스, 정책 등)은 반영되지 않습니다",
                "단기간의 급격한 변동은 분석 정확도를 떨어뜨릴 수 있습니다",
                "투자 조언이 아닌 참고 자료로만 활용해야 합니다"
            ]
        }
        
        logger.debug("심리 분석 정보 조회 완료")
        return psychology_info
        
    except Exception as e:
        logger.error(f"심리 분석 정보 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="심리 분석 정보 조회 중 오류가 발생했습니다")


@router.get("/popular-symbols")
async def get_popular_symbols():
    """
    인기 종목 목록 조회 (카테고리별)
    
    Returns:
        카테고리별 인기 종목 목록
    """
    try:
        logger.debug("인기 종목 목록 요청")
        
        popular_symbols = {
            "crypto": {
                "label": "인기 암호화폐",
                "symbols": [
                    {"symbol": "BTC/USDT", "name": "비트코인", "category": "메이저"},
                    {"symbol": "ETH/USDT", "name": "이더리움", "category": "메이저"},
                    {"symbol": "BNB/USDT", "name": "바이낸스 코인", "category": "거래소"},
                    {"symbol": "XRP/USDT", "name": "리플", "category": "결제"},
                    {"symbol": "ADA/USDT", "name": "카르다노", "category": "스마트컨트랙트"},
                    {"symbol": "SOL/USDT", "name": "솔라나", "category": "스마트컨트랙트"},
                    {"symbol": "DOGE/USDT", "name": "도지코인", "category": "밈코인"},
                    {"symbol": "DOT/USDT", "name": "폴카닷", "category": "인터체인"},
                    {"symbol": "AVAX/USDT", "name": "아발란체", "category": "스마트컨트랙트"},
                    {"symbol": "MATIC/USDT", "name": "폴리곤", "category": "레이어2"}
                ]
            },
            "stock": {
                "label": "인기 주식",
                "symbols": [
                    {"symbol": "AAPL", "name": "애플", "category": "기술"},
                    {"symbol": "MSFT", "name": "마이크로소프트", "category": "기술"},
                    {"symbol": "GOOGL", "name": "구글", "category": "기술"},
                    {"symbol": "AMZN", "name": "아마존", "category": "전자상거래"},
                    {"symbol": "TSLA", "name": "테슬라", "category": "자동차"},
                    {"symbol": "META", "name": "메타", "category": "소셜미디어"},
                    {"symbol": "NVDA", "name": "엔비디아", "category": "반도체"},
                    {"symbol": "NFLX", "name": "넷플릭스", "category": "스트리밍"},
                    {"symbol": "JPM", "name": "JPMorgan", "category": "금융"},
                    {"symbol": "V", "name": "비자", "category": "금융"}
                ]
            }
        }
        
        logger.debug("인기 종목 목록 조회 완료")
        return popular_symbols
        
    except Exception as e:
        logger.error(f"인기 종목 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="인기 종목 목록 조회 중 오류가 발생했습니다")