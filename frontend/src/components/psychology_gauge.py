"""
PatternLeader Psychology Gauge Component

심리 비율 게이지 차트 생성 컴포넌트
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import streamlit as st
from typing import Dict, List, Tuple
from ..utils.api_client import PsychologyRatios
from ..utils.visualizations import get_sentiment_emoji, format_percentage


def create_psychology_gauge(psychology_ratios: PsychologyRatios) -> go.Figure:
    """
    심리 비율 게이지 차트 생성
    
    Args:
        psychology_ratios: 심리 비율 데이터
        
    Returns:
        go.Figure: Plotly 게이지 차트 객체
    """
    
    # 데이터 준비
    buyers_pct = psychology_ratios.buyers * 100
    holders_pct = psychology_ratios.holders * 100
    sellers_pct = psychology_ratios.sellers * 100
    
    # 도미넌트 감정 계산
    dominant_emotion = max(
        ('매수', buyers_pct),
        ('관망', holders_pct), 
        ('매도', sellers_pct)
    )[0]
    
    # 게이지 값 계산 (매수자 비율 기준)
    gauge_value = buyers_pct
    
    fig = go.Figure()
    
    # 메인 게이지 추가
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=gauge_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "🧠 시장 심리 게이지", 'font': {'size': 18}},
        number={'suffix': "%", 'font': {'size': 24}},
        delta={'reference': 50, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': "lightgray"},  # 매도 우세
                {'range': [30, 70], 'color': "lightblue"},  # 균형
                {'range': [70, 100], 'color': "lightgreen"}  # 매수 우세
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    # 레이아웃 설정
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        font={'color': "darkblue"},
        paper_bgcolor="white"
    )
    
    return fig


def create_psychology_pie_chart(psychology_ratios: PsychologyRatios) -> go.Figure:
    """
    심리 비율 파이 차트 생성
    
    Args:
        psychology_ratios: 심리 비율 데이터
        
    Returns:
        go.Figure: Plotly 파이 차트 객체
    """
    
    # 데이터 준비
    labels = ['매수자', '관망자', '매도자']
    values = [
        psychology_ratios.buyers * 100,
        psychology_ratios.holders * 100,
        psychology_ratios.sellers * 100
    ]
    colors = ['#2E8B57', '#FFD700', '#DC143C']  # 매수(초록), 관망(노랑), 매도(빨강)
    
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        marker_colors=colors,
        textinfo='label+percent',
        textposition='auto',
        textfont_size=12,
        hovertemplate='<b>%{label}</b><br>비율: %{percent}<br>값: %{value:.1f}%<extra></extra>',
        hole=0.4  # 도넛 차트
    ))
    
    # 중앙에 도미넌트 감정 표시
    dominant_idx = values.index(max(values))
    dominant_label = labels[dominant_idx]
    dominant_emoji = {'매수자': '📈', '관망자': '⏸️', '매도자': '📉'}[dominant_label]
    
    fig.add_annotation(
        text=f"{dominant_emoji}<br><b>{dominant_label}<br>우세</b>",
        x=0.5, y=0.5,
        font_size=16,
        showarrow=False
    )
    
    fig.update_layout(
        title={
            'text': "🧠 시장 참여자 심리 구성",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        height=350,
        margin=dict(l=20, r=20, t=60, b=60)
    )
    
    return fig


def create_psychology_bar_chart(psychology_ratios: PsychologyRatios) -> go.Figure:
    """
    심리 비율 막대 차트 생성
    
    Args:
        psychology_ratios: 심리 비율 데이터
        
    Returns:
        go.Figure: Plotly 막대 차트 객체
    """
    
    # 데이터 준비
    categories = ['매수자', '관망자', '매도자']
    values = [
        psychology_ratios.buyers * 100,
        psychology_ratios.holders * 100,
        psychology_ratios.sellers * 100
    ]
    colors = ['#2E8B57', '#FFD700', '#DC143C']
    emojis = ['📈', '⏸️', '📉']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        marker_color=colors,
        text=[f"{emojis[i]}<br>{v:.1f}%" for i, v in enumerate(values)],
        textposition='auto',
        textfont={'size': 14, 'color': 'white'},
        hovertemplate='<b>%{x}</b><br>비율: %{y:.1f}%<extra></extra>'
    ))
    
    # 50% 기준선 추가
    fig.add_hline(
        y=50, 
        line_dash="dash", 
        line_color="gray",
        annotation_text="균형선 (50%)",
        annotation_position="bottom right"
    )
    
    fig.update_layout(
        title={
            'text': "📊 시장 심리 비율 분석",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        xaxis_title="참여자 유형",
        yaxis_title="비율 (%)",
        yaxis=dict(range=[0, 100]),
        showlegend=False,
        height=350,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig


def create_sentiment_thermometer(sentiment_score: float) -> go.Figure:
    """
    감정 온도계 차트 생성
    
    Args:
        sentiment_score: 감정 지수 (-1 ~ 1)
        
    Returns:
        go.Figure: Plotly 온도계 차트 객체
    """
    
    # 감정 지수를 0-100 스케일로 변환
    thermometer_value = (sentiment_score + 1) * 50
    
    # 감정 단계 정의
    if sentiment_score <= -0.7:
        emotion_text = "극도 공포 😱"
        color = "#8B0000"
    elif sentiment_score <= -0.3:
        emotion_text = "공포 😰"
        color = "#DC143C"
    elif sentiment_score <= -0.1:
        emotion_text = "불안 😟"
        color = "#FF6347"
    elif sentiment_score <= 0.1:
        emotion_text = "중립 😐"
        color = "#FFD700"
    elif sentiment_score <= 0.3:
        emotion_text = "낙관 🙂"
        color = "#32CD32"
    elif sentiment_score <= 0.7:
        emotion_text = "탐욕 😊"
        color = "#228B22"
    else:
        emotion_text = "극도 탐욕 🤑"
        color = "#006400"
    
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=thermometer_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"🌡️ 감정 온도계<br><b>{emotion_text}</b>", 'font': {'size': 14}},
        number={'font': {'size': 1, 'color': 'rgba(0,0,0,0)'}},  # 숫자 숨김 (투명 처리)
        gauge={
            'axis': {
                'range': [None, 100], 
                'tickmode': 'array',
                'tickvals': [10, 30, 50, 70, 90],
                'ticktext': ['극도공포', '공포', '중립', '탐욕', '극도탐욕'],
                'tickfont': {'size': 10}
            },
            'bar': {'color': color, 'thickness': 0.8},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 20], 'color': "#FFE4E1"},   # 극도 공포
                {'range': [20, 40], 'color': "#FFCCCB"},  # 공포
                {'range': [40, 60], 'color': "#FFFACD"},  # 중립
                {'range': [60, 80], 'color': "#98FB98"},  # 탐욕
                {'range': [80, 100], 'color': "#90EE90"}  # 극도 탐욕
            ],
            'threshold': {
                'line': {'color': "black", 'width': 3},
                'thickness': 0.75,
                'value': thermometer_value
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=10, r=10, t=40, b=10),
        font={'color': "darkblue"},
        paper_bgcolor="white"
    )
    
    return fig


def render_psychology_dashboard(psychology_ratios: PsychologyRatios, 
                              sentiment_score: float) -> None:
    """
    심리 분석 대시보드 렌더링
    
    Args:
        psychology_ratios: 심리 비율 데이터
        sentiment_score: 감정 지수
    """
    
    st.subheader("🧠 시장 참여자 심리 분석")
    
    # 상단: 주요 지표
    col1, col2, col3 = st.columns(3)
    
    with col1:
        buyers_pct = psychology_ratios.buyers * 100
        st.metric(
            "매수자 비율",
            f"{buyers_pct:.1f}%",
            delta=f"{buyers_pct - 33.3:.1f}%p",
            help="시장에서 매수 의향을 보이는 참여자 비율"
        )
    
    with col2:
        holders_pct = psychology_ratios.holders * 100
        st.metric(
            "관망자 비율", 
            f"{holders_pct:.1f}%",
            delta=f"{holders_pct - 33.3:.1f}%p",
            help="현재 포지션을 유지하며 관망하는 참여자 비율"
        )
    
    with col3:
        sellers_pct = psychology_ratios.sellers * 100
        st.metric(
            "매도자 비율",
            f"{sellers_pct:.1f}%", 
            delta=f"{sellers_pct - 33.3:.1f}%p",
            help="시장에서 매도 의향을 보이는 참여자 비율"
        )
    
    # 중단: 차트 영역
    col1, col2 = st.columns(2)
    
    with col1:
        # 파이 차트
        pie_chart = create_psychology_pie_chart(psychology_ratios)
        st.plotly_chart(pie_chart, use_container_width=True)
    
    with col2:
        # 감정 온도계
        thermometer = create_sentiment_thermometer(sentiment_score)
        st.plotly_chart(thermometer, use_container_width=True)
    
    # 하단: 막대 차트
    bar_chart = create_psychology_bar_chart(psychology_ratios)
    st.plotly_chart(bar_chart, use_container_width=True)


def get_psychology_interpretation(psychology_ratios: PsychologyRatios, 
                                sentiment_score: float) -> str:
    """
    심리 분석 해석 텍스트 생성
    
    Args:
        psychology_ratios: 심리 비율 데이터
        sentiment_score: 감정 지수
        
    Returns:
        str: 해석 텍스트
    """
    
    # 주요 비율 계산
    buyers_pct = psychology_ratios.buyers * 100
    holders_pct = psychology_ratios.holders * 100
    sellers_pct = psychology_ratios.sellers * 100
    
    # 도미넌트 감정 판단
    max_ratio = max(buyers_pct, holders_pct, sellers_pct)
    
    if max_ratio == buyers_pct:
        dominant = "매수 심리"
        emoji = "📈"
        if buyers_pct > 70:
            intensity = "매우 강한"
            warning = "⚠️ 과도한 매수 심리로 조정 위험이 있습니다."
        elif buyers_pct > 50:
            intensity = "강한"
            warning = "💡 상승 모멘텀이 있지만 신중한 접근이 필요합니다."
        else:
            intensity = "약한"
            warning = "📊 균형 잡힌 상태에서 약간의 매수 우세를 보입니다."
    elif max_ratio == sellers_pct:
        dominant = "매도 심리"
        emoji = "📉"
        if sellers_pct > 60:
            intensity = "매우 강한"
            warning = "💡 강한 매도 압력으로 저점 매수 기회를 고려해볼 수 있습니다."
        elif sellers_pct > 45:
            intensity = "강한"
            warning = "⚠️ 하락 압력이 있어 신중한 관찰이 필요합니다."
        else:
            intensity = "약한"
            warning = "📊 약간의 매도 우세를 보이지만 큰 변화는 없습니다."
    else:
        dominant = "관망 심리"
        emoji = "⏸️"
        if holders_pct > 60:
            intensity = "매우 강한"
            warning = "🤔 대부분이 관망 중으로 방향성 결정을 기다리는 상황입니다."
        else:
            intensity = "강한"
            warning = "📊 관망세가 우세하여 추세 전환점을 주목해야 합니다."
    
    # 감정 지수 해석
    if sentiment_score > 0.5:
        emotion_desc = "탐욕 상태"
    elif sentiment_score > 0:
        emotion_desc = "낙관 상태"
    elif sentiment_score > -0.5:
        emotion_desc = "불안 상태"
    else:
        emotion_desc = "공포 상태"
    
    interpretation = f"""
    **🎯 현재 시장 심리 요약**
    
    {emoji} **{intensity} {dominant}**가 시장을 지배하고 있습니다.
    전체적으로 시장은 **{emotion_desc}**를 보이고 있습니다.
    
    **📊 구성 비율:**
    • 매수자: {buyers_pct:.1f}%
    • 관망자: {holders_pct:.1f}%  
    • 매도자: {sellers_pct:.1f}%
    
    **💭 투자 시사점:**
    {warning}
    """
    
    return interpretation


def create_psychology_comparison_chart(ratios_list: List[PsychologyRatios], 
                                     labels: List[str]) -> go.Figure:
    """
    여러 시점의 심리 비율 비교 차트
    
    Args:
        ratios_list: 심리 비율 데이터 리스트
        labels: 시점 라벨 리스트
        
    Returns:
        go.Figure: 비교 차트
    """
    
    fig = go.Figure()
    
    # 매수자 비율
    buyers_values = [r.buyers * 100 for r in ratios_list]
    fig.add_trace(go.Scatter(
        x=labels,
        y=buyers_values,
        mode='lines+markers',
        name='매수자',
        line=dict(color='green', width=3),
        marker=dict(size=8)
    ))
    
    # 관망자 비율
    holders_values = [r.holders * 100 for r in ratios_list]
    fig.add_trace(go.Scatter(
        x=labels,
        y=holders_values,
        mode='lines+markers',
        name='관망자',
        line=dict(color='orange', width=3),
        marker=dict(size=8)
    ))
    
    # 매도자 비율
    sellers_values = [r.sellers * 100 for r in ratios_list]
    fig.add_trace(go.Scatter(
        x=labels,
        y=sellers_values,
        mode='lines+markers',
        name='매도자',
        line=dict(color='red', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="📈 시장 심리 변화 추이",
        xaxis_title="시점",
        yaxis_title="비율 (%)",
        yaxis=dict(range=[0, 100]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=400
    )
    
    return fig 