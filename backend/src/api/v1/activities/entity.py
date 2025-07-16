from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Literal, Optional, Dict

from api.v1.activities.constant import WeatherQuality


@dataclass
class GeocodingEntity:
    lat: float = field(metadata={"desc": "검색된 위치의 지리적 좌표(위도)"})
    lon: float = field(metadata={"desc": "발견된 위치의 지리적 좌표(경도)"})


@dataclass
class WeatherEntity:
    condition: Literal["Clear", "Clouds", "Rain", "Snow", "Thunderstorm", "Drizzle", "Mist", "Haze", "Fog"] = field(
        metadata={"desc": "날씨 상태 (맑음, 흐림 등)"}
    )
    description: str = field(metadata={"desc": "날씨 설명 (한국어: 맑음, 흐림 등)"})
    icon: str = field(metadata={"desc": "날씨 아이콘 코드 (OpenWeatherMap 전용)"})

    temperature: float = field(metadata={"desc": "현재 기온 (℃)"})
    feels_like: float = field(metadata={"desc": "체감 기온 (℃)"})
    humidity: int = field(metadata={"desc": "습도 (%)"})

    wind_speed: float = field(metadata={"desc": "풍속 (m/s)"})
    cloudiness: int = field(metadata={"desc": "구름량 (%)"})

    sunset: datetime = field(metadata={"desc": "일몰 시간 (datetime)"})
    latitude: float = field(metadata={"desc": "위도"})
    longitude: float = field(metadata={"desc": "경도"})

    city_name: str = field(metadata={"desc": "도시 이름"})


@dataclass
class WeatherRecommendationEntity:
    outdoor_possible: bool = field(
        metadata={
            "desc": "현재 날씨 조건에 따라 실외 활동이 가능 한지 여부 (예: 비가 오지 않고, 바람이 약하고, 적절한 온도일 때 True)"
        }
    )
    air_quality: WeatherQuality = field(
        metadata={
            "desc": "날씨 전반 적인 활동 적합도 (예: 기온, 풍속, 날씨 상태 등을 종합 하여 '좋음', '보통', '나쁨' 중 하나)"
        }
    )
    uv_risk: WeatherQuality = field(
        metadata={"desc": "자외선 노출 위험도 등급 (구름량 또는 자외선 지수 기반 으로 '좋음', '보통', '나쁨')"}
    )
    weather_condition: str = field(
        metadata={"desc": "기본 적인 날씨 상태 값 (예: Clear, Rain, Clouds 등 OpenWeatherMap 기준 코드)"}
    )
    sunset: datetime = field(metadata={"desc": "현재 지역의 일몰 시간 (추천 활동 시간 제한 계산에 활용됨)"})


@dataclass
class PlaceEntity:
    id: int = field(metadata={"desc": "OpenStreetMap에서 제공하는 고유 ID"})
    name: str = field(metadata={"desc": "장소 이름"})
    lat: float = field(metadata={"desc": "위도"})
    lon: float = field(metadata={"desc": "경도"})
    type: str = field(metadata={"desc": "장소 타입 (cafe, park, museum 등)"})
    description: str = field(metadata={"desc": "장소 설명 및 카테고리 정보"})
    opening_hours: Optional[str] = field(default=None, metadata={"desc": "운영 시간"})
    website: Optional[str] = field(default=None, metadata={"desc": "웹사이트 URL"})
    phone: Optional[str] = field(default=None, metadata={"desc": "전화번호"})
    address: Optional[str] = field(default=None, metadata={"desc": "주소"})
    weather_match_score: Optional[int] = field(default=None, metadata={"desc": "현재 날씨와의 매칭 점수 (0-100)"})
    optimal_timing: Optional[str] = field(default=None, metadata={"desc": "최적 방문 시간 추천"})
    weather_context_info: Optional[Dict[str, str]] = field(default=None, metadata={"desc": "날씨별 장소 특화 정보"})


@dataclass
class PlaceSearchEntity:
    city: str = field(metadata={"desc": "검색 도시"})
    activity_type: str = field(metadata={"desc": "활동 타입 (cafe, park, museum 등)"})
    places: List[PlaceEntity] = field(metadata={"desc": "검색된 장소 목록"})
    total_count: int = field(metadata={"desc": "총 검색 결과 수"})
    search_radius: int = field(metadata={"desc": "검색 반경 (미터)"})
