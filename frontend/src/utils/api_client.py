"""
PatternLeader API Client

FastAPI 백엔드와의 통신을 담당하는 클라이언트 모듈
"""

import requests
import streamlit as st
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class PsychologyRatios:
    """심리 비율 데이터 클래스"""
    buyers: float
    holders: float
    sellers: float


@dataclass  
class DistributionStats:
    """분포 통계 데이터 클래스"""
    mean: float
    std: float
    skewness: float
    kurtosis: float
    peak_position: float
    # 백분위 값들 (백엔드 호환성)
    percentile_5: float
    percentile_25: float
    percentile_50: float
    percentile_75: float
    percentile_95: float


@dataclass
class VisualizationData:
    """시각화 데이터 클래스"""
    x_values: list
    y_values: list
    current_position: float
    zones: Dict[str, Dict]


@dataclass
class AnalysisResponse:
    """분석 응답 데이터 클래스"""
    symbol: str
    current_price: float
    analysis_timestamp: datetime
    psychology_ratios: PsychologyRatios
    sentiment_score: float
    risk_level: str
    interpretation: str
    distribution_stats: DistributionStats
    visualization_data: VisualizationData
    confidence_score: float
    # 백엔드 호환성을 위한 추가 필드들
    market_type: str
    period: str
    data_points_count: int


class PatternLeaderAPI:
    """PatternLeader API 클라이언트"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        API 클라이언트 초기화
        
        Args:
            base_url: FastAPI 서버 기본 URL
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def get_analysis(self, symbol: str, market_type: str, period: str = "3mo", exchange: Optional[str] = None) -> AnalysisResponse:
        """
        시장 심리 분석 요청
        
        Args:
            symbol: 종목 코드 (예: AAPL, BTC/USDT)
            market_type: 시장 타입 (stock, crypto)
            period: 분석 기간 (1mo, 3mo, 6mo, 1y)
            exchange: 거래소 (암호화폐만 해당)
            
        Returns:
            AnalysisResponse: 분석 결과
            
        Raises:
            requests.exceptions.RequestException: API 요청 실패
            ValueError: 잘못된 파라미터
        """
        try:
            # 파라미터 검증
            self._validate_parameters(symbol, market_type, period)
            
            # API 엔드포인트 구성 (URL 인코딩 적용)
            encoded_symbol = symbol.replace('/', '%2F')
            url = f"{self.base_url}/api/v1/analysis/psychology/{encoded_symbol}"
            
            params = {
                "market_type": market_type,
                "period": period
            }
            
            if exchange and market_type == "crypto":
                params["exchange"] = exchange
            
            # API 요청
            with st.spinner(f"{symbol} 분석 중..."):
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
            
            # 응답 파싱
            data = response.json()
            return self._parse_analysis_response(data)
            
        except requests.exceptions.Timeout:
            raise requests.exceptions.RequestException("API 요청 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.")
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.RequestException("API 서버에 연결할 수 없습니다. 서버 상태를 확인해주세요.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise requests.exceptions.RequestException(f"종목을 찾을 수 없습니다: {symbol}")
            elif e.response.status_code == 422:
                raise requests.exceptions.RequestException("잘못된 파라미터입니다. 입력값을 확인해주세요.")
            else:
                raise requests.exceptions.RequestException(f"API 오류 ({e.response.status_code}): {e.response.text}")
        except Exception as e:
            raise requests.exceptions.RequestException(f"예상치 못한 오류가 발생했습니다: {str(e)}")
    
    def get_distribution_data(self, symbol: str, market_type: str, period: str = "3mo") -> Dict[str, Any]:
        """
        분포 곡선 시각화용 원시 데이터 요청
        
        Args:
            symbol: 종목 코드
            market_type: 시장 타입
            period: 분석 기간
            
        Returns:
            Dict: 분포 데이터
        """
        try:
            # URL 인코딩 적용
            encoded_symbol = symbol.replace('/', '%2F')
            url = f"{self.base_url}/api/v1/analysis/distribution/{encoded_symbol}"
            params = {
                "market_type": market_type,
                "period": period
            }
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            st.error(f"분포 데이터 요청 실패: {str(e)}")
            return {}
    
    
    def _validate_parameters(self, symbol: str, market_type: str, period: str) -> None:
        """파라미터 유효성 검사"""
        if not symbol or not symbol.strip():
            raise ValueError("종목 코드를 입력해주세요.")
        
        if market_type not in ["stock", "crypto"]:
            raise ValueError("시장 타입은 'stock' 또는 'crypto'여야 합니다.")
        
        if period not in ["1mo", "3mo", "6mo", "1y"]:
            raise ValueError("기간은 '1mo', '3mo', '6mo', '1y' 중 하나여야 합니다.")
    
    def _parse_analysis_response(self, data: Dict[str, Any]) -> AnalysisResponse:
        """API 응답 데이터를 AnalysisResponse 객체로 변환"""
        try:
            return AnalysisResponse(
                symbol=data["symbol"],
                current_price=data["current_price"],
                analysis_timestamp=datetime.fromisoformat(data["analysis_timestamp"].replace('Z', '+00:00')),
                psychology_ratios=PsychologyRatios(**data["psychology_ratios"]),
                sentiment_score=data["sentiment_score"],
                risk_level=data["risk_level"],
                interpretation=data["interpretation"],
                distribution_stats=DistributionStats(**data["distribution_stats"]),
                visualization_data=VisualizationData(**data["visualization_data"]),
                confidence_score=data["confidence_score"],
                market_type=data["market_type"],
                period=data["period"],
                data_points_count=data["data_points_count"]
            )
        except KeyError as e:
            raise ValueError(f"API 응답 형식이 올바르지 않습니다. 누락된 필드: {e}")
        except Exception as e:
            raise ValueError(f"응답 파싱 중 오류가 발생했습니다: {str(e)}")
    
    def check_server_health(self) -> bool:
        """API 서버 상태 확인"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False


# API 클라이언트 싱글톤 인스턴스
@st.cache_resource
def get_api_client() -> PatternLeaderAPI:
    """캐시된 API 클라이언트 인스턴스 반환"""
    return PatternLeaderAPI() 