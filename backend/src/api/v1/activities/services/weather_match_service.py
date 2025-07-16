"""
날씨 매칭 점수 계산 서비스

현재 날씨 조건과 각 장소/활동의 적합도를 0-100점으로 계산하여 제공합니다.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta

from api.v1.activities.entity import WeatherEntity, PlaceEntity
from api.v1.activities.constant import WeatherQuality


class WeatherMatchService:
    """날씨 매칭 점수 계산 서비스"""
    
    # 활동 타입별 가중치 정의
    ACTIVITY_WEIGHTS = {
        # 실외 활동 (날씨에 더 민감)
        "park": {"temperature": 0.3, "wind": 0.25, "cloudiness": 0.2, "humidity": 0.15, "condition": 0.1},
        "tourism": {"temperature": 0.25, "wind": 0.2, "cloudiness": 0.25, "humidity": 0.15, "condition": 0.15},
        "outdoor_sports": {"temperature": 0.3, "wind": 0.3, "cloudiness": 0.2, "humidity": 0.1, "condition": 0.1},
        "adventure": {"temperature": 0.35, "wind": 0.25, "cloudiness": 0.2, "humidity": 0.1, "condition": 0.1},
        
        # 실내 활동 (날씨에 덜 민감)
        "cafe": {"temperature": 0.2, "wind": 0.1, "cloudiness": 0.1, "humidity": 0.3, "condition": 0.3},
        "restaurant": {"temperature": 0.2, "wind": 0.1, "cloudiness": 0.1, "humidity": 0.3, "condition": 0.3},
        "museum": {"temperature": 0.15, "wind": 0.05, "cloudiness": 0.1, "humidity": 0.35, "condition": 0.35},
        "shopping": {"temperature": 0.2, "wind": 0.1, "cloudiness": 0.1, "humidity": 0.3, "condition": 0.3},
        "indoor_sports": {"temperature": 0.25, "wind": 0.05, "cloudiness": 0.1, "humidity": 0.3, "condition": 0.3},
        
        # 기본값 (중간 정도 날씨 민감도)
        "default": {"temperature": 0.25, "wind": 0.2, "cloudiness": 0.15, "humidity": 0.2, "condition": 0.2}
    }

    # 온도별 점수 테이블 (활동 타입별)
    TEMPERATURE_SCORES = {
        "outdoor": {
            (15, 25): 100, (10, 15): 80, (25, 30): 80,
            (5, 10): 60, (30, 35): 60, (-5, 5): 30, (35, 45): 30
        },
        "indoor": {
            (18, 26): 100, (15, 18): 90, (26, 30): 90,
            (10, 15): 70, (30, 35): 70, (5, 10): 50, (35, 40): 50
        }
    }

    async def calculate_weather_match_score(self, weather: WeatherEntity, place: PlaceEntity) -> int:
        """날씨와 장소의 매칭 점수를 계산합니다 (0-100점)"""
        
        # 장소 타입에 따른 가중치 선택
        place_type = self._normalize_place_type(place.type)
        weights = self.ACTIVITY_WEIGHTS.get(place_type, self.ACTIVITY_WEIGHTS["default"])
        
        # 각 날씨 요소별 점수 계산
        temp_score = self._calculate_temperature_score(weather.temperature, place_type)
        wind_score = self._calculate_wind_score(weather.wind_speed, place_type)
        humidity_score = self._calculate_humidity_score(weather.humidity)
        cloudiness_score = self._calculate_cloudiness_score(weather.cloudiness, place_type)
        condition_score = self._calculate_condition_score(weather.condition, place_type)
        
        # 가중 평균으로 최종 점수 계산
        final_score = (
            temp_score * weights["temperature"] +
            wind_score * weights["wind"] +
            humidity_score * weights["humidity"] +
            cloudiness_score * weights["cloudiness"] +
            condition_score * weights["condition"]
        )
        
        return max(0, min(100, int(final_score)))

    async def get_optimal_timing(self, weather: WeatherEntity, place: PlaceEntity) -> Optional[str]:
        """최적의 방문 시간을 추천합니다"""
        
        place_type = self._normalize_place_type(place.type)
        current_score = await self.calculate_weather_match_score(weather, place)
        
        # 현재 점수가 80점 이상이면 '지금 바로' 추천
        if current_score >= 80:
            return "지금 바로"
        elif current_score >= 60:
            return "1-2시간 후"
        elif current_score >= 40:
            return "오늘 오후"
        else:
            return "내일 오전"

    def _normalize_place_type(self, place_type: str) -> str:
        """장소 타입을 표준화합니다"""
        place_type_lower = place_type.lower()
        
        # 매핑 테이블
        type_mapping = {
            "cafe": "cafe",
            "coffee": "cafe",
            "restaurant": "restaurant",
            "food": "restaurant",
            "park": "park",
            "garden": "park",
            "museum": "museum",
            "gallery": "museum",
            "shop": "shopping",
            "mall": "shopping",
            "shopping": "shopping",
            "gym": "indoor_sports",
            "fitness": "indoor_sports",
            "sports": "outdoor_sports",
            "tourist_attraction": "tourism",
            "attraction": "tourism",
        }
        
        for key, value in type_mapping.items():
            if key in place_type_lower:
                return value
        
        return "default"

    def _calculate_temperature_score(self, temperature: float, place_type: str) -> float:
        """온도 점수를 계산합니다"""
        category = "outdoor" if place_type in ["park", "tourism", "outdoor_sports", "adventure"] else "indoor"
        scores = self.TEMPERATURE_SCORES[category]
        
        for (min_temp, max_temp), score in scores.items():
            if min_temp <= temperature < max_temp:
                return score
        
        return 20  # 범위를 벗어나는 경우

    def _calculate_wind_score(self, wind_speed: float, place_type: str) -> float:
        """바람 점수를 계산합니다"""
        if place_type in ["park", "outdoor_sports", "adventure"]:
            # 실외 활동에서는 바람이 중요
            if wind_speed <= 3:
                return 100
            elif wind_speed <= 6:
                return 80
            elif wind_speed <= 10:
                return 60
            else:
                return 30
        else:
            # 실내 활동에서는 바람이 덜 중요
            return 90

    def _calculate_humidity_score(self, humidity: float) -> float:
        """습도 점수를 계산합니다"""
        if 40 <= humidity <= 70:
            return 100
        elif 30 <= humidity < 40 or 70 < humidity <= 80:
            return 80
        elif 20 <= humidity < 30 or 80 < humidity <= 90:
            return 60
        else:
            return 40

    def _calculate_cloudiness_score(self, cloudiness: float, place_type: str) -> float:
        """구름량 점수를 계산합니다"""
        if place_type in ["park", "tourism", "outdoor_sports"]:
            # 실외 활동에서는 맑은 날이 좋음
            if cloudiness <= 20:
                return 100
            elif cloudiness <= 50:
                return 80
            elif cloudiness <= 80:
                return 60
            else:
                return 40
        else:
            # 실내 활동에서는 구름량이 덜 중요
            return 80

    def _calculate_condition_score(self, condition: str, place_type: str) -> float:
        """날씨 상태 점수를 계산합니다"""
        condition_lower = condition.lower()
        
        if place_type in ["park", "tourism", "outdoor_sports", "adventure"]:
            # 실외 활동
            if condition_lower == "clear":
                return 100
            elif condition_lower == "clouds":
                return 80
            elif condition_lower in ["mist", "haze"]:
                return 60
            elif condition_lower in ["rain", "drizzle"]:
                return 20
            elif condition_lower in ["thunderstorm", "snow"]:
                return 10
            else:
                return 50
        else:
            # 실내 활동 (날씨의 영향을 덜 받음)
            if condition_lower in ["rain", "drizzle", "thunderstorm"]:
                return 100  # 비 오는 날 실내 활동 선호
            elif condition_lower == "clear":
                return 70   # 맑은 날에는 실외 선호 경향
            else:
                return 85
    
    def generate_weather_context(self, weather: WeatherEntity, place: PlaceEntity) -> str:
        """날씨별 상황 정보 및 팁을 생성합니다."""
        activity_type = self._normalize_place_type(place.type)
        context_tips = []
        
        # 온도 관련 팁
        if weather.temperature < 10:
            if activity_type in ["park", "tourism", "outdoor_sports"]:
                context_tips.append("⛄ 따뜻한 옷차림 필수, 실내 휴게 공간 확인 권장")
            else:
                context_tips.append("🏠 실내 활동으로 추위를 피하기 좋은 시간")
        elif weather.temperature > 30:
            if activity_type in ["park", "tourism"]:
                context_tips.append("🌞 그늘진 곳 우선 방문, 충분한 수분 섭취 필요")
            elif activity_type == "cafe":
                context_tips.append("❄️ 시원한 음료와 에어컨이 있는 실내에서 더위 피하기")
        elif 18 <= weather.temperature <= 25:
            if activity_type in ["park", "outdoor_sports"]:
                context_tips.append("🌟 야외 활동하기 완벽한 날씨")
        
        # 바람 관련 팁
        if weather.wind_speed > 8 and activity_type in ["park", "outdoor_sports"]:
            context_tips.append("💨 강풍 주의, 바람막이 복장 권장")
        
        # 날씨 상태 관련 팁
        if weather.condition == "Rain":
            if activity_type in ["cafe", "museum", "shopping"]:
                context_tips.append("☔ 비 오는 날 실내에서 여유롭게 보내기 좋음")
            else:
                context_tips.append("☔ 우산 필수, 실내 대안 활동 고려")
        elif weather.condition == "Clear":
            if activity_type in ["park", "tourism"]:
                context_tips.append("☀️ 맑은 날, 야외 활동과 사진 촬영에 최적")
        elif weather.condition in ["Mist", "Fog"]:
            context_tips.append("🌫️ 시야 제한, 안전 운전 및 이동 주의")
        
        # 습도 관련 팁
        if weather.humidity > 80:
            context_tips.append("💧 높은 습도로 끈적함 주의, 시원한 실내 공간 추천")
        
        # 장소별 특화 팁
        if activity_type == "cafe":
            if weather.condition in ["Rain", "Snow"]:
                context_tips.append("☕ 창가 자리에서 비/눈 구경하며 따뜻한 음료 즐기기")
            elif weather.temperature > 25:
                context_tips.append("🧊 아이스 음료와 에어컨 자리 추천")
        elif activity_type == "park":
            if 18 <= weather.temperature <= 25 and weather.wind_speed <= 5:
                context_tips.append("🌸 산책, 피크닉, 야외 운동에 완벽한 조건")
        
        return " | ".join(context_tips) if context_tips else "현재 날씨에서 방문 가능한 장소입니다."
    
    def get_optimal_time_recommendation(self, weather: WeatherEntity, place: PlaceEntity) -> str:
        """최적 방문 시간을 추천합니다."""
        activity_type = self._normalize_place_type(place.type)
        current_hour = datetime.now().hour
        
        if activity_type in ["park", "tourism", "outdoor_sports"]:
            if weather.temperature > 30:
                return "오전 9-11시 또는 오후 5시 이후 (더위 피하기)"
            elif weather.temperature < 5:
                return "오후 12-3시 (가장 따뜻한 시간대)"
            elif weather.condition == "Clear":
                return "오전 10시-오후 4시 (일조량 충분한 시간대)"
            else:
                return "언제든 방문 가능"
        elif activity_type == "cafe":
            if weather.condition in ["Rain", "Snow"]:
                return "오후 2-5시 (여유로운 차 시간)"
            else:
                return "오전 10시-오후 6시 (카페 이용하기 좋은 시간)"
        elif activity_type in ["restaurant"]:
            return "점심시간(12-2시) 또는 저녁시간(6-8시)"
        else:
            return "운영시간 내 언제든 방문 가능"

    def get_weather_context_info(self, place: PlaceEntity, weather: WeatherEntity) -> Dict[str, str]:
        """날씨 조건에 따른 장소별 특화 정보를 제공합니다."""
        place_type = self._get_place_category(place.type)
        
        context_info = {
            "weather_tip": "",
            "recommended_area": "",
            "special_note": ""
        }
        
        # 온도 기반 팁
        if weather.temperature > 28:
            if place_type in ["cafe", "restaurant"]:
                context_info["weather_tip"] = "에어컨이 잘 되는 실내 좌석 추천"
                context_info["recommended_area"] = "실내 중앙 테이블"
            elif place_type == "park":
                context_info["weather_tip"] = "그늘진 곳에서 휴식 추천"
                context_info["recommended_area"] = "나무 그늘 아래 벤치"
        elif weather.temperature < 10:
            if place_type in ["cafe", "restaurant"]:
                context_info["weather_tip"] = "따뜻한 음료와 실내 좌석 추천"
                context_info["recommended_area"] = "창가 자리 (햇빛 있는 곳)"
            elif place_type == "park":
                context_info["weather_tip"] = "실내 시설 이용 추천"
                context_info["recommended_area"] = "실내 전시관이나 온실"
        
        # 바람 기반 팁
        if weather.wind_speed > 5:
            if place_type in ["cafe", "restaurant"]:
                context_info["weather_tip"] = "바람막이가 있는 실내 좌석 추천"
                context_info["recommended_area"] = "실내 안쪽 자리"
            elif place_type == "park":
                context_info["weather_tip"] = "바람막이가 있는 곳 추천"
                context_info["recommended_area"] = "건물이나 나무에 가린 곳"
        
        # 습도 기반 팁
        if weather.humidity > 70:
            context_info["special_note"] = "습도가 높아 쾌적함을 위해 에어컨 시설 확인 필요"
        
        # 구름량 기반 팁
        if weather.cloudiness > 80:
            if place_type in ["cafe", "restaurant"]:
                context_info["weather_tip"] = "아늑한 실내 분위기 즐기기 좋은 날"
            elif place_type == "park":
                context_info["weather_tip"] = "야외 활동하기 적당한 날씨"
        elif weather.cloudiness < 20:
            if place_type in ["cafe", "restaurant"]:
                context_info["weather_tip"] = "테라스나 야외 좌석 추천"
                context_info["recommended_area"] = "야외 테라스나 창가 자리"
            elif place_type == "park":
                context_info["weather_tip"] = "맑은 하늘 아래 야외 활동 최적"
        
        return context_info

    def _get_place_category(self, place_type: str) -> str:
        """장소 타입을 대분류로 변환합니다."""
        cafe_types = ["cafe", "coffee_shop", "tea_house"]
        restaurant_types = ["restaurant", "fast_food", "pub", "bar", "food_court"]
        park_types = ["park", "garden", "recreation_ground", "nature_reserve"]
        tourism_types = ["museum", "gallery", "attraction", "monument", "castle"]
        
        if place_type in cafe_types:
            return "cafe"
        elif place_type in restaurant_types:
            return "restaurant"
        elif place_type in park_types:
            return "park"
        elif place_type in tourism_types:
            return "tourism"
        else:
            return "other" 