# 🚀 PatternLeader 설치 가이드

## 📋 시스템 요구사항

- **Python**: 3.9 이상
- **메모리**: 최소 4GB RAM (권장 8GB)
- **디스크**: 최소 1GB 여유 공간
- **인터넷**: 시장 데이터 수집을 위한 안정적인 연결

## 🔧 설치 방법

### 1️⃣ 전체 설치 (개발 환경)

```bash
# 저장소 클론
git clone <repository-url>
cd market-pattern-leader

# Python 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows

# 백엔드 설치
cd backend
pip install -r requirements.txt

# 프론트엔드 설치
cd ../frontend
pip install -r requirements.txt
```

### 2️⃣ 최소 설치 (운영 환경)

```bash
# 백엔드만 설치 (API 서버)
cd backend
pip install -r requirements-minimal.txt

# 프론트엔드만 설치 (대시보드)
cd frontend  
pip install -r requirements-minimal.txt
```

### 3️⃣ Docker 설치 (선택사항)

```bash
# Docker Compose로 전체 실행
docker-compose up -d

# 개별 서비스 실행
docker-compose up backend   # 백엔드만
docker-compose up frontend  # 프론트엔드만
```

## 🏃‍♂️ 실행 방법

### 백엔드 실행 (API 서버)

```bash
cd backend
python main.py

# 또는 uvicorn으로 직접 실행
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**접속**: http://localhost:8000
**API 문서**: http://localhost:8000/docs

### 프론트엔드 실행 (대시보드)

```bash
cd frontend
streamlit run app.py

# 또는 포트 지정
streamlit run app.py --server.port 8501
```

**접속**: http://localhost:8501

## 📦 라이브러리 상세 설명

### 백엔드 Dependencies

#### 🔧 Core Framework
- **fastapi**: 고성능 웹 API 프레임워크
- **uvicorn**: ASGI 서버
- **pydantic**: 데이터 검증 및 타입 안전성

#### 📊 Data Collection
- **yfinance**: Yahoo Finance API 클라이언트 (주식 데이터)
- **ccxt**: 암호화폐 거래소 통합 라이브러리

#### 🧮 Data Analysis
- **numpy**: 수치 계산 라이브러리
- **pandas**: 데이터 조작 및 분석
- **scipy**: 과학 계산 (KDE 분포 추정)
- **scikit-learn**: 머신러닝 (전처리)

#### ⚡ Performance
- **httpx**: 비동기 HTTP 클라이언트
- **aiohttp**: 비동기 웹 클라이언트
- **redis**: 캐시 시스템 (선택사항)

#### 🛠️ Development
- **pytest**: 테스트 프레임워크
- **black**: 코드 포맷터
- **ruff**: 빠른 린터

### 프론트엔드 Dependencies

#### 🎨 UI Framework
- **streamlit**: 웹 애플리케이션 프레임워크
- **plotly**: 인터랙티브 차트 라이브러리

#### 🎯 Enhanced Components
- **streamlit-option-menu**: 향상된 네비게이션
- **streamlit-aggrid**: 고급 데이터 테이블
- **streamlit-plotly-events**: 차트 상호작용
- **streamlit-extras**: 추가 UI 컴포넌트

#### 📈 Additional Visualization
- **matplotlib**: 기본 차트 라이브러리
- **seaborn**: 통계 시각화
- **bokeh**: 인터랙티브 웹 차트
- **altair**: 선언적 시각화

## 🚨 설치 문제 해결

### 일반적인 문제

#### 1. yfinance 설치 오류
```bash
# SSL 인증서 문제
pip install --trusted-host pypi.org --trusted-host pypi.python.org yfinance

# 또는 최신 버전으로 업그레이드
pip install --upgrade yfinance
```

#### 2. CCXT 설치 오류
```bash
# Visual Studio Build Tools 필요 (Windows)
# https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio

# 또는 미리 컴파일된 휠 사용
pip install --only-binary=all ccxt
```

#### 3. Streamlit 포트 충돌
```bash
# 다른 포트로 실행
streamlit run app.py --server.port 8502
```

#### 4. 메모리 부족
```bash
# 환경변수 설정으로 메모리 사용량 제한
export MALLOC_ARENA_MAX=2
export PYTHONHASHSEED=0
```

### 플랫폼별 설치 가이드

#### Windows
```bash
# Chocolatey로 Python 설치
choco install python

# 또는 Microsoft Store에서 Python 설치
# pip 업그레이드
python -m pip install --upgrade pip
```

#### macOS
```bash
# Homebrew로 Python 설치
brew install python

# Xcode Command Line Tools 설치
xcode-select --install
```

#### Ubuntu/Debian
```bash
# Python 및 개발 도구 설치
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-dev build-essential

# 시스템 라이브러리 설치
sudo apt install libssl-dev libffi-dev
```

## 🔍 설치 확인

### 백엔드 테스트
```bash
cd backend
python -c "import fastapi, yfinance, ccxt; print('백엔드 라이브러리 OK')"

# API 테스트
curl http://localhost:8000/health
```

### 프론트엔드 테스트
```bash
cd frontend
python -c "import streamlit, plotly; print('프론트엔드 라이브러리 OK')"

# Streamlit 테스트
streamlit hello
```

## 📚 추가 리소스

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Streamlit 공식 문서](https://docs.streamlit.io/)
- [yfinance 문서](https://pypi.org/project/yfinance/)
- [CCXT 문서](https://ccxt.readthedocs.io/)
- [Plotly 문서](https://plotly.com/python/)

## 💡 성능 최적화 팁

### 백엔드 최적화
```bash
# 프로덕션 환경에서 Gunicorn 사용
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Redis 캐시 활성화
pip install redis
export CACHE_TYPE=redis
export REDIS_HOST=localhost
```

### 프론트엔드 최적화
```bash
# Streamlit 캐시 설정
export STREAMLIT_CACHE_DIR=/tmp/streamlit_cache

# 메모리 사용량 모니터링
pip install memory-profiler
```

## 🛠️ 개발 환경 설정

### VSCode 설정
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black"
}
```

### Git Hooks 설정
```bash
# pre-commit 설치
pip install pre-commit
pre-commit install

# 코드 품질 검사 자동화
pre-commit run --all-files
```