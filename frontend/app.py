"""
PatternLeader Streamlit Main App

메인 애플리케이션 진입점
"""

import streamlit as st
import sys
import os

# 프로젝트 루트 디렉토리를 Python 패스에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)

try:
    from src.pages.main_dashboard import render_main_dashboard
    from src.pages.analysis_detail import render_analysis_detail_page
except ImportError as e:
    st.error(f"모듈 임포트 오류: {e}")
    st.stop()


def main():
    """메인 애플리케이션"""
    
    # Streamlit 설정
    st.set_page_config(
        page_title="PatternLeader - 시장 심리 분석",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/your-repo/pattern-leader',
            'Report a bug': 'https://github.com/your-repo/pattern-leader/issues',
            'About': """
            # PatternLeader 📊
            
            AI 기반 시장 심리 분석 서비스
            
            **주요 기능:**
            - KDE 분포 분석
            - 심리 상태 분석  
            - 리스크 평가
            - 투자 가이드라인 제공
            
            **개발:** PatternLeader Team
            **버전:** 1.0.0
            """
        }
    )
    
    # 사이드바 네비게이션
    st.sidebar.title("📊 PatternLeader")
    st.sidebar.markdown("---")
    
    # 페이지 선택
    page = st.sidebar.selectbox(
        "페이지 선택",
        ["메인 대시보드", "상세 분석"],
        index=0,
        help="분석하고 싶은 페이지를 선택하세요"
    )
    
    # 앱 정보
    with st.sidebar.expander("ℹ️ 앱 정보"):
        st.write("**버전:** 1.0.0")
        st.write("**업데이트:** 2024-01-01")
        st.write("**상태:** 베타")
        
        st.markdown("### 📞 지원")
        st.write("- GitHub Issues")
        st.write("- 이메일 문의")
        st.write("- 사용자 가이드")
    
    # 시스템 상태
    with st.sidebar.expander("🔧 시스템 상태"):
        # 백엔드 연결 상태 확인
        try:
            from src.utils.api_client import get_api_client
            api_client = get_api_client()
            
            if api_client.check_server_health():
                st.success("✅ 백엔드 서버 연결됨")
            else:
                st.error("❌ 백엔드 서버 연결 실패")
                st.info("백엔드 서버를 실행해주세요:\n`cd backend && python main.py`")
        except Exception as e:
            st.error(f"❌ 연결 확인 실패: {str(e)}")
        
        # 세션 정보
        st.write(f"**세션 ID:** {st.session_state.get('session_id', 'N/A')}")
        
        # 캐시 상태
        cache_size = len(st.session_state)
        st.write(f"**캐시 크기:** {cache_size} 항목")
    
    # 페이지 라우팅
    if page == "메인 대시보드":
        render_main_dashboard()
    elif page == "상세 분석":
        render_analysis_detail_page()
    
    # 푸터
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.8em;'>
        © 2024 PatternLeader Team<br>
        AI-Powered Market Psychology Analysis
        </div>
        """, 
        unsafe_allow_html=True
    )


def initialize_session_state():
    """세션 상태 초기화"""
    
    if 'session_id' not in st.session_state:
        import uuid
        st.session_state.session_id = str(uuid.uuid4())[:8]
    
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {
            'theme': 'default',
            'language': 'ko',
            'cache_enabled': True,
            'notifications': False
        }


def handle_errors():
    """전역 에러 핸들링"""
    
    try:
        return True
    except Exception as e:
        st.error(f"애플리케이션 오류가 발생했습니다: {str(e)}")
        
        with st.expander("🔍 오류 세부 정보"):
            st.code(str(e))
            
            st.markdown("### 📋 문제 해결 방법:")
            st.write("1. 페이지를 새로고침해보세요")
            st.write("2. 브라우저 캐시를 지워보세요") 
            st.write("3. 백엔드 서버가 실행 중인지 확인하세요")
            st.write("4. 문제가 지속되면 GitHub Issues에 신고해주세요")
        
        return False


def setup_custom_css():
    """커스텀 CSS 스타일 설정"""
    
    st.markdown("""
    <style>
    /* 메인 컨테이너 스타일 */
    .main > div {
        padding-top: 2rem;
    }
    
    /* 사이드바 스타일 */
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    /* 메트릭 카드 스타일 */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        border-radius: 0.5rem;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #1565c0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* 성공 메시지 스타일 */
    .stSuccess {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        border-radius: 0.25rem;
    }
    
    /* 경고 메시지 스타일 */
    .stWarning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 0.25rem;
    }
    
    /* 오류 메시지 스타일 */
    .stError {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 0.25rem;
    }
    
    /* 차트 컨테이너 스타일 */
    .stPlotlyChart {
        background-color: white;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* 데이터프레임 스타일 */
    .stDataFrame {
        border-radius: 0.5rem;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 확장 가능한 섹션 스타일 */
    .streamlit-expanderHeader {
        background-color: #f1f3f4;
        border-radius: 0.25rem;
        padding: 0.5rem;
    }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border-radius: 0.25rem 0.25rem 0 0;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
    
    /* 진행률 바 스타일 */
    .stProgress > div > div > div {
        background-color: #1f77b4;
    }
    
    /* 선택 박스 스타일 */
    .stSelectbox > div > div {
        background-color: white;
        border-radius: 0.25rem;
    }
    
    /* 텍스트 입력 스타일 */
    .stTextInput > div > div > input {
        border-radius: 0.25rem;
        border: 1px solid #ccc;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #1f77b4;
        box-shadow: 0 0 0 0.2rem rgba(31, 119, 180, 0.25);
    }
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .main > div {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        div[data-testid="metric-container"] {
            margin-bottom: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def check_dependencies():
    """필수 의존성 확인"""
    
    required_packages = [
        'streamlit',
        'plotly', 
        'pandas',
        'numpy',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        st.error(f"❌ 누락된 패키지: {', '.join(missing_packages)}")
        st.info("다음 명령어로 설치하세요:")
        st.code(f"pip install {' '.join(missing_packages)}")
        st.stop()


if __name__ == "__main__":
    # 의존성 확인
    check_dependencies()
    
    # 세션 상태 초기화
    initialize_session_state()
    
    # 커스텀 CSS 적용
    setup_custom_css()
    
    # 에러 핸들링
    if handle_errors():
        # 메인 앱 실행
        main()
    
    # 세션 정보 로깅 (개발용)
    if st.sidebar.button("🔍 세션 정보 보기", help="개발자용: 세션 상태 확인"):
        with st.sidebar.expander("세션 상태"):
            st.json(dict(st.session_state)) 