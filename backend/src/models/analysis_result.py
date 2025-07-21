"""분석 결과 모델"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional
from datetime import datetime


class PsychologyRatios(BaseModel):
    """심리 비율 모델"""
    buyers: float = Field(..., ge=0, le=1, description="매수자 비율 (0-1)")
    holders: float = Field(..., ge=0, le=1, description="관망자 비율 (0-1)")
    sellers: float = Field(..., ge=0, le=1, description="매도자 비율 (0-1)")
    
    @validator('sellers')
    def validate_ratios_sum(cls, v, values):
        """비율 합계가 1이 되는지 검증"""
        if 'buyers' in values and 'holders' in values:
            total = values['buyers'] + values['holders'] + v
            if not (0.99 <= total <= 1.01):  # 부동소수점 오차 허용
                raise ValueError(f"심리 비율의 합계가 1이 아닙니다: {total}")
        return v


class DistributionStats(BaseModel):
    """분포 통계 모델"""
    mean: float = Field(..., description="평균 수익률")
    std: float = Field(..., ge=0, description="표준편차")
    skewness: float = Field(..., description="왜도 (분포의 비대칭성)")
    kurtosis: float = Field(..., description="첨도 (분포의 뾰족함)")
    peak_position: float = Field(..., description="분포 피크 위치")
    
    # 백분위 값들
    percentile_5: float = Field(..., description="5번째 백분위")
    percentile_25: float = Field(..., description="25번째 백분위")
    percentile_50: float = Field(..., description="50번째 백분위 (중앙값)")
    percentile_75: float = Field(..., description="75번째 백분위")
    percentile_95: float = Field(..., description="95번째 백분위")


class VisualizationData(BaseModel):
    """시각화 데이터 모델"""
    x_values: List[float] = Field(..., description="KDE X축 값들")
    y_values: List[float] = Field(..., description="KDE Y축 값들")
    current_position: float = Field(..., description="현재 위치")
    zones: Dict[str, Dict[str, float]] = Field(
        default_factory=dict,
        description="구간 정보 (oversold, overbought 등)"
    )
    
    @validator('y_values')
    def validate_same_length(cls, v, values):
        """X, Y 값들의 길이가 같은지 검증"""
        if 'x_values' in values and len(v) != len(values['x_values']):
            raise ValueError("X값과 Y값의 길이가 다릅니다")
        return v


class AnalysisResponse(BaseModel):
    """분석 응답 모델"""
    symbol: str = Field(..., description="종목 코드")
    current_price: float = Field(..., gt=0, description="현재 가격")
    analysis_timestamp: datetime = Field(..., description="분석 수행 시간")
    
    # 심리 분석 결과
    psychology_ratios: PsychologyRatios = Field(..., description="심리 비율")
    sentiment_score: float = Field(..., ge=-1, le=1, description="감정 지수 (-1: 극도공포, 1: 극도탐욕)")
    risk_level: str = Field(..., pattern="^(low|medium|high|extreme)$", description="리스크 레벨")
    interpretation: str = Field(..., description="분석 해석")
    
    # 통계 분석 결과
    distribution_stats: DistributionStats = Field(..., description="분포 통계")
    visualization_data: VisualizationData = Field(..., description="시각화 데이터")
    confidence_score: float = Field(..., ge=0, le=1, description="분석 신뢰도")
    
    # 메타데이터
    market_type: str = Field(..., pattern="^(stock|crypto)$", description="시장 타입")
    period: str = Field(..., description="분석 기간")
    data_points_count: int = Field(..., ge=1, description="사용된 데이터 포인트 수")


class QuickAnalysisResponse(BaseModel):
    """빠른 분석 응답 모델 (간소화된 버전)"""
    symbol: str
    current_price: float
    psychology_ratios: PsychologyRatios
    sentiment_score: float
    risk_level: str
    interpretation: str
    confidence_score: float
    analysis_timestamp: datetime


class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    error: str = Field(..., description="에러 타입")
    message: str = Field(..., description="에러 메시지")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="에러 발생 시간")
    details: Optional[Dict] = Field(None, description="추가 에러 정보")


class SymbolValidationResponse(BaseModel):
    """심볼 검증 응답 모델"""
    symbol: str
    is_valid: bool
    market_type: str
    message: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """헬스체크 응답 모델"""
    status: str = Field(..., pattern="^(healthy|degraded|unhealthy)$")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str
    services: Dict[str, str] = Field(default_factory=dict)
    uptime_seconds: Optional[float] = None