"""
PatternLeader Distribution Chart Component

KDE 분포 곡선 차트 생성 컴포넌트
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import streamlit as st
from typing import Dict, Any
from ..utils.api_client import VisualizationData, DistributionStats


def _is_valid_numeric(value: float) -> bool:
    """
    숫자값 유효성 검증
    
    Args:
        value: 검증할 숫자값
        
    Returns:
        bool: 유효한 숫자인지 여부 (NaN, inf 제외)
    """
    return value is not None and np.isfinite(value) and not np.isnan(value)


def create_distribution_chart(viz_data: VisualizationData, distribution_stats: DistributionStats) -> go.Figure:
    """
    KDE 분포 곡선 차트 생성
    
    Args:
        viz_data: 시각화 데이터
        distribution_stats: 분포 통계
        
    Returns:
        go.Figure: Plotly 차트 객체
    """
    
    fig = go.Figure()
    
    # 분포 곡선 추가
    fig.add_trace(go.Scatter(
        x=viz_data.x_values,
        y=viz_data.y_values,
        mode='lines',
        name='수익률 분포',
        line=dict(color='#1f77b4', width=3),
        fill='tonexty',
        fillcolor='rgba(31, 119, 180, 0.1)',
        hovertemplate='수익률: %{x:.2%}<br>확률 밀도: %{y:.2f}<extra></extra>'
    ))
    
    # 현재 위치 표시 (유효성 검증 포함)
    if _is_valid_numeric(viz_data.current_position):
        current_y = np.interp(viz_data.current_position, viz_data.x_values, viz_data.y_values)
        if _is_valid_numeric(current_y):
            fig.add_trace(go.Scatter(
                x=[viz_data.current_position],
                y=[current_y],
                mode='markers+text',
                name='현재 위치',
                marker=dict(
                    color='red', 
                    size=15, 
                    symbol='diamond',
                    line=dict(color='darkred', width=2)
                ),
                text=['현재'],
                textposition='top center',
                textfont=dict(size=12, color='red'),
                hovertemplate='현재 위치<br>수익률: %{x:.2%}<extra></extra>'
            ))
    
    # 평균선 추가 (유효성 검증 포함)
    if _is_valid_numeric(distribution_stats.mean):
        max_y = max(viz_data.y_values) if viz_data.y_values else 1.0
        fig.add_trace(go.Scatter(
            x=[distribution_stats.mean, distribution_stats.mean],
            y=[0, max_y * 0.8],
            mode='lines',
            name='평균',
            line=dict(color='gray', width=2, dash='dot'),
            hovertemplate='평균: %{x:.2%}<extra></extra>'
        ))
    
    # 과매수/과매도 구간 표시 (데이터 유효성 검증 포함)
    if 'oversold' in viz_data.zones:
        oversold = viz_data.zones['oversold']
        if (_is_valid_numeric(oversold.get('start')) and 
            _is_valid_numeric(oversold.get('end'))):
            try:
                fig.add_vrect(
                    x0=oversold['start'],
                    x1=oversold['end'],
                    fillcolor="green",
                    opacity=0.2,
                    line_width=0,
                    annotation_text="과매도",
                    annotation_position="top left",
                    annotation=dict(font_size=10, font_color="green")
                )
            except Exception:
                # annotation 없이 fallback
                fig.add_vrect(
                    x0=oversold['start'],
                    x1=oversold['end'],
                    fillcolor="green",
                    opacity=0.2,
                    line_width=0
                )
    
    if 'overbought' in viz_data.zones:
        overbought = viz_data.zones['overbought']
        if (_is_valid_numeric(overbought.get('start')) and 
            _is_valid_numeric(overbought.get('end'))):
            try:
                fig.add_vrect(
                    x0=overbought['start'],
                    x1=overbought['end'],
                    fillcolor="red",
                    opacity=0.2,
                    line_width=0,
                    annotation_text="과매수",
                    annotation_position="top right",
                    annotation=dict(font_size=10, font_color="red")
                )
            except Exception:
                # annotation 없이 fallback
                fig.add_vrect(
                    x0=overbought['start'],
                    x1=overbought['end'],
                    fillcolor="red",
                    opacity=0.2,
                    line_width=0
                )
    
    # ±1σ, ±2σ 구간 표시 (데이터 유효성 검증 포함)
    std = distribution_stats.std
    mean = distribution_stats.mean
    
    # 통계값 유효성 검증
    if _is_valid_numeric(mean) and _is_valid_numeric(std) and std > 0:
        # ±1σ 구간 (68%)
        try:
            fig.add_vrect(
                x0=mean - std,
                x1=mean + std,
                fillcolor="blue",
                opacity=0.1,
                line_width=0,
                annotation_text="68% 구간",
                annotation_position="bottom center",
                annotation=dict(font_size=8, font_color="blue")
            )
        except Exception as e:
            # annotation_position fallback
            fig.add_vrect(
                x0=mean - std,
                x1=mean + std,
                fillcolor="blue",
                opacity=0.1,
                line_width=0
            )
        
        # ±2σ 구간 (95%)
        fig.add_vrect(
            x0=mean - 2*std,
            x1=mean + 2*std,
            fillcolor="purple",
            opacity=0.05,
            line_width=0
        )
    
    # 레이아웃 설정
    fig.update_layout(
        title={
            'text': "📊 수익률 분포 및 현재 시장 위치",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        xaxis_title="수익률 (%)",
        yaxis_title="확률 밀도",
        xaxis=dict(
            tickformat='.1%',
            gridcolor='lightgray',
            gridwidth=1
        ),
        yaxis=dict(
            gridcolor='lightgray',
            gridwidth=1
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=450,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # 통계 정보 추가 (오른쪽 상단) - 유효성 검증 포함
    stats_parts = []
    
    if _is_valid_numeric(distribution_stats.mean):
        stats_parts.append(f"평균: {distribution_stats.mean:.2%}")
    
    if _is_valid_numeric(distribution_stats.std):
        stats_parts.append(f"표준편차: {distribution_stats.std:.2%}")
    
    if _is_valid_numeric(distribution_stats.skewness):
        stats_parts.append(f"왜도: {distribution_stats.skewness:.2f}")
    
    if _is_valid_numeric(distribution_stats.kurtosis):
        stats_parts.append(f"첨도: {distribution_stats.kurtosis:.2f}")
    
    if stats_parts:  # 유효한 통계값이 하나라도 있는 경우에만 표시
        stats_text = "\n".join(stats_parts)
        fig.add_annotation(
            text=stats_text,
            xref="paper", yref="paper",
            x=0.98, y=0.98,
            xanchor="right", yanchor="top",
            showarrow=False,
            font=dict(size=10, color="gray"),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="gray",
            borderwidth=1
        )
    
    return fig


def create_simplified_distribution_chart(viz_data: VisualizationData) -> go.Figure:
    """
    간소화된 분포 차트 (모바일 최적화)
    
    Args:
        viz_data: 시각화 데이터
        
    Returns:
        go.Figure: 간소화된 Plotly 차트 객체
    """
    
    fig = go.Figure()
    
    # 분포 곡선만 표시
    fig.add_trace(go.Scatter(
        x=viz_data.x_values,
        y=viz_data.y_values,
        mode='lines',
        name='분포',
        line=dict(color='#1f77b4', width=2),
        fill='tonexty',
        fillcolor='rgba(31, 119, 180, 0.2)'
    ))
    
    # 현재 위치만 표시
    current_y = np.interp(viz_data.current_position, viz_data.x_values, viz_data.y_values)
    fig.add_trace(go.Scatter(
        x=[viz_data.current_position],
        y=[current_y],
        mode='markers',
        name='현재',
        marker=dict(color='red', size=12, symbol='diamond')
    ))
    
    fig.update_layout(
        title="분포 및 현재 위치",
        xaxis_title="수익률",
        yaxis_title="밀도",
        showlegend=False,
        height=300,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig


def render_distribution_analysis(viz_data: VisualizationData, 
                               distribution_stats: DistributionStats,
                               current_price: float,
                               symbol: str) -> None:
    """
    분포 분석 결과를 Streamlit에 렌더링
    
    Args:
        viz_data: 시각화 데이터
        distribution_stats: 분포 통계
        current_price: 현재 가격
        symbol: 종목 코드
    """
    
    st.subheader("📊 수익률 분포 분석")
    
    # 차트 표시
    chart = create_distribution_chart(viz_data, distribution_stats)
    st.plotly_chart(chart, use_container_width=True)
    
    # 분포 해석
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 분포 특성")
        
        # 왜도 해석
        if abs(distribution_stats.skewness) < 0.5:
            skew_desc = "대칭적 분포"
            skew_emoji = "⚖️"
        elif distribution_stats.skewness > 0:
            skew_desc = "우편향 (상승 편향)"
            skew_emoji = "📈"
        else:
            skew_desc = "좌편향 (하락 편향)"
            skew_emoji = "📉"
        
        # 첨도 해석
        if distribution_stats.kurtosis > 3:
            kurt_desc = "뾰족한 분포 (높은 변동성)"
            kurt_emoji = "⚡"
        elif distribution_stats.kurtosis < -1:
            kurt_desc = "평평한 분포 (낮은 변동성)"
            kurt_emoji = "📊"
        else:
            kurt_desc = "정상 분포"
            kurt_emoji = "📈"
        
        st.write(f"{skew_emoji} **분포 형태:** {skew_desc}")
        st.write(f"{kurt_emoji} **변동성:** {kurt_desc}")
        
    with col2:
        st.markdown("### 📍 현재 위치")
        
        # 현재 위치 백분위 계산 (근사)
        position_percentile = len([x for x in viz_data.x_values if x <= viz_data.current_position]) / len(viz_data.x_values)
        
        st.metric(
            "위치 백분위",
            f"{position_percentile:.1%}",
            help="전체 수익률 분포에서 현재 위치의 백분위"
        )
        
        # 평균 대비 위치
        diff_from_mean = viz_data.current_position - distribution_stats.mean
        if abs(diff_from_mean) < distribution_stats.std * 0.5:
            position_desc = "평균 근처"
        elif diff_from_mean > 0:
            position_desc = "평균 이상"
        else:
            position_desc = "평균 이하"
        
        st.write(f"**평균 대비:** {position_desc}")
        st.write(f"**편차:** {diff_from_mean:.2%}")


def get_distribution_insights(distribution_stats: DistributionStats, 
                            current_position: float) -> Dict[str, str]:
    """
    분포 기반 인사이트 생성
    
    Args:
        distribution_stats: 분포 통계
        current_position: 현재 위치
        
    Returns:
        Dict: 인사이트 딕셔너리
    """
    
    insights = {}
    
    # 표준편차 기반 변동성 평가
    if distribution_stats.std > 0.05:  # 5% 이상
        insights['volatility'] = "높은 변동성 - 리스크 관리 필수"
    elif distribution_stats.std > 0.02:  # 2% 이상
        insights['volatility'] = "보통 변동성 - 적절한 리스크 수준"
    else:
        insights['volatility'] = "낮은 변동성 - 안정적 움직임"
    
    # 현재 위치 기반 추천
    z_score = (current_position - distribution_stats.mean) / distribution_stats.std
    
    if z_score < -2:
        insights['position'] = "극도 과매도 - 반등 가능성 높음"
    elif z_score < -1:
        insights['position'] = "과매도 - 매수 기회 고려"
    elif z_score > 2:
        insights['position'] = "극도 과매수 - 조정 위험 높음"
    elif z_score > 1:
        insights['position'] = "과매수 - 신중한 접근 필요"
    else:
        insights['position'] = "정상 범위 - 추세 관찰 필요"
    
    # 왜도 기반 추세 전망
    if distribution_stats.skewness > 1:
        insights['trend'] = "상승 모멘텀 강함 - 추가 상승 가능"
    elif distribution_stats.skewness < -1:
        insights['trend'] = "하락 압력 강함 - 추가 하락 주의"
    else:
        insights['trend'] = "균형 잡힌 상태 - 방향성 대기"
    
    return insights 