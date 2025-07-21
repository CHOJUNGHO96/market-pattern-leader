"""
PatternLeader Market Selector Component

시장/종목 선택 위젯 컴포넌트
"""

import streamlit as st
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MarketSelection:
    """시장 선택 데이터 클래스"""
    market_type: str
    symbol: str
    period: str
    exchange: Optional[str] = None


class MarketSelector:
    """시장/종목 선택 위젯"""
    
    def __init__(self):
        """초기화"""
        self.popular_stocks = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", 
            "META", "NVDA", "NFLX", "SPY", "QQQ"
        ]
        
        self.popular_crypto = [
            "BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT", "XRP/USDT",
            "SOL/USDT", "DOGE/USDT", "AVAX/USDT", "DOT/USDT", "MATIC/USDT"
        ]
        
        self.crypto_exchanges = [
            "binance", "coinbase", "kraken", "bitfinex", "huobi"
        ]
        
        self.periods = {
            "1mo": "1개월",
            "3mo": "3개월", 
            "6mo": "6개월",
            "1y": "1년"
        }
    
    def render_selector(self) -> MarketSelection:
        """
        시장 선택 위젯 렌더링
        
        Returns:
            MarketSelection: 선택된 시장 정보
        """
        
        st.sidebar.header("⚙️ 분석 설정")
        
        # 시장 타입 선택
        market_type = st.sidebar.selectbox(
            "📊 시장 타입",
            ["stock", "crypto"],
            format_func=lambda x: "주식 시장" if x == "stock" else "암호화폐 시장",
            help="분석할 시장을 선택하세요"
        )
        
        # 종목 선택 부분
        self._render_symbol_selector(market_type)
        
        # 입력된 종목 코드
        if market_type == "stock":
            symbol = st.sidebar.text_input(
                "🏢 종목 코드",
                value=st.session_state.get('selected_symbol', 'AAPL'),
                placeholder="예: AAPL, MSFT, TSLA",
                help="Yahoo Finance에서 지원하는 종목 코드를 입력하세요"
            ).upper()
        else:
            symbol = st.sidebar.text_input(
                "💰 암호화폐 페어",
                value=st.session_state.get('selected_symbol', 'BTC/USDT'),
                placeholder="예: BTC/USDT, ETH/USDT",
                help="거래소에서 지원하는 암호화폐 페어를 입력하세요"
            ).upper()
        
        # 분석 기간 선택
        period = st.sidebar.selectbox(
            "📅 분석 기간",
            list(self.periods.keys()),
            index=1,  # 3mo 기본값
            format_func=lambda x: self.periods[x],
            help="분석에 사용할 데이터 기간을 선택하세요"
        )
        
        # 암호화폐인 경우 거래소 선택
        exchange = None
        if market_type == "crypto":
            exchange = st.sidebar.selectbox(
                "🏦 거래소",
                self.crypto_exchanges,
                index=0,  # binance 기본값
                format_func=lambda x: x.title(),
                help="데이터를 가져올 거래소를 선택하세요"
            )
        
        # 세션 상태 업데이트
        st.session_state['selected_symbol'] = symbol
        
        return MarketSelection(
            market_type=market_type,
            symbol=symbol,
            period=period,
            exchange=exchange
        )
    
    def _render_symbol_selector(self, market_type: str) -> None:
        """
        인기 종목 선택 버튼 렌더링
        
        Args:
            market_type: 시장 타입
        """
        
        if market_type == "stock":
            st.sidebar.markdown("**📈 인기 주식**")
            popular_list = self.popular_stocks
        else:
            st.sidebar.markdown("**🚀 인기 암호화폐**")
            popular_list = self.popular_crypto
        
        # 인기 종목을 3개씩 나누어 버튼으로 표시
        for i in range(0, len(popular_list), 3):
            cols = st.sidebar.columns(3)
            for j, col in enumerate(cols):
                if i + j < len(popular_list):
                    symbol = popular_list[i + j]
                    if col.button(symbol, key=f"popular_{symbol}"):
                        st.session_state['selected_symbol'] = symbol
                        st.rerun()
    
    def render_advanced_options(self) -> Dict[str, any]:
        """
        고급 옵션 렌더링
        
        Returns:
            Dict: 고급 옵션 설정값
        """
        
        with st.sidebar.expander("🔧 고급 설정"):
            
            # 캐시 사용 여부
            use_cache = st.checkbox(
                "캐시 사용",
                value=True,
                help="이전 분석 결과를 캐시에서 불러와 속도를 향상시킵니다"
            )
            
            # 시각화 옵션
            chart_style = st.selectbox(
                "차트 스타일",
                ["default", "dark", "minimal"],
                format_func=lambda x: {"default": "기본", "dark": "다크", "minimal": "미니멀"}[x]
            )
            
            # 분석 세부 레벨
            analysis_level = st.select_slider(
                "분석 상세도",
                options=["기본", "상세", "전문가"],
                value="상세",
                help="분석 결과의 상세 정도를 선택하세요"
            )
            
            # 알림 설정
            enable_alerts = st.checkbox(
                "알림 활성화",
                value=False,
                help="분석 완료 시 알림을 받습니다"
            )
        
        return {
            "use_cache": use_cache,
            "chart_style": chart_style,
            "analysis_level": analysis_level,
            "enable_alerts": enable_alerts
        }
    
    def validate_symbol(self, symbol: str, market_type: str) -> Tuple[bool, str]:
        """
        종목 코드 유효성 검사
        
        Args:
            symbol: 종목 코드
            market_type: 시장 타입
            
        Returns:
            Tuple[bool, str]: (유효성, 오류 메시지)
        """
        
        if not symbol or not symbol.strip():
            return False, "종목 코드를 입력해주세요."
        
        symbol = symbol.strip().upper()
        
        if market_type == "stock":
            # 주식 종목 코드 검사
            if len(symbol) < 1 or len(symbol) > 5:
                return False, "주식 종목 코드는 1-5자리여야 합니다."
            
            if not symbol.isalnum():
                return False, "주식 종목 코드는 영문자와 숫자만 포함해야 합니다."
        
        elif market_type == "crypto":
            # 암호화폐 페어 검사
            if "/" not in symbol:
                return False, "암호화폐는 'BTC/USDT' 형식으로 입력해주세요."
            
            parts = symbol.split("/")
            if len(parts) != 2:
                return False, "올바른 암호화폐 페어 형식이 아닙니다."
            
            base, quote = parts
            if len(base) < 2 or len(quote) < 2:
                return False, "기초/기준 통화는 최소 2자리여야 합니다."
        
        return True, ""
    
    def get_symbol_info(self, symbol: str, market_type: str) -> Dict[str, str]:
        """
        종목 정보 제공
        
        Args:
            symbol: 종목 코드
            market_type: 시장 타입
            
        Returns:
            Dict: 종목 정보
        """
        
        info = {
            "symbol": symbol,
            "market_type": market_type,
            "description": "",
            "sector": "",
            "tips": []
        }
        
        if market_type == "stock":
            stock_info = {
                "AAPL": {"name": "Apple Inc.", "sector": "Technology"},
                "MSFT": {"name": "Microsoft Corporation", "sector": "Technology"},
                "GOOGL": {"name": "Alphabet Inc.", "sector": "Technology"},
                "AMZN": {"name": "Amazon.com Inc.", "sector": "Consumer Discretionary"},
                "TSLA": {"name": "Tesla Inc.", "sector": "Consumer Discretionary"},
                "META": {"name": "Meta Platforms Inc.", "sector": "Technology"},
                "NVDA": {"name": "NVIDIA Corporation", "sector": "Technology"},
                "NFLX": {"name": "Netflix Inc.", "sector": "Communication Services"}
            }
            
            if symbol in stock_info:
                info["description"] = stock_info[symbol]["name"]
                info["sector"] = stock_info[symbol]["sector"]
            
            info["tips"] = [
                "주식 시장은 장 중/장 후 시간에 따라 데이터가 다를 수 있습니다.",
                "대형주는 일반적으로 더 안정적인 패턴을 보입니다.",
                "실적 발표나 뉴스가 심리에 큰 영향을 줄 수 있습니다."
            ]
        
        elif market_type == "crypto":
            crypto_info = {
                "BTC/USDT": {"name": "Bitcoin", "type": "Base Currency"},
                "ETH/USDT": {"name": "Ethereum", "type": "Smart Contract Platform"},
                "BNB/USDT": {"name": "Binance Coin", "type": "Exchange Token"},
                "ADA/USDT": {"name": "Cardano", "type": "Smart Contract Platform"},
                "XRP/USDT": {"name": "Ripple", "type": "Payment Network"},
                "SOL/USDT": {"name": "Solana", "type": "Smart Contract Platform"},
                "DOGE/USDT": {"name": "Dogecoin", "type": "Meme Coin"},
                "AVAX/USDT": {"name": "Avalanche", "type": "Smart Contract Platform"}
            }
            
            if symbol in crypto_info:
                info["description"] = crypto_info[symbol]["name"]
                info["sector"] = crypto_info[symbol]["type"]
            
            info["tips"] = [
                "암호화폐는 24시간 거래되어 변동성이 높습니다.",
                "비트코인이 다른 알트코인에 미치는 영향을 고려하세요.",
                "거래량이 낮은 시간대에는 패턴이 왜곡될 수 있습니다."
            ]
        
        return info
    
    def render_symbol_info_panel(self, symbol: str, market_type: str) -> None:
        """
        종목 정보 패널 렌더링
        
        Args:
            symbol: 종목 코드
            market_type: 시장 타입
        """
        
        info = self.get_symbol_info(symbol, market_type)
        
        with st.sidebar.expander(f"ℹ️ {symbol} 정보"):
            if info["description"]:
                st.write(f"**이름:** {info['description']}")
            
            if info["sector"]:
                st.write(f"**섹터:** {info['sector']}")
            
            st.write("**💡 분석 팁:**")
            for tip in info["tips"]:
                st.write(f"• {tip}")
    
    def render_comparison_tool(self) -> List[str]:
        """
        여러 종목 비교 도구 렌더링
        
        Returns:
            List[str]: 비교할 종목 리스트
        """
        
        with st.sidebar.expander("🔄 종목 비교"):
            st.write("최대 3개 종목까지 비교 가능합니다.")
            
            symbols = []
            for i in range(3):
                symbol = st.text_input(
                    f"종목 {i+1}",
                    key=f"compare_symbol_{i}",
                    placeholder="종목 코드 입력"
                )
                if symbol:
                    symbols.append(symbol.upper())
            
            if len(symbols) > 1:
                st.success(f"{len(symbols)}개 종목 비교 준비 완료")
            
            return symbols


def render_market_status() -> None:
    """시장 상태 정보 표시"""
    
    import datetime
    import pytz
    
    # 현재 시간 (여러 시간대)
    now_utc = datetime.datetime.now(pytz.UTC)
    
    # 주요 시장 시간
    markets = {
        "🇺🇸 미국 (NYSE)": pytz.timezone('America/New_York'),
        "🇰🇷 한국 (KRX)": pytz.timezone('Asia/Seoul'),
        "🇯🇵 일본 (TSE)": pytz.timezone('Asia/Tokyo'),
        "🇬🇧 영국 (LSE)": pytz.timezone('Europe/London')
    }
    
    st.sidebar.markdown("### 🌍 글로벌 시장 현황")
    
    for market_name, tz in markets.items():
        local_time = now_utc.astimezone(tz)
        time_str = local_time.strftime("%H:%M")
        
        # 장 시간 판단 (간단한 로직)
        hour = local_time.hour
        if "NYSE" in market_name or "NASDAQ" in market_name:
            is_open = 9 <= hour <= 16  # 9:30-16:00 (대략)
        elif "KRX" in market_name:
            is_open = 9 <= hour <= 15  # 9:00-15:30 (대략)
        else:
            is_open = 9 <= hour <= 17  # 기본값
        
        status_emoji = "🟢" if is_open else "🔴"
        status_text = "장중" if is_open else "장마감"
        
        st.sidebar.write(f"{market_name}: {time_str} {status_emoji} {status_text}")


# 전역 인스턴스
market_selector = MarketSelector() 