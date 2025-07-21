# 📊 PatternLeader: 시장 심리 분석 서비스 설계

## 🏗️ 시스템 아키텍처 개요

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Frontend     │    │     Backend     │    │  Data Sources   │
│   (Streamlit)   │◄──►│    (FastAPI)    │◄──►│                 │
│                 │    │                 │    │  • yfinance     │
│  • 시각화       │    │  • REST API     │    │  • ccxt         │
│  • 사용자 입력  │    │  • 데이터 처리  │    │                 │
│  • 심리 해석    │    │  • 분석 엔진    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Storage       │
                       │                 │
                       │  • SQLite       │
                       │  • CSV Cache    │
                       └─────────────────┘
```

## 📁 프로젝트 구조

```
market-pattern-leader/
├── backend/
│   ├── src/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── endpoints/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── analysis.py
│   │   │       │   └── market.py
│   │   │       └── dependencies.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── logging.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── data_collector.py
│   │   │   ├── analysis_engine.py
│   │   │   └── psychology_analyzer.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── market_data.py
│   │   │   └── analysis_result.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── helpers.py
│   ├── tests/
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── distribution_chart.py
│   │   │   ├── psychology_gauge.py
│   │   │   └── market_selector.py
│   │   ├── pages/
│   │   │   ├── __init__.py
│   │   │   ├── main_dashboard.py
│   │   │   └── analysis_detail.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── api_client.py
│   │       └── visualizations.py
│   ├── requirements.txt
│   └── app.py
├── data/
│   ├── cache/
│   └── db/
├── docs/
├── requirements.txt
└── README.md
```

## 🔄 데이터 수집 및 처리 모듈

### 📊 Data Collector Service (`data_collector.py`)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import yfinance as yf
import ccxt
import pandas as pd

@dataclass
class MarketData:
    symbol: str
    market_type: str  # 'stock' or 'crypto'
    price_data: pd.DataFrame
    volume_data: pd.Series
    timestamp: datetime

class DataCollectorInterface(ABC):
    @abstractmethod
    def collect_data(self, symbol: str, period: str) -> MarketData:
        pass

class StockDataCollector(DataCollectorInterface):
    """Yahoo Finance를 통한 주식 데이터 수집"""
    
    def collect_data(self, symbol: str, period: str = "3mo") -> MarketData:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        
        return MarketData(
            symbol=symbol,
            market_type="stock",
            price_data=data[['Open', 'High', 'Low', 'Close']],
            volume_data=data['Volume'],
            timestamp=datetime.now()
        )

class CryptoDataCollector(DataCollectorInterface):
    """CCXT를 통한 암호화폐 데이터 수집"""
    
    def __init__(self, exchange_name: str = 'binance'):
        self.exchange = getattr(ccxt, exchange_name)()
    
    def collect_data(self, symbol: str, period: str = "1d") -> MarketData:
        # CCXT 구현 로직
        pass
```

### 📈 데이터 처리 파이프라인

```
Raw Data → Validation → Cleaning → Feature Engineering → KDE Analysis
    ↓           ↓           ↓            ↓               ↓
  API 응답    이상치 탐지   결측치 처리   수익률 계산    분포 추정
```

## 🧠 분석 엔진 및 심리 분석 로직

### 📊 KDE 기반 분포 분석 (`psychology_analyzer.py`)

```python
from dataclasses import dataclass
from typing import Tuple, Dict
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import gaussian_kde
from sklearn.preprocessing import StandardScaler

@dataclass
class PsychologyResult:
    """심리 분석 결과"""
    symbol: str
    current_price: float
    distribution_stats: Dict
    psychology_ratios: Dict  # {'buyers': 0.65, 'holders': 0.25, 'sellers': 0.10}
    sentiment_score: float  # -1 (극도공포) ~ 1 (극도탐욕)
    risk_level: str  # 'low', 'medium', 'high', 'extreme'
    interpretation: str

class PsychologyAnalyzer:
    """시장 심리 분석 엔진"""
    
    def __init__(self):
        self.scaler = StandardScaler()
    
    def analyze_psychology(self, market_data: MarketData) -> PsychologyResult:
        """주요 분석 흐름"""
        # 1. 수익률 계산
        returns = self._calculate_returns(market_data.price_data)
        
        # 2. KDE 분포 추정
        kde_dist = self._estimate_kde_distribution(returns)
        
        # 3. 현재 위치 기반 심리 상태 계산
        current_position = self._get_current_position(market_data)
        psychology_ratios = self._calculate_psychology_ratios(kde_dist, current_position)
        
        # 4. 감정 지수 및 리스크 레벨 계산
        sentiment_score = self._calculate_sentiment_score(psychology_ratios, kde_dist)
        risk_level = self._assess_risk_level(sentiment_score, psychology_ratios)
        
        # 5. 해석 생성
        interpretation = self._generate_interpretation(psychology_ratios, sentiment_score, risk_level)
        
        return PsychologyResult(
            symbol=market_data.symbol,
            current_price=market_data.price_data['Close'].iloc[-1],
            distribution_stats=self._get_distribution_stats(kde_dist, returns),
            psychology_ratios=psychology_ratios,
            sentiment_score=sentiment_score,
            risk_level=risk_level,
            interpretation=interpretation
        )
    
    def _calculate_returns(self, price_data: pd.DataFrame) -> np.ndarray:
        """수익률 계산 (로그 수익률 사용)"""
        close_prices = price_data['Close']
        returns = np.log(close_prices / close_prices.shift(1)).dropna()
        return returns.values
    
    def _estimate_kde_distribution(self, returns: np.ndarray) -> gaussian_kde:
        """KDE를 통한 분포 추정"""
        # 이상치 제거 (±3σ 범위)
        mean, std = np.mean(returns), np.std(returns)
        filtered_returns = returns[np.abs(returns - mean) <= 3 * std]
        
        # KDE 추정
        kde = gaussian_kde(filtered_returns)
        kde.set_bandwidth(kde.factor * 0.8)  # 대역폭 조정
        
        return kde
    
    def _calculate_psychology_ratios(self, kde_dist: gaussian_kde, current_position: float) -> Dict[str, float]:
        """현재 위치 기반 매수/관망/매도 비율 계산"""
        
        # 분포의 표준편차 추정
        x_range = np.linspace(-0.1, 0.1, 1000)
        densities = kde_dist(x_range)
        peak_idx = np.argmax(densities)
        peak_position = x_range[peak_idx]
        
        # 현재 위치가 분포의 어느 구간에 있는지 계산
        position_percentile = self._calculate_percentile(kde_dist, current_position)
        
        # 심리 비율 계산 (정규분포 가정)
        if position_percentile < 0.16:  # -1σ 이하 (과매도)
            buyers = 0.70 + (0.16 - position_percentile) * 0.5
            sellers = 0.10
            holders = 1.0 - buyers - sellers
        elif position_percentile > 0.84:  # +1σ 이상 (과매수)
            sellers = 0.60 + (position_percentile - 0.84) * 0.8
            buyers = 0.15
            holders = 1.0 - buyers - sellers
        else:  # 정상 범위
            buyers = 0.40 + (0.5 - position_percentile) * 0.6
            sellers = 0.20 + (position_percentile - 0.5) * 0.6
            holders = 1.0 - buyers - sellers
        
        return {
            'buyers': max(0, min(0.9, buyers)),
            'holders': max(0, min(0.8, holders)), 
            'sellers': max(0, min(0.9, sellers))
        }
    
    def _calculate_sentiment_score(self, psychology_ratios: Dict, kde_dist: gaussian_kde) -> float:
        """감정 지수 계산 (-1: 극도공포, 1: 극도탐욕)"""
        buyers_ratio = psychology_ratios['buyers']
        sellers_ratio = psychology_ratios['sellers']
        
        # 기본 감정 점수
        base_sentiment = (buyers_ratio - sellers_ratio) * 2 - 0.1
        
        # 분포의 분산도를 고려한 조정
        x_range = np.linspace(-0.05, 0.05, 500)
        variance = np.var(kde_dist(x_range))
        volatility_adjustment = min(0.3, variance * 100)
        
        sentiment = base_sentiment + volatility_adjustment if base_sentiment > 0 else base_sentiment - volatility_adjustment
        
        return max(-1.0, min(1.0, sentiment))
```

### 🎯 핵심 분석 알고리즘

```
입력: 가격 데이터 (OHLCV)
   ↓
1. 수익률 계산 (log returns)
   ↓
2. KDE 분포 추정 + 이상치 제거
   ↓  
3. 현재 위치 백분위 계산
   ↓
4. 정규분포 기반 심리 비율 계산:
   - 과매도구간 (-1σ): 매수자 ↑
   - 정상구간: 균형
   - 과매수구간 (+1σ): 매도자 ↑
   ↓
5. 감정지수 = (매수비율 - 매도비율) × 2 + 변동성조정
   ↓
출력: 심리분석 결과
```

## 🔌 FastAPI 백엔드 구조 및 API 엔드포인트

### 🎯 주요 엔드포인트 설계

```python
# backend/src/api/v1/endpoints/analysis.py

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ...models.analysis_result import AnalysisResponse
from ...services.analysis_engine import AnalysisEngine

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.get("/psychology/{symbol}", response_model=AnalysisResponse)
async def analyze_market_psychology(
    symbol: str,
    market_type: str = Query(..., regex="^(stock|crypto)$"),
    period: str = Query("3mo", regex="^(1mo|3mo|6mo|1y)$"),
    exchange: Optional[str] = Query(None)
):
    """
    시장 심리 분석 API
    
    Args:
        symbol: 종목 코드 (예: AAPL, BTC/USDT)
        market_type: 시장 타입 (stock, crypto)
        period: 분석 기간 (1mo, 3mo, 6mo, 1y)
        exchange: 거래소 (암호화폐만 해당)
    
    Returns:
        심리 분석 결과 및 시각화 데이터
    """
    try:
        analysis_engine = AnalysisEngine()
        result = await analysis_engine.analyze(
            symbol=symbol,
            market_type=market_type,
            period=period,
            exchange=exchange
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/distribution/{symbol}")
async def get_distribution_data(
    symbol: str,
    market_type: str = Query(...),
    period: str = Query("3mo")
):
    """분포 곡선 시각화용 원시 데이터 제공"""
    pass

@router.get("/historical/{symbol}")
async def get_historical_psychology(
    symbol: str,
    market_type: str = Query(...),
    days: int = Query(30, ge=7, le=365)
):
    """과거 심리 변화 추이 데이터"""
    pass
```

### 📋 API 응답 모델

```python
# backend/src/models/analysis_result.py

from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class PsychologyRatios(BaseModel):
    buyers: float
    holders: float  
    sellers: float

class DistributionStats(BaseModel):
    mean: float
    std: float
    skewness: float
    kurtosis: float
    peak_position: float

class VisualizationData(BaseModel):
    """시각화를 위한 데이터"""
    x_values: List[float]
    y_values: List[float]
    current_position: float
    zones: Dict[str, Dict]  # {'oversold': {'start': -0.02, 'end': -0.01}}

class AnalysisResponse(BaseModel):
    symbol: str
    current_price: float
    analysis_timestamp: datetime
    psychology_ratios: PsychologyRatios
    sentiment_score: float
    risk_level: str
    interpretation: str
    distribution_stats: DistributionStats
    visualization_data: VisualizationData
    confidence_score: float

class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: datetime
```

### 🛠️ 백엔드 서비스 레이어

```python
# backend/src/services/analysis_engine.py

class AnalysisEngine:
    """분석 엔진 오케스트레이터"""
    
    def __init__(self):
        self.data_collector = DataCollectorFactory()
        self.psychology_analyzer = PsychologyAnalyzer()
        self.cache_manager = CacheManager()
    
    async def analyze(self, symbol: str, market_type: str, period: str, exchange: Optional[str] = None) -> AnalysisResponse:
        """전체 분석 프로세스 실행"""
        
        # 1. 캐시 확인
        cache_key = f"{symbol}_{market_type}_{period}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result and not self._is_cache_expired(cached_result):
            return cached_result
        
        # 2. 데이터 수집
        collector = self.data_collector.get_collector(market_type)
        market_data = await collector.collect_data(symbol, period)
        
        # 3. 심리 분석
        psychology_result = self.psychology_analyzer.analyze_psychology(market_data)
        
        # 4. 시각화 데이터 생성
        viz_data = self._prepare_visualization_data(psychology_result, market_data)
        
        # 5. 응답 객체 생성
        response = self._build_response(psychology_result, viz_data)
        
        # 6. 캐시 저장 (15분)
        await self.cache_manager.set(cache_key, response, ttl=900)
        
        return response
```

## 🎨 프론트엔드 시각화 구조 (Streamlit)

### 📊 메인 대시보드 구성

```python
# frontend/src/pages/main_dashboard.py

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from ..utils.api_client import PatternLeaderAPI
from ..components.distribution_chart import create_distribution_chart
from ..components.psychology_gauge import create_psychology_gauge

def render_main_dashboard():
    """메인 대시보드 렌더링"""
    
    st.title("📊 PatternLeader - 시장 심리 분석")
    
    # 사이드바: 입력 컨트롤
    with st.sidebar:
        st.header("⚙️ 분석 설정")
        
        market_type = st.selectbox(
            "시장 타입",
            ["stock", "crypto"],
            format_func=lambda x: "주식" if x == "stock" else "암호화폐"
        )
        
        symbol = st.text_input(
            "종목 코드",
            value="AAPL" if market_type == "stock" else "BTC/USDT",
            help="주식: AAPL, TSLA 등 | 암호화폐: BTC/USDT, ETH/USDT 등"
        )
        
        period = st.selectbox(
            "분석 기간",
            ["1mo", "3mo", "6mo", "1y"],
            index=1,
            format_func=lambda x: {"1mo": "1개월", "3mo": "3개월", "6mo": "6개월", "1y": "1년"}[x]
        )
        
        analyze_button = st.button("🔍 분석 시작", type="primary")
    
    # 메인 영역: 분석 결과 표시
    if analyze_button:
        with st.spinner("데이터 수집 및 분석 중..."):
            try:
                api = PatternLeaderAPI()
                result = api.get_analysis(symbol, market_type, period)
                
                # 결과 표시
                _display_analysis_results(result)
                
            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다: {str(e)}")

def _display_analysis_results(result):
    """분석 결과 표시"""
    
    # 1. 요약 카드
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "현재 가격",
            f"${result.current_price:,.2f}",
            delta=None
        )
    
    with col2:
        sentiment_emoji = "😱" if result.sentiment_score < -0.5 else "😰" if result.sentiment_score < 0 else "😐" if result.sentiment_score < 0.5 else "🤑"
        st.metric(
            "감정 지수",
            f"{result.sentiment_score:.2f}",
            delta=sentiment_emoji
        )
    
    with col3:
        risk_color = {"low": "🟢", "medium": "🟡", "high": "🟠", "extreme": "🔴"}
        st.metric(
            "리스크 레벨",
            result.risk_level.upper(),
            delta=risk_color.get(result.risk_level, "⚪")
        )
    
    with col4:
        st.metric(
            "신뢰도",
            f"{result.confidence_score:.1%}",
            delta=None
        )
    
    # 2. 심리 분포 차트
    st.subheader("🧠 시장 참여자 심리 분포")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 분포 곡선 차트
        distribution_fig = create_distribution_chart(result.visualization_data, result.distribution_stats)
        st.plotly_chart(distribution_fig, use_container_width=True)
    
    with col2:
        # 심리 비율 게이지
        psychology_fig = create_psychology_gauge(result.psychology_ratios)
        st.plotly_chart(psychology_fig, use_container_width=True)
    
    # 3. 해석 및 권고
    st.subheader("📝 심리 분석 해석")
    
    # 해석 텍스트를 구조화된 형태로 표시
    interpretation_container = st.container()
    with interpretation_container:
        st.info(result.interpretation)
        
        # 추가 인사이트
        _display_psychology_insights(result.psychology_ratios, result.risk_level)

def _display_psychology_insights(ratios, risk_level):
    """추가 심리 인사이트 표시"""
    
    st.subheader("💡 주요 인사이트")
    
    # 매수자 비율이 높은 경우
    if ratios.buyers > 0.6:
        st.warning("⚠️ 매수 심리가 과도하게 높습니다. 추격매수 리스크를 고려하세요.")
    
    # 매도자 비율이 높은 경우
    if ratios.sellers > 0.5:
        st.success("✅ 매도 압력이 높아 반등 기회를 노려볼 수 있습니다.")
    
    # 관망자 비율이 높은 경우
    if ratios.holders > 0.5:
        st.info("🤔 관망세가 강합니다. 방향성 결정을 기다리는 상황입니다.")
```

### 📈 시각화 컴포넌트

```python
# frontend/src/components/distribution_chart.py

import plotly.graph_objects as go
import numpy as np

def create_distribution_chart(viz_data, distribution_stats):
    """KDE 분포 곡선 차트 생성"""
    
    fig = go.Figure()
    
    # 분포 곡선
    fig.add_trace(go.Scatter(
        x=viz_data.x_values,
        y=viz_data.y_values,
        mode='lines',
        name='심리 분포',
        line=dict(color='blue', width=3),
        fill='tonexty'
    ))
    
    # 현재 위치 표시
    current_y = np.interp(viz_data.current_position, viz_data.x_values, viz_data.y_values)
    fig.add_trace(go.Scatter(
        x=[viz_data.current_position],
        y=[current_y],
        mode='markers',
        name='현재 위치',
        marker=dict(color='red', size=15, symbol='diamond')
    ))
    
    # 과매수/과매도 구간 표시
    if 'oversold' in viz_data.zones:
        fig.add_vrect(
            x0=viz_data.zones['oversold']['start'],
            x1=viz_data.zones['oversold']['end'],
            fillcolor="green",
            opacity=0.2,
            annotation_text="과매도"
        )
    
    if 'overbought' in viz_data.zones:
        fig.add_vrect(
            x0=viz_data.zones['overbought']['start'],
            x1=viz_data.zones['overbought']['end'],
            fillcolor="red",
            opacity=0.2,
            annotation_text="과매수"
        )
    
    fig.update_layout(
        title="수익률 분포 및 현재 시장 위치",
        xaxis_title="수익률 (%)",
        yaxis_title="확률 밀도",
        showlegend=True,
        height=400
    )
    
    return fig
```

## 🚀 개발 단계별 구현 로드맵

### 📅 Phase 1: 기반 구조 구축 (Week 1-2)

**🎯 목표**: 프로젝트 초기 설정 및 핵심 데이터 파이프라인 구축

**주요 작업**:
```
┌─ Day 1-2: 프로젝트 초기 설정
│  ├── 디렉토리 구조 생성
│  ├── requirements.txt 작성
│  ├── Git 저장소 설정
│  └── 개발 환경 구성
│
├─ Day 3-5: 데이터 수집 모듈 구현
│  ├── yfinance 연동 (주식 데이터)
│  ├── ccxt 연동 (암호화폐 데이터)
│  ├── 데이터 검증 로직
│  └── 기본 테스트 작성
│
├─ Day 6-8: 기본 분석 엔진 구현
│  ├── 수익률 계산 함수
│  ├── KDE 분포 추정 로직
│  ├── 기본 통계 계산
│  └── 단위 테스트 작성
│
└─ Day 9-10: FastAPI 기본 구조
   ├── API 서버 초기 설정
   ├── 기본 엔드포인트 생성
   ├── 모델 스키마 정의
   └── CORS 설정
```

**완료 기준**:
- [ ] 주식/암호화폐 데이터 수집 성공
- [ ] 기본 KDE 분포 계산 정상 동작
- [ ] API 서버 정상 구동 및 응답

### 📅 Phase 2: 핵심 분석 로직 구현 (Week 3-4)

**🎯 목표**: 심리 분석 알고리즘 완성 및 API 통합

**주요 작업**:
```
┌─ Day 11-13: 심리 분석 알고리즘 구현
│  ├── 백분위 기반 심리 비율 계산
│  ├── 감정 지수 알고리즘
│  ├── 리스크 레벨 판정 로직
│  └── 해석 문구 생성 엔진
│
├─ Day 14-16: API 통합 및 최적화
│  ├── 분석 엔진과 API 연동
│  ├── 캐시 시스템 구현
│  ├── 에러 핸들링 강화
│  └── API 응답 최적화
│
├─ Day 17-18: 시각화 데이터 준비
│  ├── 분포 곡선 데이터 생성
│  ├── 구간별 색상 매핑
│  ├── 차트용 좌표 계산
│  └── 성능 최적화
│
└─ Day 19-20: 통합 테스트
   ├── 전체 파이프라인 테스트
   ├── 다양한 종목 검증
   ├── 성능 벤치마크
   └── 버그 수정
```

**완료 기준**:
- [ ] 심리 비율 계산 정확도 >90%
- [ ] API 응답 시간 <3초
- [ ] 10개 이상 종목 정상 분석

### 📅 Phase 3: 프론트엔드 구현 (Week 5-6)

**🎯 목표**: 사용자 친화적 대시보드 완성

**주요 작업**:
```
┌─ Day 21-23: Streamlit 기본 구조
│  ├── 페이지 레이아웃 설계
│  ├── 사이드바 입력 컨트롤
│  ├── API 클라이언트 구현
│  └── 기본 UI 컴포넌트
│
├─ Day 24-26: 시각화 구현
│  ├── Plotly 분포 곡선 차트
│  ├── 심리 비율 게이지 차트
│  ├── 인터랙티브 요소 추가
│  └── 반응형 디자인
│
├─ Day 27-28: UX 개선
│  ├── 로딩 상태 표시
│  ├── 에러 메시지 개선
│  ├── 도움말 및 가이드
│  └── 접근성 개선
│
└─ Day 29-30: 통합 및 최적화
   ├── 백엔드-프론트엔드 통합
   ├── 사용자 경험 테스트
   ├── 성능 최적화
   └── 배포 준비
```

**완료 기준**:
- [ ] 직관적인 사용자 인터페이스
- [ ] 분포 곡선 실시간 시각화
- [ ] 심리 해석 텍스트 자동 생성

### 📅 Phase 4: 고도화 및 배포 (Week 7-8)

**🎯 목표**: 프로덕션 준비 및 추가 기능 구현

**주요 작업**:
```
┌─ Day 31-33: 고급 기능 추가
│  ├── 과거 심리 변화 추이
│  ├── 다중 종목 비교 기능
│  ├── 알림 및 관심 종목
│  └── 데이터 내보내기
│
├─ Day 34-35: 성능 최적화
│  ├── 데이터베이스 인덱싱
│  ├── 캐시 전략 개선
│  ├── API 응답 압축
│  └── 메모리 사용량 최적화
│
├─ Day 36-37: 배포 환경 구성
│  ├── Docker 컨테이너화
│  ├── CI/CD 파이프라인
│  ├── 모니터링 설정
│  └── 보안 강화
│
└─ Day 38-40: 최종 테스트 및 배포
   ├── 프로덕션 환경 테스트
   ├── 사용자 수용 테스트
   ├── 문서화 완료
   └── 정식 배포
```

**완료 기준**:
- [ ] 프로덕션 환경 안정 운영
- [ ] 사용자 피드백 수집 시스템
- [ ] 확장 가능한 아키텍처

### 🔧 기술적 고려사항

**📊 성능 최적화**:
- 데이터 캐싱: Redis (15분 TTL)
- API 응답 압축: gzip
- 프론트엔드 최적화: lazy loading

**🔒 보안 고려사항**:
- API 속도 제한: 분당 100회
- 입력 데이터 검증 및 살균
- HTTPS 강제 적용

**📈 확장성 고려사항**:
- 마이크로서비스 아키텍처 준비
- 데이터베이스 샤딩 가능한 구조
- 로드밸런싱 준비

## 🎯 핵심 설계 요약

### 💡 주요 혁신점

**1. 통계적 심리 분석**
- KDE 기반 정규분포 추정으로 객관적 심리 상태 수치화
- 현재 위치의 백분위를 통한 매수/매도/관망 비율 계산
- 분산도 고려한 감정 지수 보정 알고리즘

**2. 직관적 시각화**
- 분포 곡선 + 현재 위치 표시로 한눈에 파악 가능
- 과매수/과매도 구간 색상 구분
- 실시간 심리 비율 게이지 차트

**3. 확장 가능한 아키텍처**
- 모듈화된 데이터 수집기 (주식/암호화폐 독립)
- 플러그인 형태의 분석 엔진
- RESTful API를 통한 프론트엔드 분리

### 🔑 차별화 포인트

1. **기술적 차별화**: 무료 API만으로 고도화된 심리 분석 제공
2. **사용자 경험**: 복잡한 차트 분석 없이도 심리 상태 파악 가능
3. **확장성**: 다양한 시장과 지표 추가 가능한 유연한 구조
4. **실용성**: 투자 의사결정에 직접 활용 가능한 정량적 지표

### ⚠️ 구현 시 주의사항

**데이터 품질 관리**:
- API 응답 지연/실패에 대한 견고한 에러 처리
- 이상치 데이터 필터링 및 검증 로직 필수
- 시장 휴일/거래 중단 상황 고려

**성능 최적화**:
- 실시간 분석보다는 캐싱 전략 활용
- KDE 계산 최적화 (적절한 대역폭 설정)
- 프론트엔드 렌더링 성능 고려

**사용자 경험**:
- 분석 결과에 대한 명확한 면책 조항
- 심리 해석의 한계점 명시
- 투자 권유가 아닌 참고 자료임을 강조

이 설계를 바탕으로 단계적 구현을 진행하면, 사용자가 시장 심리를 직관적으로 파악하고 투자 타이밍 판단에 활용할 수 있는 강력한 도구를 만들 수 있을 것입니다.