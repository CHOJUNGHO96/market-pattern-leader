"""심리 분석기 테스트"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from src.services.psychology_analyzer import PsychologyAnalyzer
from src.models.market_data import MarketData


class TestPsychologyAnalyzer:
    """PsychologyAnalyzer 테스트 클래스"""
    
    @pytest.fixture
    def analyzer(self):
        """분석기 인스턴스"""
        return PsychologyAnalyzer()
    
    @pytest.fixture
    def sample_market_data(self):
        """샘플 시장 데이터"""
        # 30일간의 샘플 데이터 생성
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30, freq='D')
        
        # 기본 가격을 100으로 시작하여 랜덤 워크 생성
        np.random.seed(42)  # 재현 가능한 테스트를 위한 시드
        price_changes = np.random.normal(0, 0.02, 30)  # 평균 0%, 표준편차 2%
        
        prices = [100]
        for change in price_changes[:-1]:  # 마지막 제외
            new_price = prices[-1] * (1 + change)
            prices.append(new_price)
        
        # OHLC 데이터 생성
        price_data = pd.DataFrame({
            'Open': prices,
            'High': [p * 1.01 for p in prices],  # 고가는 1% 위
            'Low': [p * 0.99 for p in prices],   # 저가는 1% 아래
            'Close': prices
        }, index=dates)
        
        volume_data = pd.Series([1000000] * 30, index=dates)
        
        return MarketData(
            symbol="TEST-USD",
            market_type="crypto",
            price_data=price_data,
            volume_data=volume_data,
            timestamp=datetime.now(),
            period="1mo"
        )
    
    def test_analyze_psychology_basic(self, analyzer, sample_market_data):
        """기본 심리 분석 테스트"""
        result = analyzer.analyze_psychology(sample_market_data)
        
        # 기본 속성 검증
        assert result.symbol == "TEST-USD"
        assert result.current_price > 0
        assert result.confidence_score >= 0 and result.confidence_score <= 1
        assert result.risk_level in ["low", "medium", "high", "extreme"]
        assert result.sentiment_score >= -1 and result.sentiment_score <= 1
        
        # 심리 비율 검증
        ratios = result.psychology_ratios
        assert ratios.buyers >= 0 and ratios.buyers <= 1
        assert ratios.sellers >= 0 and ratios.sellers <= 1
        assert ratios.holders >= 0 and ratios.holders <= 1
        
        # 비율 합계 검증 (1에 가까워야 함)
        total_ratio = ratios.buyers + ratios.sellers + ratios.holders
        assert abs(total_ratio - 1.0) < 0.01
        
        # 해석 텍스트 존재 확인
        assert isinstance(result.interpretation, str)
        assert len(result.interpretation) > 0
    
    def test_calculate_returns(self, analyzer, sample_market_data):
        """수익률 계산 테스트"""
        returns = analyzer._calculate_returns(sample_market_data.price_data)
        
        # 반환값 검증
        assert isinstance(returns, np.ndarray)
        assert len(returns) == len(sample_market_data.price_data) - 1  # 첫 번째 제외
        
        # 수익률 범위 검증 (±50% 제한)
        assert all(return_val >= -0.5 and return_val <= 0.5 for return_val in returns)
    
    def test_estimate_kde_distribution(self, analyzer):
        """KDE 분포 추정 테스트"""
        # 정규분포 샘플 데이터
        np.random.seed(42)
        sample_returns = np.random.normal(0, 0.02, 100)
        
        kde_dist = analyzer._estimate_kde_distribution(sample_returns)
        
        # KDE 객체 타입 확인
        from scipy.stats import gaussian_kde
        assert isinstance(kde_dist, gaussian_kde)
        
        # KDE 함수 동작 확인
        test_points = np.array([0.0, 0.01, -0.01])
        densities = kde_dist(test_points)
        
        assert len(densities) == 3
        assert all(density >= 0 for density in densities)
    
    def test_calculate_distribution_stats(self, analyzer):
        """분포 통계 계산 테스트"""
        # 알려진 분포의 샘플 데이터
        np.random.seed(42)
        sample_returns = np.random.normal(0.01, 0.02, 100)  # 평균 1%, 표준편차 2%
        
        stats = analyzer._calculate_distribution_stats(sample_returns)
        
        # 통계값 범위 검증
        assert abs(stats.mean - 0.01) < 0.01  # 평균이 대략 1%
        assert abs(stats.std - 0.02) < 0.01   # 표준편차가 대략 2%
        assert stats.percentile_50 == stats.peak_position  # 중앙값 = 피크
        
        # 백분위 순서 검증
        assert stats.percentile_5 < stats.percentile_25
        assert stats.percentile_25 < stats.percentile_50
        assert stats.percentile_50 < stats.percentile_75
        assert stats.percentile_75 < stats.percentile_95
    
    def test_calculate_psychology_ratios_oversold(self, analyzer):
        """과매도 상황에서의 심리 비율 계산 테스트"""
        # 모의 KDE와 과매도 위치
        np.random.seed(42)
        sample_returns = np.random.normal(0, 0.02, 100)
        kde_dist = analyzer._estimate_kde_distribution(sample_returns)
        
        # 과매도 상황 (분포의 낮은 백분위)
        current_position = np.percentile(sample_returns, 10)  # 10번째 백분위
        
        ratios = analyzer._calculate_psychology_ratios(kde_dist, current_position, sample_returns)
        
        # 과매도에서는 매수자 비율이 높아야 함
        assert ratios.buyers > ratios.sellers
    
    def test_calculate_psychology_ratios_overbought(self, analyzer):
        """과매수 상황에서의 심리 비율 계산 테스트"""
        # 모의 KDE와 과매수 위치
        np.random.seed(42)
        sample_returns = np.random.normal(0, 0.02, 100)
        kde_dist = analyzer._estimate_kde_distribution(sample_returns)
        
        # 과매수 상황 (분포의 높은 백분위)
        current_position = np.percentile(sample_returns, 90)  # 90번째 백분위
        
        ratios = analyzer._calculate_psychology_ratios(kde_dist, current_position, sample_returns)
        
        # 과매수에서는 매도자 비율이 높아야 함
        assert ratios.sellers > ratios.buyers
    
    def test_calculate_sentiment_score(self, analyzer):
        """감정 지수 계산 테스트"""
        from src.models.analysis_result import PsychologyRatios
        
        # 모의 KDE
        np.random.seed(42)
        sample_returns = np.random.normal(0, 0.02, 100)
        kde_dist = analyzer._estimate_kde_distribution(sample_returns)
        
        # 매수 우세 상황
        ratios_bullish = PsychologyRatios(buyers=0.7, holders=0.2, sellers=0.1)
        sentiment_bullish = analyzer._calculate_sentiment_score(ratios_bullish, kde_dist, sample_returns)
        
        # 매도 우세 상황
        ratios_bearish = PsychologyRatios(buyers=0.1, holders=0.2, sellers=0.7)
        sentiment_bearish = analyzer._calculate_sentiment_score(ratios_bearish, kde_dist, sample_returns)
        
        # 매수 우세가 더 높은 감정 지수를 가져야 함
        assert sentiment_bullish > sentiment_bearish
        
        # 범위 확인
        assert -1 <= sentiment_bullish <= 1
        assert -1 <= sentiment_bearish <= 1
    
    def test_assess_risk_level(self, analyzer):
        """리스크 레벨 평가 테스트"""
        from src.models.analysis_result import PsychologyRatios, DistributionStats
        
        # 낮은 리스크 상황
        low_risk_ratios = PsychologyRatios(buyers=0.4, holders=0.4, sellers=0.2)
        low_risk_stats = DistributionStats(
            mean=0.001, std=0.01, skewness=0.1, kurtosis=0.1, peak_position=0.001,
            percentile_5=-0.02, percentile_25=-0.005, percentile_50=0.001,
            percentile_75=0.007, percentile_95=0.025
        )
        
        risk_level = analyzer._assess_risk_level(0.1, low_risk_ratios, low_risk_stats)
        
        # 낮은 리스크여야 함
        assert risk_level in ["low", "medium"]
        
        # 높은 리스크 상황
        high_risk_ratios = PsychologyRatios(buyers=0.9, holders=0.05, sellers=0.05)
        high_risk_stats = DistributionStats(
            mean=0.05, std=0.1, skewness=2.0, kurtosis=5.0, peak_position=0.05,
            percentile_5=-0.15, percentile_25=-0.05, percentile_50=0.05,
            percentile_75=0.15, percentile_95=0.25
        )
        
        risk_level_high = analyzer._assess_risk_level(0.8, high_risk_ratios, high_risk_stats)
        
        # 높은 리스크여야 함
        assert risk_level_high in ["high", "extreme"]
    
    def test_prepare_visualization_data(self, analyzer):
        """시각화 데이터 준비 테스트"""
        # 모의 데이터
        np.random.seed(42)
        sample_returns = np.random.normal(0, 0.02, 100)
        kde_dist = analyzer._estimate_kde_distribution(sample_returns)
        
        from src.models.analysis_result import DistributionStats
        distribution_stats = DistributionStats(
            mean=0.0, std=0.02, skewness=0.0, kurtosis=0.0, peak_position=0.0,
            percentile_5=-0.04, percentile_25=-0.01, percentile_50=0.0,
            percentile_75=0.01, percentile_95=0.04
        )
        
        current_position = 0.01
        
        viz_data = analyzer._prepare_visualization_data(kde_dist, current_position, distribution_stats)
        
        # 시각화 데이터 검증
        assert len(viz_data.x_values) == 100
        assert len(viz_data.y_values) == 100
        assert len(viz_data.x_values) == len(viz_data.y_values)
        assert viz_data.current_position == current_position
        
        # 구간 정보 확인
        assert "oversold" in viz_data.zones
        assert "normal" in viz_data.zones
        assert "overbought" in viz_data.zones
        
        # Y값이 모두 양수인지 확인 (밀도 함수)
        assert all(y >= 0 for y in viz_data.y_values)
    
    def test_calculate_confidence_score(self, analyzer):
        """신뢰도 계산 테스트"""
        from src.models.analysis_result import DistributionStats
        
        # 많은 데이터, 안정적인 분포
        np.random.seed(42)
        many_returns = np.random.normal(0, 0.02, 200)
        stable_stats = DistributionStats(
            mean=0.0, std=0.02, skewness=0.1, kurtosis=0.1, peak_position=0.0,
            percentile_5=-0.04, percentile_25=-0.01, percentile_50=0.0,
            percentile_75=0.01, percentile_95=0.04
        )
        
        confidence_high = analyzer._calculate_confidence_score(many_returns, stable_stats)
        
        # 적은 데이터, 불안정한 분포
        few_returns = np.random.normal(0, 0.1, 20)
        unstable_stats = DistributionStats(
            mean=0.05, std=0.1, skewness=2.0, kurtosis=5.0, peak_position=0.05,
            percentile_5=-0.15, percentile_25=-0.05, percentile_50=0.05,
            percentile_75=0.15, percentile_95=0.25
        )
        
        confidence_low = analyzer._calculate_confidence_score(few_returns, unstable_stats)
        
        # 신뢰도 범위 확인
        assert 0 <= confidence_high <= 1
        assert 0 <= confidence_low <= 1
        
        # 안정적인 경우가 더 높은 신뢰도를 가져야 함
        assert confidence_high > confidence_low
    
    def test_edge_case_insufficient_data(self, analyzer):
        """데이터 부족 상황 테스트"""
        # 매우 적은 데이터로 MarketData 생성
        dates = pd.date_range(start=datetime.now() - timedelta(days=5), periods=5, freq='D')
        price_data = pd.DataFrame({
            'Open': [100, 101, 102, 103, 104],
            'High': [101, 102, 103, 104, 105],
            'Low': [99, 100, 101, 102, 103],
            'Close': [100, 101, 102, 103, 104]
        }, index=dates)
        
        volume_data = pd.Series([1000000] * 5, index=dates)
        
        market_data = MarketData(
            symbol="TEST-USD",
            market_type="crypto",
            price_data=price_data,
            volume_data=volume_data,
            timestamp=datetime.now(),
            period="5d"
        )
        
        # 데이터가 부족하면 예외 발생해야 함
        with pytest.raises(ValueError, match="충분한 수익률 데이터가 없습니다"):
            analyzer.analyze_psychology(market_data)