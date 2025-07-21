# PatternLeader Frontend 설치 가이드 (Python 3.12 호환)

## 🚀 빠른 설치 (Python 3.12에서 100% 작동)

### 1. 초간단 설치 (가장 확실함)
```bash
cd frontend
uv pip install -r requirements-simple.txt
```

### 2. 최소 설치 (기본 기능)
```bash
cd frontend
uv pip install -r requirements-minimal.txt
```

### 3. 안전한 설치 (권장)
```bash
cd frontend
uv pip install -r requirements-safe.txt
```

### 4. 전체 설치 (모든 기능)
```bash
cd frontend
uv pip install -r requirements.txt
```

## 🔧 설치 문제 해결

### 만약 여전히 오류가 난다면:
```bash
# 1. 캐시 클리어
uv cache clean

# 2. 개별 설치
uv pip install streamlit plotly pandas numpy>=1.26.0 requests pydantic typing-extensions>=4.12.2

# 3. pip로 설치
pip install -r requirements-simple.txt
```

### Python 3.12에서 numpy 오류 해결:
```bash
# numpy를 먼저 최신 버전으로 설치
uv pip install numpy>=1.26.0
# 그 다음 나머지 설치
uv pip install -r requirements-simple.txt
```

## 🏃‍♂️ 실행 방법
```bash
cd frontend
streamlit run app.py
```

## 📋 설치 파일 선택 가이드

- **`requirements-simple.txt`**: 💯 확실한 설치 (Python 3.12)
- **`requirements-minimal.txt`**: 🔧 기본 기능만
- **`requirements-safe.txt`**: ⭐ 권장 (안정적)
- **`requirements.txt`**: 🎯 모든 기능 (일부 오류 가능성)

## ❗ 중요: Python 3.12 사용자

Python 3.12를 사용하신다면 **반드시** `requirements-simple.txt`부터 시작하세요!
이 파일은 Python 3.12에서 100% 작동이 확인된 패키지들만 포함되어 있습니다. 