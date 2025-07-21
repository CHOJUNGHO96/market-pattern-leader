# 📊 PatternLeader Frontend

PatternLeader의 Streamlit 기반 프론트엔드 애플리케이션입니다.

## 🎯 주요 기능

### 📈 KDE 분포 분석
- 과거 수익률 데이터의 확률 분포 추정
- 현재 위치의 통계적 의미 분석
- 과매수/과매도 구간 자동 탐지
- ±1σ, ±2σ 구간 시각화

### 🧠 심리 상태 분석
- 매수자/관망자/매도자 비율 계산
- 감정 지수를 통한 시장 심리 수치화
- 심리 비율 파이차트 및 게이지 차트
- 감정 온도계 시각화

### 📊 직관적 시각화
- 인터랙티브 Plotly 차트
- 반응형 대시보드 레이아웃
- 모바일 최적화 차트
- 실시간 데이터 업데이트

### ⚙️ 시장 선택 도구
- 주식 및 암호화폐 시장 지원
- 인기 종목 빠른 선택
- 다양한 분석 기간 설정
- 거래소별 데이터 지원

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
cd frontend
pip install -r requirements.txt
```

### 2. 백엔드 서버 실행 (선행 필요)

```bash
cd ../backend
python main.py
```

### 3. 프론트엔드 실행

```bash
cd frontend
streamlit run app.py
```

### 4. 브라우저에서 접속

```
http://localhost:8501
```

## 📁 프로젝트 구조

```
frontend/
├── app.py                          # 메인 애플리케이션 진입점
├── requirements.txt                # Python 의존성
├── README.md                       # 프로젝트 문서
└── src/                           # 소스 코드
    ├── components/                # UI 컴포넌트
    │   ├── __init__.py
    │   ├── distribution_chart.py   # KDE 분포 차트 컴포넌트
    │   ├── psychology_gauge.py     # 심리 게이지 컴포넌트
    │   └── market_selector.py      # 시장 선택 위젯
    ├── pages/                     # 페이지 모듈
    │   ├── __init__.py
    │   ├── main_dashboard.py       # 메인 대시보드
    │   └── analysis_detail.py      # 상세 분석 페이지
    └── utils/                     # 유틸리티
        ├── __init__.py
        ├── api_client.py           # API 클라이언트
        └── visualizations.py       # 시각화 헬퍼
```

## 🔧 주요 컴포넌트

### 📊 Distribution Chart (`components/distribution_chart.py`)
- `create_distribution_chart()`: KDE 분포 곡선 차트 생성
- `render_distribution_analysis()`: 분포 분석 결과 렌더링
- `get_distribution_insights()`: 분포 기반 인사이트 생성

### 🧠 Psychology Gauge (`components/psychology_gauge.py`)
- `create_psychology_gauge()`: 심리 비율 게이지 차트
- `create_psychology_pie_chart()`: 심리 구성 파이 차트
- `create_sentiment_thermometer()`: 감정 온도계 차트
- `render_psychology_dashboard()`: 심리 분석 대시보드

### ⚙️ Market Selector (`components/market_selector.py`)
- `MarketSelector`: 시장/종목 선택 위젯 클래스
- `render_market_status()`: 글로벌 시장 현황 표시
- 인기 종목 빠른 선택 기능
- 종목 코드 유효성 검사

### 🌐 API Client (`utils/api_client.py`)
- `APIClient`: FastAPI 백엔드 통신 클래스
- `get_analysis()`: 분석 결과 요청
- `check_server_health()`: 서버 상태 확인
- 에러 처리 및 재시도 로직

## 📱 사용자 인터페이스

### 메인 대시보드
- 시장/종목 선택 사이드바
- 실시간 분석 실행
- 요약 카드 및 주요 지표
- 분포 차트 및 심리 분석 차트
- 투자 가이드라인 제공

### 상세 분석 페이지
- 탭 기반 구성 (분포/심리/추이/고급)
- 상세 통계 정보
- 과거 데이터 추이
- 고급 분석 지표
- 시나리오 분석

## 🎨 스타일링

### 커스텀 CSS
- 반응형 디자인
- 다크/라이트 테마 지원
- 모바일 최적화
- 접근성 고려

### 색상 팔레트
- Primary: `#1f77b4` (파란색)
- Success: `#4caf50` (초록색)
- Warning: `#ffc107` (노란색)
- Error: `#dc3545` (빨간색)

## 🔧 설정

### 환경 변수
```bash
# .env 파일 (선택사항)
BACKEND_URL=http://localhost:8000
API_TIMEOUT=30
CACHE_TTL=300
```

### Streamlit 설정
```toml
# .streamlit/config.toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[server]
port = 8501
headless = false
```

## 🐛 디버깅

### 로그 확인
- Streamlit 콘솔 출력 확인
- 브라우저 개발자 도구 활용
- 네트워크 탭에서 API 요청 확인

### 일반적인 문제

**1. 백엔드 연결 실패**
```bash
# 백엔드 서버 상태 확인
curl http://localhost:8000/health
```

**2. 모듈 임포트 오류**
```bash
# 의존성 재설치
pip install -r requirements.txt --force-reinstall
```

**3. 차트 렌더링 문제**
```bash
# 브라우저 캐시 삭제
# Streamlit 캐시 클리어
streamlit cache clear
```

## 🚀 배포

### 로컬 배포
```bash
streamlit run app.py --server.port 8501
```

### Docker 배포
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

### 클라우드 배포
- Streamlit Cloud
- Heroku
- AWS ECS
- Google Cloud Run

## 📊 성능 최적화

### 캐싱 전략
- Streamlit 내장 캐시 활용
- API 응답 캐싱
- 차트 데이터 메모이제이션

### 로딩 최적화
- 지연 로딩 (Lazy Loading)
- 청크 단위 데이터 로드
- 프리로딩 전략

## 🧪 테스트

### 단위 테스트
```bash
pytest tests/
```

### E2E 테스트
```bash
# Selenium 기반 테스트
python tests/e2e_test.py
```

## 🤝 기여하기

1. Fork 프로젝트
2. Feature 브랜치 생성
3. 변경사항 커밋
4. Pull Request 제출

## 📄 라이선스

MIT License - 자세한 내용은 LICENSE 파일 참조

## 📞 지원

- GitHub Issues: 버그 리포트 및 기능 요청
- Documentation: 상세 사용법 가이드
- Community: 사용자 커뮤니티 지원

---

**개발팀:** PatternLeader Team  
**버전:** 1.0.0  
**업데이트:** 2024-01-01 