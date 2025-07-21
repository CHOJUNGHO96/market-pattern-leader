"""
PatternLeader Main Dashboard

메인 대시보드 페이지 구현
"""

import streamlit as st
import plotly.graph_objects as go
import requests
from typing import Optional
import time

# 컴포넌트 임포트
from ..components.distribution_chart import create_distribution_chart, render_distribution_analysis
from ..components.psychology_gauge import render_psychology_dashboard, get_psychology_interpretation
from ..components.market_selector import MarketSelector, render_market_status
from ..utils.api_client import get_api_client, AnalysisResponse
from ..utils.visualizations import (
    get_sentiment_emoji, get_risk_color, format_price, format_percentage,
    create_psychology_breakdown_text, create_risk_level_description,
    create_interpretation_summary, create_analysis_metadata,
    get_market_display_name, get_period_display_name
)


def render_main_dashboard():
    """메인 대시보드 렌더링"""
    
    # 페이지 설정
    st.set_page_config(
        page_title="PatternLeader - 시장 심리 분석",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 메인 타이틀
    st.title("📊 PatternLeader - 시장 심리 분석")
    st.markdown("---")
    
    # 사이드바: 시장 선택기
    market_selector = MarketSelector()
    selection = market_selector.render_selector()
    
    # 고급 옵션
    advanced_options = market_selector.render_advanced_options()
    
    # 종목 정보 패널
    market_selector.render_symbol_info_panel(selection.symbol, selection.market_type)
    
    # 시장 상태 정보
    render_market_status()
    
    # 메인 영역
    if st.sidebar.button("🔍 분석 시작", type="primary", use_container_width=True):
        _perform_analysis(selection, advanced_options)
    
    # 분석 결과 표시 영역
    if 'analysis_result' in st.session_state:
        _display_analysis_results(st.session_state.analysis_result, selection)
    else:
        _display_welcome_screen()


def _perform_analysis(selection, advanced_options):
    """분석 수행"""
    
    # 입력 검증
    market_selector = MarketSelector()
    is_valid, error_msg = market_selector.validate_symbol(selection.symbol, selection.market_type)
    
    if not is_valid:
        st.error(f"❌ {error_msg}")
        return
    
    # API 클라이언트 가져오기
    api_client = get_api_client()
    
    # 서버 상태 확인
    if not api_client.check_server_health():
        st.error("❌ API 서버에 연결할 수 없습니다. 서버 상태를 확인해주세요.")
        st.info("💡 백엔드 서버를 먼저 실행해주세요: `cd backend && python main.py`")
        return
    
    try:
        # 분석 실행
        with st.spinner(f"📊 {selection.symbol} 분석 중..."):
            
            # 진행률 표시
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("📥 데이터 수집 중...")
            progress_bar.progress(25)
            time.sleep(0.5)
            
            status_text.text("🧮 분포 계산 중...")
            progress_bar.progress(50)
            time.sleep(0.5)
            
            status_text.text("🧠 심리 분석 중...")
            progress_bar.progress(75)
            time.sleep(0.5)
            
            # API 호출
            result = api_client.get_analysis(
                symbol=selection.symbol,
                market_type=selection.market_type,
                period=selection.period,
                exchange=selection.exchange
            )
            
            status_text.text("✅ 분석 완료!")
            progress_bar.progress(100)
            time.sleep(0.5)
            
            # 결과 저장
            st.session_state.analysis_result = result
            
            # UI 정리
            progress_bar.empty()
            status_text.empty()
            
            st.success("🎉 분석이 완료되었습니다!")
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API 요청 실패: {str(e)}")
        
        # 에러 상세 정보
        with st.expander("🔍 오류 세부 정보"):
            st.code(str(e))
            st.info("💡 문제 해결 방법:")
            st.write("1. 백엔드 서버가 실행 중인지 확인")
            st.write("2. 종목 코드가 올바른지 확인")  
            st.write("3. 네트워크 연결 상태 확인")
            
    except Exception as e:
        st.error(f"❌ 예상치 못한 오류: {str(e)}")
        
        with st.expander("🔍 오류 세부 정보"):
            st.code(str(e))


def _display_analysis_results(result: AnalysisResponse, selection):
    """분석 결과 표시"""
    
    st.subheader(f"📊 {result.symbol} 분석 결과")
    
    # 1. 요약 카드 섹션
    _render_summary_cards(result)
    
    st.markdown("---")
    
    # 2. 메인 차트 섹션
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 분포 차트
        st.subheader("📈 수익률 분포 및 현재 위치")
        distribution_fig = create_distribution_chart(result.visualization_data, result.distribution_stats)
        st.plotly_chart(distribution_fig, use_container_width=True)
        
    with col2:
        # 심리 분석 차트들
        render_psychology_dashboard(result.psychology_ratios, result.sentiment_score)
    
    st.markdown("---")
    
    # 3. 해석 및 인사이트 섹션
    _render_interpretation_section(result)
    
    st.markdown("---")
    
    # 4. 상세 분석 섹션
    _render_detailed_analysis(result, selection)
    
    # 5. 메타데이터 및 면책 조항
    _render_footer_info(result)


def _render_summary_cards(result: AnalysisResponse):
    """요약 카드 렌더링"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        sentiment_emoji = get_sentiment_emoji(result.sentiment_score)
        st.metric(
            "현재 가격",
            format_price(result.current_price),
            help="분석 시점 기준 가격"
        )
    
    with col2:
        st.metric(
            "감정 지수",
            f"{result.sentiment_score:.2f}",
            delta=f"{sentiment_emoji}",
            help="시장 감정 상태 (-1: 극도공포, 1: 극도탐욕)"
        )
    
    with col3:
        risk_color = get_risk_color(result.risk_level)
        st.metric(
            "리스크 레벨",
            result.risk_level.upper(),
            delta=f"{risk_color}",
            help="투자 위험도 평가"
        )
    
    with col4:
        confidence_level = "높음" if result.confidence_score > 0.8 else "보통" if result.confidence_score > 0.6 else "낮음"
        st.metric(
            "분석 신뢰도",
            f"{result.confidence_score:.1%}",
            delta=confidence_level,
            help="분석 결과의 신뢰도"
        )


def _render_interpretation_section(result: AnalysisResponse):
    """해석 및 인사이트 섹션"""
    
    st.subheader("🎯 종합 분석 해석")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 주요 해석
        st.markdown("### 📝 현재 시장 상황")
        interpretation = get_psychology_interpretation(result.psychology_ratios, result.sentiment_score)
        st.markdown(interpretation)
        
        # 투자 시사점
        st.markdown("### 💡 투자 가이드라인")
        investment_guide = _generate_investment_guidelines(result)
        st.markdown(investment_guide)
    
    with col2:
        # 심리 구성 요약
        st.markdown("### 🧠 심리 구성")
        psychology_text = create_psychology_breakdown_text({
            'buyers': result.psychology_ratios.buyers,
            'holders': result.psychology_ratios.holders,
            'sellers': result.psychology_ratios.sellers
        })
        st.markdown(psychology_text)
        
        # 리스크 평가
        st.markdown("### ⚠️ 리스크 평가")
        risk_desc = create_risk_level_description(result.risk_level, result.sentiment_score)
        st.info(risk_desc)


def _render_detailed_analysis(result: AnalysisResponse, selection):
    """상세 분석 섹션"""
    
    with st.expander("🔍 상세 분석 보기", expanded=False):
        
        # 분포 통계
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 분포 통계")
            stats_data = {
                "평균 수익률": f"{result.distribution_stats.mean:.2%}",
                "표준편차": f"{result.distribution_stats.std:.2%}",
                "왜도": f"{result.distribution_stats.skewness:.3f}",
                "첨도": f"{result.distribution_stats.kurtosis:.3f}",
                "피크 위치": f"{result.distribution_stats.peak_position:.2%}"
            }
            
            for key, value in stats_data.items():
                st.write(f"**{key}:** {value}")
        
        with col2:
            st.markdown("#### 🎯 심리 분석 세부사항")
            psychology_data = {
                "매수자 비율": f"{result.psychology_ratios.buyers:.1%}",
                "관망자 비율": f"{result.psychology_ratios.holders:.1%}",
                "매도자 비율": f"{result.psychology_ratios.sellers:.1%}",
                "감정 지수": f"{result.sentiment_score:.3f}",
                "신뢰도": f"{result.confidence_score:.1%}"
            }
            
            for key, value in psychology_data.items():
                st.write(f"**{key}:** {value}")
        
        # 분석 설정 정보
        st.markdown("#### ⚙️ 분석 설정")
        settings_info = f"""
        - **종목:** {result.symbol}
        - **시장:** {get_market_display_name(selection.market_type)}
        - **기간:** {get_period_display_name(selection.period)}
        - **분석 시각:** {result.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}
        """
        if selection.exchange:
            settings_info += f"\n- **거래소:** {selection.exchange.title()}"
        
        st.markdown(settings_info)


def _render_footer_info(result: AnalysisResponse):
    """푸터 정보 렌더링"""
    
    st.markdown("---")
    
    # 메타데이터
    metadata = create_analysis_metadata(result)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(metadata)
    
    with col2:
        st.markdown("#### ⚠️ 투자 유의사항")
        st.warning("""
        **면책 조항:**
        - 본 분석은 투자 참고 자료일 뿐, 투자 권유가 아닙니다.
        - 과거 데이터 기반 분석으로 미래 수익을 보장하지 않습니다.
        - 투자 결정은 본인의 판단과 책임 하에 진행하세요.
        - 손실에 대한 책임은 투자자 본인에게 있습니다.
        """)


def _display_welcome_screen():
    """환영 화면 표시"""
    
    st.markdown("""
    ## 👋 PatternLeader에 오신 것을 환영합니다!
    
    **PatternLeader**는 AI 기반 시장 심리 분석 서비스입니다.
    
    ### 🎯 주요 기능
    
    📊 **KDE 분포 분석**
    - 과거 수익률 데이터의 확률 분포 추정
    - 현재 위치의 통계적 의미 분석
    - 과매수/과매도 구간 자동 탐지
    
    🧠 **심리 상태 분석** 
    - 매수자/관망자/매도자 비율 계산
    - 감정 지수를 통한 시장 심리 수치화
    - 리스크 레벨 자동 평가
    
    📈 **직관적 시각화**
    - 분포 곡선과 현재 위치 표시
    - 심리 비율 파이차트 및 게이지
    - 인터랙티브 차트로 상세 정보 제공
    
    ### 🚀 시작하기
    
    1. **사이드바**에서 시장 타입 선택 (주식/암호화폐)
    2. **종목 코드** 입력 또는 인기 종목 선택
    3. **분석 기간** 설정 (1개월~1년)
    4. **🔍 분석 시작** 버튼 클릭
    
    ### 💡 사용 팁
    
    - 인기 종목은 버튼을 클릭하여 빠르게 선택 가능
    - 분석 결과는 자동으로 캐시되어 빠른 재조회 가능  
    - 고급 설정에서 차트 스타일과 상세도 조정 가능
    - 여러 종목 비교 기능으로 상대적 분석 가능
    
    ### 📞 지원
    
    문의사항이나 피드백은 GitHub Issues를 통해 연락주세요.
    """)
    
    # 샘플 차트 표시
    with st.expander("📊 샘플 분석 결과 미리보기"):
        _display_sample_charts()


def _display_sample_charts():
    """샘플 차트 표시"""
    
    import numpy as np
    
    # 샘플 데이터 생성
    x = np.linspace(-0.1, 0.1, 100)
    y = np.exp(-0.5 * (x / 0.03) ** 2)  # 가우시안 형태
    
    # 샘플 분포 차트
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='lines',
        name='수익률 분포',
        fill='tonexty',
        line=dict(color='blue', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=[0.02],
        y=[0.8],
        mode='markers',
        name='현재 위치',
        marker=dict(color='red', size=10, symbol='diamond')
    ))
    
    fig.update_layout(
        title="📊 샘플: 수익률 분포 분석",
        xaxis_title="수익률 (%)",
        yaxis_title="확률 밀도",
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)


def _generate_investment_guidelines(result: AnalysisResponse) -> str:
    """투자 가이드라인 생성"""
    
    buyers_pct = result.psychology_ratios.buyers * 100
    sellers_pct = result.psychology_ratios.sellers * 100
    sentiment = result.sentiment_score
    risk = result.risk_level
    
    guidelines = []
    
    # 심리 기반 가이드라인
    if buyers_pct > 70:
        guidelines.append("🔴 **과도한 매수 심리** - 단기 조정 가능성 높음, 신중한 접근 필요")
    elif buyers_pct > 50:
        guidelines.append("🟡 **강한 매수 심리** - 모멘텀 투자 고려, 리스크 관리 필수")
    elif sellers_pct > 60:
        guidelines.append("🟢 **강한 매도 심리** - 역투자 기회 모색, 분할 매수 고려")
    else:
        guidelines.append("⚪ **균형 잡힌 심리** - 추세 확인 후 투자 방향 결정")
    
    # 감정 지수 기반 가이드라인
    if sentiment > 0.7:
        guidelines.append("⚠️ **극도 탐욕** - 과열 구간, 수익 실현 고려")
    elif sentiment > 0.3:
        guidelines.append("📈 **탐욕 구간** - 상승 모멘텀 있으나 과열 주의")
    elif sentiment < -0.7:
        guidelines.append("💰 **극도 공포** - 저점 매수 기회, 장기 관점 접근")
    elif sentiment < -0.3:
        guidelines.append("📉 **공포 구간** - 반등 기대, 분할 매수 전략")
    
    # 리스크 레벨 기반 가이드라인
    if risk == "extreme":
        guidelines.append("🚨 **극도 위험** - 투자 금액 최소화, 손절 준비")
    elif risk == "high":
        guidelines.append("⚠️ **높은 위험** - 포지션 크기 조절, 스톱로스 설정")
    elif risk == "medium":
        guidelines.append("📊 **중간 위험** - 적절한 포지션 크기 유지")
    else:
        guidelines.append("✅ **낮은 위험** - 안정적 투자 환경")
    
    return "\n".join([f"- {guideline}" for guideline in guidelines])


# 페이지 실행
if __name__ == "__main__":
    render_main_dashboard() 