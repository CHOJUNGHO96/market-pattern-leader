"""시장 심리 분석 엔진"""

from dataclasses import dataclass
from typing import Tuple, Dict, List
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import gaussian_kde
from sklearn.preprocessing import StandardScaler
import logging

from src.models.market_data import MarketData
from src.models.analysis_result import (
    PsychologyRatios, DistributionStats, VisualizationData
)
from src.core.logging import get_logger


@dataclass
class PsychologyResult:
    """심리 분석 결과 컨테이너"""
    symbol: str
    current_price: float
    distribution_stats: DistributionStats
    psychology_ratios: PsychologyRatios
    sentiment_score: float  # -1 (극도공포) ~ 1 (극도탐욕)
    risk_level: str  # 'low', 'medium', 'high', 'extreme'
    interpretation: str
    visualization_data: VisualizationData
    confidence_score: float


class PsychologyAnalyzer:
    """시장 심리 분석 엔진"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.scaler = StandardScaler()
    
    def analyze_psychology(self, market_data: MarketData) -> PsychologyResult:
        """
        주요 심리 분석 흐름
        
        Args:
            market_data: 시장 데이터
            
        Returns:
            PsychologyResult 객체
        """
        try:
            self.logger.info(f"심리 분석 시작: {market_data.symbol}")
            
            # 1. 수익률 계산
            returns = self._calculate_returns(market_data.price_data)
            
            if len(returns) < 10:
                raise ValueError(f"분석을 위한 충분한 수익률 데이터가 없습니다: {len(returns)}개")
            
            # 2. KDE 분포 추정
            kde_dist = self._estimate_kde_distribution(returns)
            
            # 3. 분포 통계 계산
            distribution_stats = self._calculate_distribution_stats(returns)
            
            # 4. 현재 위치 기반 심리 상태 계산
            current_position = self._get_current_position(market_data)
            psychology_ratios = self._calculate_psychology_ratios(kde_dist, current_position, returns)
            
            # 5. 감정 지수 및 리스크 레벨 계산
            sentiment_score = self._calculate_sentiment_score(psychology_ratios, kde_dist, returns)
            risk_level = self._assess_risk_level(sentiment_score, psychology_ratios, distribution_stats)
            
            # 6. 시각화 데이터 생성
            visualization_data = self._prepare_visualization_data(kde_dist, current_position, distribution_stats)
            
            # 7. 신뢰도 계산
            confidence_score = self._calculate_confidence_score(returns, distribution_stats)
            
            # 8. 해석 생성
            interpretation = self._generate_interpretation(
                psychology_ratios, sentiment_score, risk_level, distribution_stats, current_position
            )
            
            result = PsychologyResult(
                symbol=market_data.symbol,
                current_price=market_data.current_price,
                distribution_stats=distribution_stats,
                psychology_ratios=psychology_ratios,
                sentiment_score=sentiment_score,
                risk_level=risk_level,
                interpretation=interpretation,
                visualization_data=visualization_data,
                confidence_score=confidence_score
            )
            
            self.logger.info(f"심리 분석 완료: {market_data.symbol}")
            return result
            
        except Exception as e:
            self.logger.error(f"심리 분석 실패: {market_data.symbol}, 오류: {str(e)}")
            raise
    
    def _calculate_returns(self, price_data: pd.DataFrame) -> np.ndarray:
        """
        수익률 계산 (로그 수익률 사용)
        
        Args:
            price_data: 가격 데이터 DataFrame
            
        Returns:
            수익률 배열
        """
        close_prices = price_data['Close']
        
        # 단순 수익률 계산 (로그 수익률은 극값에서 불안정할 수 있음)
        returns = close_prices.pct_change().dropna()
        
        # 이상치 제거 (±50% 제한)
        returns = returns.clip(-0.5, 0.5)
        
        return returns.values
    
    def _estimate_kde_distribution(self, returns: np.ndarray) -> gaussian_kde:
        """
        KDE를 통한 분포 추정
        
        Args:
            returns: 수익률 배열
            
        Returns:
            gaussian_kde 객체
        """
        # 이상치 제거 (±3σ 범위)
        mean, std = np.mean(returns), np.std(returns)
        filtered_returns = returns[np.abs(returns - mean) <= 3 * std]
        
        if len(filtered_returns) < 5:
            # 필터링 후 데이터가 부족하면 원본 사용
            filtered_returns = returns
        
        # KDE 추정
        kde = gaussian_kde(filtered_returns)
        
        # 대역폭 조정 (스무딩 효과)
        kde.set_bandwidth(kde.factor * 0.8)
        
        return kde
    
    def _calculate_distribution_stats(self, returns: np.ndarray) -> DistributionStats:
        """
        분포 통계 계산
        
        Args:
            returns: 수익률 배열
            
        Returns:
            DistributionStats 객체
        """
        # 기본 통계
        mean = float(np.mean(returns))
        std = float(np.std(returns, ddof=1))
        skewness = float(stats.skew(returns))
        kurtosis = float(stats.kurtosis(returns))
        
        # 백분위 계산
        percentiles = np.percentile(returns, [5, 25, 50, 75, 95])
        
        # 피크 위치 (최빈값 근사)
        peak_position = float(np.median(returns))  # 중앙값을 피크로 근사
        
        return DistributionStats(
            mean=mean,
            std=std,
            skewness=skewness,
            kurtosis=kurtosis,
            peak_position=peak_position,
            percentile_5=float(percentiles[0]),
            percentile_25=float(percentiles[1]),
            percentile_50=float(percentiles[2]),
            percentile_75=float(percentiles[3]),
            percentile_95=float(percentiles[4])
        )
    
    def _get_current_position(self, market_data: MarketData) -> float:
        """
        현재 위치 (최근 수익률) 계산
        
        Args:
            market_data: 시장 데이터
            
        Returns:
            현재 위치 (수익률)
        """
        close_prices = market_data.price_data['Close']
        if len(close_prices) < 2:
            return 0.0
        
        # 최근 1일 수익률
        current_return = (close_prices.iloc[-1] - close_prices.iloc[-2]) / close_prices.iloc[-2]
        return float(current_return)
    
    def _calculate_psychology_ratios(
        self, 
        kde_dist: gaussian_kde, 
        current_position: float,
        returns: np.ndarray
    ) -> PsychologyRatios:
        """
        현재 위치 기반 매수/관망/매도 비율 계산
        
        Args:
            kde_dist: KDE 분포
            current_position: 현재 위치
            returns: 수익률 배열
            
        Returns:
            PsychologyRatios 객체
        """
        # 현재 위치의 백분위 계산
        position_percentile = self._calculate_percentile(returns, current_position)
        
        # 심리 비율 계산 (정규분포 가정)
        if position_percentile < 0.16:  # -1σ 이하 (과매도)
            buyers = 0.70 + (0.16 - position_percentile) * 0.5
            sellers = 0.10
            holders = 1.0 - buyers - sellers
        elif position_percentile > 0.84:  # +1σ 이상 (과매수)
            sellers = 0.60 + (position_percentile - 0.84) * 0.8
            buyers = 0.15
            holders = 1.0 - buyers - sellers
        else:  # 정상 범위
            # 현재 위치에 따른 선형 보간
            center_bias = abs(position_percentile - 0.5)  # 중앙에서의 거리
            
            if position_percentile < 0.5:  # 중앙 아래 (매수 성향)
                buyers = 0.45 + (0.5 - position_percentile) * 0.4
                sellers = 0.25 + (position_percentile - 0.16) * 0.3
            else:  # 중앙 위 (매도 성향)
                buyers = 0.35 - (position_percentile - 0.5) * 0.3
                sellers = 0.35 + (position_percentile - 0.5) * 0.4
            
            holders = 1.0 - buyers - sellers
        
        # 비율 정규화 및 범위 제한
        buyers = max(0.05, min(0.85, buyers))
        sellers = max(0.05, min(0.85, sellers))
        holders = max(0.10, min(0.80, holders))
        
        # 합계를 1로 정규화
        total = buyers + sellers + holders
        buyers /= total
        sellers /= total
        holders /= total
        
        return PsychologyRatios(
            buyers=buyers,
            holders=holders,
            sellers=sellers
        )
    
    def _calculate_percentile(self, returns: np.ndarray, current_position: float) -> float:
        """
        현재 위치의 백분위 계산
        
        Args:
            returns: 수익률 배열
            current_position: 현재 위치
            
        Returns:
            백분위 (0-1)
        """
        # 현재 위치보다 작은 값들의 비율
        below_count = np.sum(returns <= current_position)
        percentile = below_count / len(returns)
        
        return float(percentile)
    
    def _calculate_sentiment_score(
        self, 
        psychology_ratios: PsychologyRatios, 
        kde_dist: gaussian_kde,
        returns: np.ndarray
    ) -> float:
        """
        감정 지수 계산 (-1: 극도공포, 1: 극도탐욕)
        
        Args:
            psychology_ratios: 심리 비율
            kde_dist: KDE 분포
            returns: 수익률 배열
            
        Returns:
            감정 지수
        """
        # 기본 감정 점수 (매수자 - 매도자)
        base_sentiment = psychology_ratios.buyers - psychology_ratios.sellers
        
        # 변동성 조정
        volatility = np.std(returns)
        volatility_factor = min(0.3, volatility * 10)  # 변동성이 높을수록 감정이 극단적
        
        # 감정 증폭
        if base_sentiment > 0:
            sentiment = base_sentiment + volatility_factor
        else:
            sentiment = base_sentiment - volatility_factor
        
        # 범위 제한
        sentiment = max(-1.0, min(1.0, sentiment))
        
        return float(sentiment)
    
    def _assess_risk_level(
        self, 
        sentiment_score: float, 
        psychology_ratios: PsychologyRatios,
        distribution_stats: DistributionStats
    ) -> str:
        """
        리스크 레벨 평가
        
        Args:
            sentiment_score: 감정 지수
            psychology_ratios: 심리 비율
            distribution_stats: 분포 통계
            
        Returns:
            리스크 레벨 ('low', 'medium', 'high', 'extreme')
        """
        # 감정 지수 기반 리스크
        sentiment_risk = abs(sentiment_score)
        
        # 변동성 기반 리스크
        volatility_risk = min(1.0, distribution_stats.std * 20)
        
        # 불균형 기반 리스크 (매수/매도 비율 불균형)
        imbalance_risk = abs(psychology_ratios.buyers - psychology_ratios.sellers)
        
        # 종합 리스크 점수
        total_risk = (sentiment_risk * 0.4 + volatility_risk * 0.4 + imbalance_risk * 0.2)
        
        if total_risk >= 0.75:
            return "extreme"
        elif total_risk >= 0.5:
            return "high"
        elif total_risk >= 0.25:
            return "medium"
        else:
            return "low"
    
    def _prepare_visualization_data(
        self, 
        kde_dist: gaussian_kde, 
        current_position: float,
        distribution_stats: DistributionStats
    ) -> VisualizationData:
        """
        시각화 데이터 준비
        
        Args:
            kde_dist: KDE 분포
            current_position: 현재 위치
            distribution_stats: 분포 통계
            
        Returns:
            VisualizationData 객체
        """
        # X축 범위 설정 (평균 ± 3σ)
        x_min = distribution_stats.mean - 3 * distribution_stats.std
        x_max = distribution_stats.mean + 3 * distribution_stats.std
        
        # X값 생성
        x_values = np.linspace(x_min, x_max, 100)
        
        # KDE Y값 계산
        y_values = kde_dist(x_values)
        
        # 과매수/과매도 구간 정의
        oversold_threshold = distribution_stats.mean - 2 * distribution_stats.std
        overbought_threshold = distribution_stats.mean + 2 * distribution_stats.std
        
        zones = {
            'oversold': {
                'start': float(x_min),
                'end': float(oversold_threshold)
            },
            'normal': {
                'start': float(oversold_threshold),
                'end': float(overbought_threshold)
            },
            'overbought': {
                'start': float(overbought_threshold),
                'end': float(x_max)
            }
        }
        
        return VisualizationData(
            x_values=x_values.tolist(),
            y_values=y_values.tolist(),
            current_position=float(current_position),
            zones=zones
        )
    
    def _calculate_confidence_score(
        self, 
        returns: np.ndarray,
        distribution_stats: DistributionStats
    ) -> float:
        """
        분석 신뢰도 계산
        
        Args:
            returns: 수익률 배열
            distribution_stats: 분포 통계
            
        Returns:
            신뢰도 (0-1)
        """
        # 데이터 포인트 수 기반 신뢰도
        data_score = min(1.0, len(returns) / 100.0)  # 100개 이상이면 최대 점수
        
        # 분포 안정성 기반 신뢰도 (첨도가 정상범위에 있을수록 높음)
        kurtosis_score = max(0.1, 1.0 - abs(distribution_stats.kurtosis) / 10.0)
        
        # 변동성 기반 신뢰도 (적절한 변동성일 때 높음)
        volatility_score = max(0.1, 1.0 - min(1.0, distribution_stats.std * 20))
        
        # 종합 신뢰도
        confidence = (data_score * 0.4 + kurtosis_score * 0.3 + volatility_score * 0.3)
        
        return float(min(max(confidence, 0.1), 1.0))
    
    def _generate_interpretation(
        self,
        psychology_ratios: PsychologyRatios,
        sentiment_score: float,
        risk_level: str,
        distribution_stats: DistributionStats,
        current_position: float
    ) -> str:
        """
        심리 분석 해석 생성
        
        Args:
            psychology_ratios: 심리 비율
            sentiment_score: 감정 지수
            risk_level: 리스크 레벨
            distribution_stats: 분포 통계
            current_position: 현재 위치
            
        Returns:
            해석 문자열
        """
        interpretation_parts = []
        
        # 현재 심리 상태 분석
        if psychology_ratios.buyers > 0.6:
            interpretation_parts.append("매수 심리가 강한 상황입니다.")
        elif psychology_ratios.sellers > 0.5:
            interpretation_parts.append("매도 압력이 높은 상황입니다.")
        else:
            interpretation_parts.append("시장 참여자들이 관망하는 상황입니다.")
        
        # 감정 지수 해석
        if sentiment_score > 0.5:
            interpretation_parts.append("탐욕 지수가 높아 과열 가능성이 있습니다.")
        elif sentiment_score < -0.5:
            interpretation_parts.append("공포 지수가 높아 과도한 하락일 수 있습니다.")
        else:
            interpretation_parts.append("감정적 균형이 유지되고 있습니다.")
        
        # 리스크 레벨 해석
        risk_messages = {
            "low": "낮은 리스크로 안정적인 투자 환경입니다.",
            "medium": "중간 수준의 리스크가 있어 신중한 접근이 필요합니다.",
            "high": "높은 리스크 상황으로 주의가 필요합니다.",
            "extreme": "극도로 높은 리스크 상황으로 매우 주의해야 합니다."
        }
        interpretation_parts.append(risk_messages.get(risk_level, "리스크 평가를 확인하세요."))
        
        # 현재 위치 분석
        if current_position > distribution_stats.percentile_75:
            interpretation_parts.append("현재 위치가 상위 25% 구간으로 고점 근처입니다.")
        elif current_position < distribution_stats.percentile_25:
            interpretation_parts.append("현재 위치가 하위 25% 구간으로 저점 근처입니다.")
        else:
            interpretation_parts.append("현재 위치가 정상 범위 내에 있습니다.")
        
        return " ".join(interpretation_parts)