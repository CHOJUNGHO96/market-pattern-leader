# 📊 PatternLeader 백엔드

**설계 문서 기반 시장 심리 분석 FastAPI 백엔드**

## 🎯 주요 기능

### 🧠 KDE 기반 심리 분석
- **정규분포 추정**: 가격 변화율의 확률 밀도 함수 계산
- **매수/매도/관망 비율**: 현재 위치 기반 투자자 심리 추정  
- **감정 지수**: -1(극도공포) ~ 1(극도탐욕) 범위의 시장 감정 수치화
- **리스크 레벨**: low, medium, high, extreme 4단계 리스크 평가

### 📈 데이터 수집
- **주식**: Yahoo Finance API를 통한 실시간 주식 데이터
- **암호화폐**: CCXT(Binance)를 통한 암호화폐 데이터
- **다중 기간**: 1개월, 3개월, 6개월, 1년 분석 지원

### ⚡ 성능 최적화
- **인메모리 캐시**: 15분 TTL로 분석 결과 캐싱
- **비동기 처리**: 전체 파이프라인 비동기 최적화
- **요청 제한**: IP별 분당 100회 요청 제한

## 🚀 빠른 시작

### 1. 설치
```bash
cd backend
pip install -r requirements.txt
```

### 2. 실행
```bash
python main.py
```

### 3. API 문서 확인
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📡 주요 API 엔드포인트

### 심리 분석
```bash
# 전체 심리 분석
POST /api/v1/analysis/psychology/{symbol}
  - market_type: stock|crypto
  - period: 1mo|3mo|6mo|1y

# 빠른 분석
GET /api/v1/analysis/quick/{symbol}

# 분포 데이터
GET /api/v1/analysis/distribution/{symbol}
```

### 시장 정보
```bash
# 지원 심볼 목록
GET /api/v1/analysis/symbols

# 시장 타입 정보  
GET /api/v1/market/types

# 헬스체크
GET /api/v1/analysis/health
```

## 🏗️ 아키텍처

### 설계 문서 준수 구조
```
src/
├── api/v1/endpoints/        # API 엔드포인트
│   ├── analysis.py         # 심리 분석 API
│   └── market.py           # 시장 정보 API
├── services/               # 비즈니스 로직
│   ├── data_collector.py   # 데이터 수집기
│   ├── psychology_analyzer.py # 심리 분석 엔진
│   └── analysis_engine.py  # 분석 오케스트레이터
├── models/                 # 데이터 모델
│   ├── market_data.py      # 시장 데이터 모델
│   └── analysis_result.py  # 분석 결과 모델
├── core/                   # 핵심 설정
│   ├── config.py          # 설정 관리
│   └── logging.py         # 로깅 설정
└── utils/                  # 유틸리티
    └── cache_manager.py    # 캐시 관리
```

### 핵심 클래스

#### DataCollectorInterface
```python
# 주식/암호화폐 데이터 수집 추상화
- StockDataCollector (yfinance)
- CryptoDataCollector (ccxt)
```

#### PsychologyAnalyzer
```python
# KDE 기반 심리 분석 엔진
- 수익률 계산 및 분포 추정
- 현재 위치 기반 심리 비율 계산
- 감정 지수 및 리스크 레벨 평가
```

#### AnalysisEngine  
```python
# 전체 분석 프로세스 오케스트레이션
- 캐시 관리 및 데이터 수집 조율
- 심리 분석 실행 및 응답 생성
```

## 🧪 테스트

```bash
# 전체 테스트 실행
pytest

# 특정 모듈 테스트
pytest tests/test_psychology_analyzer.py

# 커버리지 포함
pytest --cov=src
```

## ⚙️ 설정

### 환경 변수
```bash
# .env 파일 생성
PROJECT_NAME="PatternLeader"
DEBUG=true
LOG_LEVEL=INFO
DATA_CACHE_TTL=900
RATE_LIMIT=100
```

### 캐시 설정
- **타입**: 메모리 캐시 (Redis 준비됨)
- **TTL**: 900초 (15분)
- **용량**: 무제한 (메모리 기반)

## 📊 사용 예제

### Python 클라이언트
```python
import httpx

async with httpx.AsyncClient() as client:
    # BTC 심리 분석
    response = await client.get(
        "http://localhost:8000/api/v1/analysis/quick/BTC/USDT",
        params={"market_type": "crypto", "period": "3mo"}
    )
    
    result = response.json()
    print(f"매수자: {result['psychology_ratios']['buyers']:.1%}")
    print(f"감정 지수: {result['sentiment_score']:.2f}")
    print(f"리스크: {result['risk_level']}")
```

### cURL
```bash
# 애플 주식 분석
curl "http://localhost:8000/api/v1/analysis/psychology/AAPL" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"market_type": "stock", "period": "3mo"}'
```

## 🔧 개발

### 코드 스타일
- **Python 3.9+** 호환
- **타입 힌트** 필수
- **한글 주석** 및 docstring  
- **PEP8** 준수

### 포맷팅
```bash
black src/
ruff src/ --fix
```

## 🚨 주의사항

1. **외부 API 의존**: yfinance, CCXT 서비스 상태에 따라 영향
2. **레이트 리밋**: 과도한 요청 시 일시적 차단
3. **투자 조언 아님**: 분석 결과는 참고용이며 투자 조언이 아님
4. **데이터 지연**: 실시간이 아닌 최근 데이터 기반 분석

## 📈 성능

- **응답 시간**: 평균 2-3초 (첫 요청), 캐시 시 <100ms
- **처리량**: 분당 ~100 요청 (레이트 리밋 기준)
- **메모리**: 기본 ~50MB, 캐시 증가 시 추가

## 🔗 관련 링크

- [설계 문서](../PatternLeader_Design_Document.md)
- [프론트엔드](../frontend/)
- [API 문서](http://localhost:8000/docs) (서버 실행 시)