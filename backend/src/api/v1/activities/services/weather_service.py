from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from dependency_injector.wiring import inject

from api.v1.activities.entity import GeocodingEntity, WeatherEntity, WeatherQuality, WeatherRecommendationEntity


class WeatherService:
    """날씨 정보 조회 및 날씨 기반 추천을 담당하는 서비스"""

    @inject
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    async def get_geocoding(self, city: str) -> GeocodingEntity:
        """도시명을 통해 위도, 경도 정보를 가져옵니다."""
        api_key = self.config["OPEN_WEATHER_MAP_API_KEY"]
        url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"

        response = requests.get(url)
        data = response.json()

        if not data:
            raise ValueError(f"도시 '{city}'를 찾을 수 없습니다.")

        return GeocodingEntity(lat=data[0]["lat"], lon=data[0]["lon"])

    async def get_weather_info_3(self, geocoding_entity: GeocodingEntity) -> WeatherEntity:
        """위도, 경도를 통해 날씨 정보를 가져옵니다."""
        api_key = self.config["OPEN_WEATHER_MAP_API_KEY"]
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={geocoding_entity.lat}&lon={geocoding_entity.lon}&appid={api_key}&units=metric"

        response = requests.get(url)
        data = response.json()

        return WeatherEntity(
            condition=data["weather"][0]["main"],
            description=data["weather"][0]["description"],
            icon=data["weather"][0]["icon"],
            temperature=data["main"]["temp"],
            feels_like=data["main"]["feels_like"],
            humidity=data["main"]["humidity"],
            wind_speed=data["wind"]["speed"],
            cloudiness=data["clouds"]["all"],
            sunset=datetime.fromtimestamp(data["sys"]["sunset"]),
            latitude=float(geocoding_entity.lat),
            longitude=float(geocoding_entity.lon),
            city_name=data["name"],
        )

    async def get_hourly_forecast(self, geocoding_entity: GeocodingEntity, hours: int = 12) -> List[Dict]:
        """시간별 날씨 예보를 가져옵니다 (최대 12시간)"""
        api_key = self.config["OPEN_WEATHER_MAP_API_KEY"]
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={geocoding_entity.lat}&lon={geocoding_entity.lon}&appid={api_key}&units=metric"

        response = requests.get(url)
        data = response.json()

        hourly_data = []
        current_time = datetime.now()
        
        # 최대 hours 시간까지의 예보 데이터 수집
        for i, forecast in enumerate(data["list"][:hours]):
            forecast_time = current_time + timedelta(hours=i*3)  # 3시간 간격
            
            hourly_data.append({
                "datetime": forecast_time,
                "hour": forecast_time.hour,
                "temperature": forecast["main"]["temp"],
                "feels_like": forecast["main"]["feels_like"],
                "humidity": forecast["main"]["humidity"],
                "wind_speed": forecast["wind"]["speed"],
                "condition": forecast["weather"][0]["main"],
                "description": forecast["weather"][0]["description"],
                "cloudiness": forecast["clouds"]["all"],
            })
        
        return hourly_data

    async def find_optimal_timing(self, geocoding_entity: GeocodingEntity, activity_type: str = "outdoor") -> Optional[str]:
        """최적의 활동 시간을 찾아 반환합니다"""
        try:
            hourly_forecast = await self.get_hourly_forecast(geocoding_entity, 12)
            
            best_score = -1
            best_time = None
            
            for forecast in hourly_forecast:
                # 간단한 점수 계산 (실제로는 activity_type에 따라 다르게 계산)
                score = self._calculate_timing_score(forecast, activity_type)
                
                if score > best_score:
                    best_score = score
                    best_time = forecast["datetime"]
            
            if best_time:
                current_time = datetime.now()
                time_diff = best_time - current_time
                
                if time_diff.total_seconds() < 3600:  # 1시간 이내
                    return "지금 바로"
                elif time_diff.total_seconds() < 7200:  # 2시간 이내
                    return f"{best_time.hour}시경 ({int(time_diff.total_seconds() / 3600)}시간 후)"
                else:
                    return f"{best_time.hour}시경"
            
            return None
        except Exception:
            return None

    def _calculate_timing_score(self, forecast: Dict, activity_type: str) -> float:
        """특정 시간대의 활동 적합도 점수를 계산합니다"""
        score = 100.0
        
        # 온도 점수 (18-26도가 최적)
        temp = forecast["temperature"]
        if 18 <= temp <= 26:
            temp_score = 100
        elif 10 <= temp < 18 or 26 < temp <= 30:
            temp_score = 80
        elif 5 <= temp < 10 or 30 < temp <= 35:
            temp_score = 60
        else:
            temp_score = 30
        
        # 습도 점수 (40-70%가 최적)
        humidity = forecast["humidity"]
        if 40 <= humidity <= 70:
            humidity_score = 100
        elif 30 <= humidity < 40 or 70 < humidity <= 80:
            humidity_score = 80
        else:
            humidity_score = 50
        
        # 바람 점수 (5m/s 이하가 최적)
        wind_speed = forecast["wind_speed"]
        if wind_speed <= 5:
            wind_score = 100
        elif wind_speed <= 8:
            wind_score = 80
        else:
            wind_score = 60
        
        # 날씨 상태 점수
        condition = forecast["condition"]
        if condition == "Clear":
            condition_score = 100
        elif condition == "Clouds":
            condition_score = 85
        elif condition in ["Mist", "Haze"]:
            condition_score = 70
        else:
            condition_score = 40
        
        # 가중 평균 계산
        if activity_type == "outdoor":
            score = (temp_score * 0.3 + humidity_score * 0.2 + wind_score * 0.3 + condition_score * 0.2)
        else:  # indoor
            score = (temp_score * 0.4 + humidity_score * 0.3 + condition_score * 0.3)
        
        return score

    def _calculate_overall_quality(self, *qualities: WeatherQuality) -> WeatherQuality:
        """여러 날씨 품질 지표를 종합하여 전반적인 품질을 계산합니다."""
        if WeatherQuality.BAD in qualities:
            return WeatherQuality.BAD
        elif WeatherQuality.NORMAL in qualities:
            return WeatherQuality.NORMAL
        else:
            return WeatherQuality.GOOD

    async def get_recommendations(self, weather_entity: WeatherEntity) -> WeatherRecommendationEntity:
        """날씨 정보를 바탕으로 추천 정보를 생성합니다."""
        # 온도 기반 평가
        temp_quality = WeatherQuality.GOOD
        if weather_entity.temperature < 0 or weather_entity.temperature > 35:
            temp_quality = WeatherQuality.BAD
        elif weather_entity.temperature < 10 or weather_entity.temperature > 30:
            temp_quality = WeatherQuality.NORMAL

        # 습도 기반 평가 (60-70% 쾌적, 70-80% 보통, 80%+ 불쾌)
        humidity_quality = WeatherQuality.GOOD
        if weather_entity.humidity > 80:
            humidity_quality = WeatherQuality.BAD
        elif weather_entity.humidity > 70:
            humidity_quality = WeatherQuality.NORMAL

        # 바람 기반 평가
        wind_quality = WeatherQuality.GOOD
        if weather_entity.wind_speed > 10:
            wind_quality = WeatherQuality.BAD
        elif weather_entity.wind_speed > 7:
            wind_quality = WeatherQuality.NORMAL

        # UV 위험도 (간단한 로직)
        uv_risk = WeatherQuality.NORMAL
        if weather_entity.condition == "Clear" and weather_entity.temperature > 25:
            uv_risk = WeatherQuality.BAD

        # 전반적인 날씨 품질 (온도, 습도, 바람을 종합 고려)
        overall_air_quality = self._calculate_overall_quality(temp_quality, humidity_quality, wind_quality)

        # 실외 활동 가능 여부 (날씨 상태, 온도, 습도, 바람 모두 고려)
        outdoor_possible = (
            weather_entity.condition not in ["Rain", "Snow", "Thunderstorm"]
            and temp_quality != WeatherQuality.BAD
            and humidity_quality != WeatherQuality.BAD
            and wind_quality != WeatherQuality.BAD
        )

        return WeatherRecommendationEntity(
            weather_condition=weather_entity.condition,
            air_quality=overall_air_quality,
            uv_risk=uv_risk,
            outdoor_possible=outdoor_possible,
            sunset=weather_entity.sunset,
        )

    def translate_weather_condition(self, condition: str) -> str:
        """날씨 상태를 영어에서 한글로 변환"""
        weather_condition_korean = {
            "Clear": "맑음",
            "Clouds": "구름 많음",
            "Rain": "비",
            "Snow": "눈",
            "Thunderstorm": "천둥번개",
            "Drizzle": "이슬비",
            "Mist": "안개",
            "Haze": "옅은 안개",
            "Fog": "짙은 안개",
        }
        return weather_condition_korean.get(condition, condition)
