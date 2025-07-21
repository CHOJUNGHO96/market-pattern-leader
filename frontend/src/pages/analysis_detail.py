"""
PatternLeader Analysis Detail Page

분석 상세 페이지 구현
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from ..components.distribution_chart import (
    create_distribution_chart, get_distribution_insights, 
    render_distribution_analysis
)
from ..components.psychology_gauge import (
    create_psychology_comparison_chart, create_sentiment_thermometer
)
from ..utils.api_client import get_api_client, AnalysisResponse
from ..utils.visualizations import (
    format_percentage, format_price, create_analysis_metadata,
    get_sentiment_emoji, get_risk_color
)


def render_analysis_detail_page():
    """분석 상세 페이지 렌더링"""
    
    st.set_page_config(
        page_title="PatternLeader - 상세 분석",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 PatternLeader - 상세 분석")
    st.markdown("---")
    
    # 세션 상태에서 분석 결과 확인
    if 'analysis_result' not in st.session_state:
        st.warning("분석 결과가 없습니다. 먼저 메인 대시보드에서 분석을 실행해주세요.")
        if st.button("메인 대시보드로 이동"):
            st.switch_page("main_dashboard")
        return
    
    result = st.session_state.analysis_result
    
    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 분포 분석", 
        "🧠 심리 분석", 
        "📈 과거 추이", 
        "🔬 고급 분석"
    ])
    
    with tab1:
        _render_distribution_analysis_tab(result)
    
    with tab2:
        _render_psychology_analysis_tab(result)
    
    with tab3:
        _render_historical_trend_tab(result)
    
    with tab4:
        _render_advanced_analysis_tab(result)


def _render_distribution_analysis_tab(result: AnalysisResponse):
    """분포 분석 탭"""
    
    st.subheader("📊 수익률 분포 상세 분석")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 메인 분포 차트
        fig = create_distribution_chart(result.visualization_data, result.distribution_stats)
        st.plotly_chart(fig, use_container_width=True)
        
        # 인사이트
        insights = get_distribution_insights(result.distribution_stats, result.visualization_data.current_position)
        
        st.markdown("### 💡 분포 기반 인사이트")
        for key, insight in insights.items():
            st.info(f"**{key.title()}:** {insight}")
    
    with col2:
        # 분포 통계 요약
        st.markdown("### 📊 통계 요약")
        
        stats_df = pd.DataFrame({
            '지표': ['평균', '표준편차', '왜도', '첨도', '피크 위치'],
            '값': [
                f"{result.distribution_stats.mean:.3%}",
                f"{result.distribution_stats.std:.3%}",
                f"{result.distribution_stats.skewness:.3f}",
                f"{result.distribution_stats.kurtosis:.3f}",
                f"{result.distribution_stats.peak_position:.3%}"
            ],
            '해석': [
                _interpret_mean(result.distribution_stats.mean),
                _interpret_std(result.distribution_stats.std),
                _interpret_skewness(result.distribution_stats.skewness),
                _interpret_kurtosis(result.distribution_stats.kurtosis),
                _interpret_peak(result.distribution_stats.peak_position)
            ]
        })
        
        st.dataframe(stats_df, use_container_width=True)
        
        # 현재 위치 분석
        st.markdown("### 📍 현재 위치")
        
        current_percentile = _calculate_percentile(
            result.visualization_data.x_values,
            result.visualization_data.current_position
        )
        
        st.metric("위치 백분위", f"{current_percentile:.1%}")
        
        z_score = (result.visualization_data.current_position - result.distribution_stats.mean) / result.distribution_stats.std
        st.metric("Z-Score", f"{z_score:.2f}")
        
        if abs(z_score) > 2:
            st.warning("⚠️ 극단적 위치 (±2σ 벗어남)")
        elif abs(z_score) > 1:
            st.info("ℹ️ 비정상 위치 (±1σ 벗어남)")
        else:
            st.success("✅ 정상 범위 내 위치")


def _render_psychology_analysis_tab(result: AnalysisResponse):
    """심리 분석 탭"""
    
    st.subheader("🧠 시장 심리 상세 분석")
    
    # 상단: 주요 지표들
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "매수자 비율",
            f"{result.psychology_ratios.buyers:.1%}",
            help="시장에서 매수 의향을 가진 참여자 비율"
        )
    
    with col2:
        st.metric(
            "관망자 비율",
            f"{result.psychology_ratios.holders:.1%}",
            help="현재 포지션을 유지하며 관망하는 참여자 비율"
        )
    
    with col3:
        st.metric(
            "매도자 비율",
            f"{result.psychology_ratios.sellers:.1%}",
            help="시장에서 매도 의향을 가진 참여자 비율"
        )
    
    with col4:
        st.metric(
            "감정 지수",
            f"{result.sentiment_score:.3f}",
            delta=get_sentiment_emoji(result.sentiment_score),
            help="시장 참여자들의 종합적인 감정 상태"
        )
    
    st.markdown("---")
    
    # 차트 섹션
    col1, col2 = st.columns(2)
    
    with col1:
        # 심리 비율 시계열 (가상 데이터)
        st.markdown("### 📈 심리 변화 추이")
        trend_chart = _create_psychology_trend_chart(result)
        st.plotly_chart(trend_chart, use_container_width=True)
    
    with col2:
        # 감정 온도계
        st.markdown("### 🌡️ 감정 온도계")
        thermometer = create_sentiment_thermometer(result.sentiment_score)
        st.plotly_chart(thermometer, use_container_width=True)
    
    # 심리 상태 해석
    st.markdown("### 🎯 심리 상태 해석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💭 주요 특징")
        
        # 도미넌트 감정 분석
        ratios = [
            ("매수", result.psychology_ratios.buyers),
            ("관망", result.psychology_ratios.holders),
            ("매도", result.psychology_ratios.sellers)
        ]
        dominant_emotion = max(ratios, key=lambda x: x[1])
        
        st.write(f"**주도 감정:** {dominant_emotion[0]} ({dominant_emotion[1]:.1%})")
        
        # 균형도 분석
        balance_score = 1 - max(result.psychology_ratios.buyers, result.psychology_ratios.holders, result.psychology_ratios.sellers)
        st.write(f"**시장 균형도:** {balance_score:.1%}")
        
        # 변동성 예측
        volatility_prediction = _predict_volatility(result)
        st.write(f"**예상 변동성:** {volatility_prediction}")
    
    with col2:
        st.markdown("#### 📊 감정 구간별 분석")
        
        emotion_zones = [
            ("극도 공포", -1.0, -0.7, "#8B0000"),
            ("공포", -0.7, -0.3, "#DC143C"),  
            ("불안", -0.3, -0.1, "#FF6347"),
            ("중립", -0.1, 0.1, "#FFD700"),
            ("낙관", 0.1, 0.3, "#32CD32"),
            ("탐욕", 0.3, 0.7, "#228B22"),
            ("극도 탐욕", 0.7, 1.0, "#006400")
        ]
        
        current_zone = None
        for zone_name, min_val, max_val, color in emotion_zones:
            if min_val <= result.sentiment_score <= max_val:
                current_zone = zone_name
                st.markdown(f"**현재 구간:** {zone_name} 🎯")
                break
        
        # 구간별 권장 행동
        recommendations = {
            "극도 공포": "적극적 매수 타이밍, 분할 매수 전략",
            "공포": "저점 매수 기회 모색, 리스크 관리",
            "불안": "신중한 관찰, 추세 확인 대기",
            "중립": "방향성 결정 대기, 균형 잡힌 접근",
            "낙관": "포지션 조정, 수익 실현 고려",
            "탐욕": "과열 주의, 리스크 관리 강화",
            "극도 탐욕": "수익 실현 권장, 조정 대비"
        }
        
        if current_zone:
            st.info(f"**권장 전략:** {recommendations.get(current_zone, '정보 없음')}")


def _render_historical_trend_tab(result: AnalysisResponse):
    """과거 추이 탭"""
    
    st.subheader("📈 과거 심리 변화 추이")
    
    # API에서 과거 데이터 요청 (실제로는 백엔드에서 구현 필요)
    try:
        api_client = get_api_client()
        historical_data = api_client.get_historical_psychology(
            symbol=result.symbol,
            market_type="stock",  # 임시
            days=30
        )
        
        if historical_data:
            _display_historical_charts(historical_data)
        else:
            _display_mock_historical_data(result)
            
    except Exception as e:
        st.warning("과거 데이터를 불러올 수 없어 시뮬레이션 데이터를 표시합니다.")
        _display_mock_historical_data(result)


def _render_advanced_analysis_tab(result: AnalysisResponse):
    """고급 분석 탭"""
    
    st.subheader("🔬 고급 분석")
    
    # 고급 지표들
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 고급 통계 지표")
        
        # 샤프 비율 (가상)
        sharpe_ratio = _calculate_mock_sharpe_ratio(result)
        st.metric("샤프 비율", f"{sharpe_ratio:.3f}")
        
        # VaR (Value at Risk)
        var_95 = result.distribution_stats.mean - 1.645 * result.distribution_stats.std
        st.metric("VaR (95%)", f"{var_95:.2%}")
        
        # 왜도 조정 VaR
        adjusted_var = _calculate_adjusted_var(result.distribution_stats)
        st.metric("조정 VaR", f"{adjusted_var:.2%}")
        
        # 첨도 기반 꼬리 위험
        tail_risk = _calculate_tail_risk(result.distribution_stats)
        st.metric("꼬리 위험", tail_risk)
    
    with col2:
        st.markdown("### 🎯 예측 모델")
        
        # 다음 기간 예측 (가상)
        next_direction = _predict_next_direction(result)
        st.metric("예상 방향", next_direction)
        
        # 변동성 예측
        volatility_forecast = _forecast_volatility(result)
        st.metric("예상 변동성", volatility_forecast)
        
        # 반전 확률
        reversal_prob = _calculate_reversal_probability(result)
        st.metric("반전 확률", f"{reversal_prob:.1%}")
        
        # 지지/저항 레벨
        support_resistance = _calculate_support_resistance(result)
        st.write(f"**지지선:** ${support_resistance['support']:.2f}")
        st.write(f"**저항선:** ${support_resistance['resistance']:.2f}")
    
    st.markdown("---")
    
    # 시나리오 분석
    st.markdown("### 🎭 시나리오 분석")
    
    scenarios = _generate_scenarios(result)
    
    scenario_tabs = st.tabs(["📈 상승", "📊 보합", "📉 하락"])
    
    for i, (tab, (scenario_name, scenario_data)) in enumerate(zip(scenario_tabs, scenarios.items())):
        with tab:
            st.markdown(f"#### {scenario_name} 시나리오")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**확률:** {scenario_data['probability']:.1%}")
                st.write(f"**예상 수익률:** {scenario_data['expected_return']:.2%}")
                st.write(f"**기간:** {scenario_data['timeframe']}")
            
            with col2:
                st.write(f"**주요 요인:** {scenario_data['key_factors']}")
                st.write(f"**위험 요소:** {scenario_data['risks']}")
            
            # 시나리오별 권장 행동
            st.info(f"**권장 행동:** {scenario_data['recommendation']}")


def _interpret_mean(mean: float) -> str:
    """평균 해석"""
    if mean > 0.01:
        return "강한 상승 편향"
    elif mean > 0.005:
        return "상승 편향"
    elif mean > -0.005:
        return "중립적"
    elif mean > -0.01:
        return "하락 편향"
    else:
        return "강한 하락 편향"


def _interpret_std(std: float) -> str:
    """표준편차 해석"""
    if std > 0.05:
        return "매우 높은 변동성"
    elif std > 0.03:
        return "높은 변동성"
    elif std > 0.02:
        return "보통 변동성"
    elif std > 0.01:
        return "낮은 변동성"
    else:
        return "매우 낮은 변동성"


def _interpret_skewness(skewness: float) -> str:
    """왜도 해석"""
    if skewness > 1:
        return "강한 우편향"
    elif skewness > 0.5:
        return "우편향"
    elif skewness > -0.5:
        return "대칭"
    elif skewness > -1:
        return "좌편향"
    else:
        return "강한 좌편향"


def _interpret_kurtosis(kurtosis: float) -> str:
    """첨도 해석"""
    if kurtosis > 5:
        return "매우 뾰족함"
    elif kurtosis > 3:
        return "뾰족함"
    elif kurtosis > 1:
        return "보통"
    elif kurtosis > -1:
        return "평평함"
    else:
        return "매우 평평함"


def _interpret_peak(peak: float) -> str:
    """피크 위치 해석"""
    if peak > 0.01:
        return "상승 편향"
    elif peak > -0.01:
        return "균형"
    else:
        return "하락 편향"


def _calculate_percentile(x_values: List[float], current_position: float) -> float:
    """백분위 계산"""
    below_current = sum(1 for x in x_values if x <= current_position)
    return below_current / len(x_values)


def _create_psychology_trend_chart(result: AnalysisResponse) -> go.Figure:
    """심리 추이 차트 생성 (모의 데이터)"""
    
    # 30일 모의 데이터 생성
    dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
    
    # 현재 값 주변에서 변동
    np.random.seed(42)
    buyers_trend = result.psychology_ratios.buyers + np.random.normal(0, 0.05, 30)
    holders_trend = result.psychology_ratios.holders + np.random.normal(0, 0.03, 30)
    sellers_trend = result.psychology_ratios.sellers + np.random.normal(0, 0.05, 30)
    
    # 정규화
    for i in range(30):
        total = buyers_trend[i] + holders_trend[i] + sellers_trend[i]
        buyers_trend[i] /= total
        holders_trend[i] /= total
        sellers_trend[i] /= total
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates, y=buyers_trend * 100,
        mode='lines+markers',
        name='매수자',
        line=dict(color='green', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=holders_trend * 100,
        mode='lines+markers',
        name='관망자',
        line=dict(color='orange', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=sellers_trend * 100,
        mode='lines+markers',
        name='매도자',
        line=dict(color='red', width=2)
    ))
    
    fig.update_layout(
        title="30일 심리 변화 추이",
        xaxis_title="날짜",
        yaxis_title="비율 (%)",
        yaxis=dict(range=[0, 100]),
        height=400
    )
    
    return fig


def _predict_volatility(result: AnalysisResponse) -> str:
    """변동성 예측"""
    if result.distribution_stats.std > 0.04:
        return "높음"
    elif result.distribution_stats.std > 0.02:
        return "보통"
    else:
        return "낮음"


def _display_mock_historical_data(result: AnalysisResponse):
    """모의 과거 데이터 표시"""
    
    st.info("📊 실제 과거 데이터 대신 시뮬레이션 데이터를 표시합니다.")
    
    # 30일간 심리 지수 변화 (모의)
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    sentiment_history = np.random.normal(result.sentiment_score, 0.2, 30)
    sentiment_history = np.clip(sentiment_history, -1, 1)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=sentiment_history,
        mode='lines+markers',
        name='감정 지수',
        line=dict(color='blue', width=2)
    ))
    
    # 구간별 색상 추가
    fig.add_hline(y=0.7, line_dash="dash", line_color="red", annotation_text="극도 탐욕")
    fig.add_hline(y=0.3, line_dash="dash", line_color="orange", annotation_text="탐욕")
    fig.add_hline(y=-0.3, line_dash="dash", line_color="orange", annotation_text="공포")
    fig.add_hline(y=-0.7, line_dash="dash", line_color="red", annotation_text="극도 공포")
    
    fig.update_layout(
        title="📈 30일 감정 지수 변화",
        xaxis_title="날짜",
        yaxis_title="감정 지수",
        yaxis=dict(range=[-1, 1]),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def _display_historical_charts(historical_data: Dict):
    """실제 과거 데이터 차트 표시"""
    # 실제 백엔드 API에서 과거 데이터를 받아 차트 생성
    # 현재는 구현되지 않음
    pass


# 고급 분석 함수들 (모의 구현)
def _calculate_mock_sharpe_ratio(result: AnalysisResponse) -> float:
    """모의 샤프 비율 계산"""
    return result.distribution_stats.mean / result.distribution_stats.std if result.distribution_stats.std > 0 else 0


def _calculate_adjusted_var(dist_stats) -> float:
    """왜도 조정 VaR 계산"""
    return dist_stats.mean - 1.645 * dist_stats.std * (1 + dist_stats.skewness/6)


def _calculate_tail_risk(dist_stats) -> str:
    """꼬리 위험 계산"""
    if dist_stats.kurtosis > 5:
        return "높음"
    elif dist_stats.kurtosis > 3:
        return "보통"
    else:
        return "낮음"


def _predict_next_direction(result: AnalysisResponse) -> str:
    """다음 방향 예측"""
    if result.sentiment_score > 0.3:
        return "📈 상승"
    elif result.sentiment_score < -0.3:
        return "📉 하락"
    else:
        return "📊 보합"


def _forecast_volatility(result: AnalysisResponse) -> str:
    """변동성 예측"""
    return f"{result.distribution_stats.std * 100:.1f}%"


def _calculate_reversal_probability(result: AnalysisResponse) -> float:
    """반전 확률 계산"""
    extreme_sentiment = abs(result.sentiment_score)
    return min(extreme_sentiment * 50, 90)


def _calculate_support_resistance(result: AnalysisResponse) -> Dict[str, float]:
    """지지/저항선 계산"""
    current_price = result.current_price
    std_price = current_price * result.distribution_stats.std
    
    return {
        "support": current_price - 2 * std_price,
        "resistance": current_price + 2 * std_price
    }


def _generate_scenarios(result: AnalysisResponse) -> Dict[str, Dict]:
    """시나리오 생성"""
    
    scenarios = {
        "상승": {
            "probability": 40.0,
            "expected_return": 15.0,
            "timeframe": "3-6개월",
            "key_factors": "강한 매수 심리, 긍정적 뉴스",
            "risks": "과열 위험, 조정 가능성",
            "recommendation": "분할 매수, 익절 라인 설정"
        },
        "보합": {
            "probability": 35.0,
            "expected_return": 2.0,
            "timeframe": "1-3개월",
            "key_factors": "균형 잡힌 심리, 불확실성",
            "risks": "방향성 부재, 변동성 증가",
            "recommendation": "관망, 돌파 시점 대기"
        },
        "하락": {
            "probability": 25.0,
            "expected_return": -8.0,
            "timeframe": "1-2개월",
            "key_factors": "매도 압력, 부정적 요인",
            "risks": "추가 하락, 패닉 매도",
            "recommendation": "손절 고려, 현금 보유"
        }
    }
    
    return scenarios


if __name__ == "__main__":
    render_analysis_detail_page() 