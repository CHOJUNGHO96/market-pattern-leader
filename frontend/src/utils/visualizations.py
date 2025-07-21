"""
PatternLeader Visualizations

차트 및 시각화 헬퍼 함수들
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
import streamlit as st


def get_sentiment_emoji(sentiment_score: float) -> str:
    """감정 지수에 따른 이모지 반환"""
    if sentiment_score <= -0.7:
        return "😱"  # 극도 공포
    elif sentiment_score <= -0.3:
        return "😰"  # 공포  
    elif sentiment_score <= -0.1:
        return "😟"  # 불안
    elif sentiment_score <= 0.1:
        return "😐"  # 중립
    elif sentiment_score <= 0.3:
        return "🙂"  # 낙관
    elif sentiment_score <= 0.7:
        return "😊"  # 탐욕
    else:
        return "🤑"  # 극도 탐욕


def get_risk_color(risk_level: str) -> str:
    """리스크 레벨에 따른 색상 반환"""
    colors = {
        "low": "🟢",
        "medium": "🟡", 
        "high": "🟠",
        "extreme": "🔴"
    }
    return colors.get(risk_level.lower(), "⚪")


def get_sentiment_color(sentiment_score: float) -> str:
    """감정 지수에 따른 색상 반환"""
    if sentiment_score <= -0.5:
        return "#ff4444"  # 빨강 (공포)
    elif sentiment_score <= 0:
        return "#ff8800"  # 주황 (불안)
    elif sentiment_score <= 0.5:
        return "#00aa00"  # 초록 (낙관)
    else:
        return "#0066ff"  # 파랑 (탐욕)


def format_price(price: float, symbol: str = "") -> str:
    """가격 포맷팅"""
    if price >= 1000000:
        return f"${price/1000000:.2f}M"
    elif price >= 1000:
        return f"${price/1000:.1f}K"
    elif price >= 1:
        return f"${price:.2f}"
    else:
        return f"${price:.6f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """백분율 포맷팅"""
    return f"{value * 100:.{decimals}f}%"


def create_psychology_breakdown_text(ratios: Dict[str, float]) -> str:
    """심리 비율 텍스트 설명 생성"""
    buyers = ratios.get('buyers', 0) * 100
    holders = ratios.get('holders', 0) * 100  
    sellers = ratios.get('sellers', 0) * 100
    
    dominant = max(ratios.items(), key=lambda x: x[1])
    
    if dominant[0] == 'buyers':
        trend = "매수세"
        emoji = "📈"
    elif dominant[0] == 'sellers':
        trend = "매도세"
        emoji = "📉"
    else:
        trend = "관망세"
        emoji = "⏸️"
    
    return f"""
    **현재 시장 심리 구성:**
    - 매수자: {buyers:.1f}%
    - 관망자: {holders:.1f}%
    - 매도자: {sellers:.1f}%
    
    {emoji} **{trend}가 우세한 상황입니다.**
    """


def create_risk_level_description(risk_level: str, sentiment_score: float) -> str:
    """리스크 레벨 설명 생성"""
    descriptions = {
        "low": "낮은 리스크 구간입니다. 안정적인 투자 환경으로 보입니다.",
        "medium": "중간 리스크 구간입니다. 신중한 접근이 필요합니다.",
        "high": "높은 리스크 구간입니다. 변동성이 클 수 있으니 주의하세요.",
        "extreme": "극도로 위험한 구간입니다. 투자 전 충분한 검토가 필요합니다."
    }
    
    base_desc = descriptions.get(risk_level.lower(), "리스크 평가가 불가능합니다.")
    
    if abs(sentiment_score) > 0.7:
        base_desc += " 감정적 과열 상태로 냉정한 판단이 중요합니다."
    
    return base_desc


def create_interpretation_summary(psychology_ratios: Dict[str, float], 
                                sentiment_score: float, 
                                risk_level: str) -> str:
    """종합적인 해석 요약 생성"""
    
    # 주요 심리 상태 판단
    buyers_pct = psychology_ratios.get('buyers', 0) * 100
    sellers_pct = psychology_ratios.get('sellers', 0) * 100
    holders_pct = psychology_ratios.get('holders', 0) * 100
    
    if buyers_pct > 60:
        main_sentiment = "강한 매수 심리"
        recommendation = "과도한 추격매수 주의"
    elif sellers_pct > 50:
        main_sentiment = "강한 매도 심리"  
        recommendation = "저점 매수 기회 모색"
    elif holders_pct > 50:
        main_sentiment = "관망 심리 우세"
        recommendation = "방향성 확인 후 진입"
    else:
        main_sentiment = "혼재된 심리 상태"
        recommendation = "신중한 관찰 필요"
    
    # 감정 지수 해석
    if sentiment_score > 0.5:
        emotion_state = "탐욕 구간"
    elif sentiment_score > 0:
        emotion_state = "낙관 구간"
    elif sentiment_score > -0.5:
        emotion_state = "불안 구간"
    else:
        emotion_state = "공포 구간"
    
    return f"""
    **📊 종합 분석 요약**
    
    **현재 상황:** {main_sentiment} ({emotion_state})
    **리스크 수준:** {risk_level.upper()}
    **투자 고려사항:** {recommendation}
    
    **심리 구성비:**
    • 매수자 {buyers_pct:.0f}% | 관망자 {holders_pct:.0f}% | 매도자 {sellers_pct:.0f}%
    """


def create_distribution_zone_info(current_position: float, zones: Dict[str, Dict]) -> str:
    """현재 위치의 분포 구간 정보 생성"""
    
    zone_info = "**현재 위치 분석:**\n\n"
    
    # 현재 위치가 어떤 구간에 있는지 확인
    current_zone = "정상 구간"
    
    if 'oversold' in zones:
        oversold = zones['oversold']
        if oversold['start'] <= current_position <= oversold['end']:
            current_zone = "과매도 구간"
    
    if 'overbought' in zones:
        overbought = zones['overbought']
        if overbought['start'] <= current_position <= overbought['end']:
            current_zone = "과매수 구간"
    
    zone_info += f"• 현재 위치: **{current_zone}**\n"
    zone_info += f"• 수익률 위치: {current_position*100:.2f}%\n\n"
    
    # 구간별 의미 설명
    if current_zone == "과매도 구간":
        zone_info += "💡 **과매도 구간**은 일반적으로 반등 가능성이 높은 구간입니다."
    elif current_zone == "과매수 구간":
        zone_info += "⚠️ **과매수 구간**은 조정 가능성을 염두에 두어야 합니다."
    else:
        zone_info += "📊 **정상 구간**에서 균형잡힌 심리 상태를 보이고 있습니다."
    
    return zone_info


def create_confidence_indicator(confidence_score: float) -> Tuple[str, str]:
    """신뢰도 지표 생성"""
    
    if confidence_score >= 0.8:
        level = "높음"
        color = "green"
        description = "분석 결과의 신뢰도가 높습니다."
    elif confidence_score >= 0.6:
        level = "보통"
        color = "orange"
        description = "분석 결과를 참고용으로 활용하세요."
    else:
        level = "낮음"
        color = "red"
        description = "데이터가 부족하거나 변동성이 높아 신뢰도가 낮습니다."
    
    return level, description


def get_period_display_name(period: str) -> str:
    """기간 코드를 표시명으로 변환"""
    period_names = {
        "1mo": "1개월",
        "3mo": "3개월", 
        "6mo": "6개월",
        "1y": "1년"
    }
    return period_names.get(period, period)


def get_market_display_name(market_type: str) -> str:
    """시장 타입을 표시명으로 변환"""
    market_names = {
        "stock": "주식",
        "crypto": "암호화폐"
    }
    return market_names.get(market_type, market_type)


def create_analysis_metadata(analysis_data: Any) -> str:
    """분석 메타데이터 생성"""
    timestamp = analysis_data.analysis_timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    return f"""
    **분석 정보**
    - 종목: {analysis_data.symbol}
    - 분석 시각: {timestamp}
    - 현재 가격: {format_price(analysis_data.current_price)}
    - 신뢰도: {format_percentage(analysis_data.confidence_score)}
    """ 