from typing import Dict, List

from api.v1.activities.entity import WeatherQuality, WeatherRecommendationEntity


class ActivityService:
    """활동 추천 및 분류 기능을 담당하는 서비스"""

    def __init__(self):
        pass

    async def get_activities(self, recommendation_entity: WeatherRecommendationEntity) -> List[str]:
        """날씨 추천 정보를 바탕으로 활동 목록을 생성합니다."""
        activities = []

        # 전반적인 날씨 품질에 따른 기본 활동 추천
        if recommendation_entity.outdoor_possible and recommendation_entity.air_quality == WeatherQuality.GOOD:
            # 야외 활동에 최적인 날씨
            activities.extend(
                ["공원에서 산책하기", "야외 운동하기", "자전거 타기", "피크닉 즐기기", "야외 카페에서 휴식"]
            )
        elif recommendation_entity.outdoor_possible and recommendation_entity.air_quality == WeatherQuality.NORMAL:
            # 야외 활동 가능하지만 조건이 보통인 경우
            activities.extend(["짧은 산책하기", "가벼운 야외 활동", "그늘진 공원 방문", "실내외 겸용 카페 가기"])
        else:
            # 실내 활동 추천 (날씨가 나쁘거나 야외 활동 부적합)
            activities.extend(
                ["실내 카페 가기", "박물관 관람하기", "쇼핑몰 가기", "도서관에서 독서", "실내 문화시설 방문"]
            )

        return activities

    async def classify_activities(self, activities: List[str], city: str) -> Dict[str, List[str]]:
        """활동 목록을 실내/실외로 분류"""
        indoor_keywords = ["실내", "카페", "관람", "박물관", "도서관", "쇼핑", "영화관", "서점", "문화시설"]
        indoor_activities = [act for act in activities if any(keyword in act for keyword in indoor_keywords)]
        outdoor_activities = [act for act in activities if not any(keyword in act for keyword in indoor_keywords)]

        # 활동이 충분하지 않은 경우 기본 활동 추가
        if len(indoor_activities) < 3:
            default_indoor = [
                f"{city} 카페에서 휴식",
                f"{city} 박물관 방문",
                f"{city} 미술관 관람",
                "실내 영화관 관람",
                "쇼핑몰 쇼핑",
                "도서관에서 독서",
            ]
            indoor_activities.extend([act for act in default_indoor if act not in indoor_activities])

        if len(outdoor_activities) < 3:
            default_outdoor = [
                f"{city} 공원 산책",
                f"{city} 근처 등산",
                f"{city} 주변 하이킹",
                f"{city} 자전거 타기",
                f"{city} 명소 관광",
            ]
            outdoor_activities.extend([act for act in default_outdoor if act not in outdoor_activities])

        return {"indoor": indoor_activities, "outdoor": outdoor_activities}

    def get_activity_types_by_weather(self, recommendation: WeatherRecommendationEntity) -> List[str]:
        """날씨 추천에 따라 적절한 활동 타입들을 반환합니다."""
        # 날씨 품질이 나쁘거나 야외 활동이 불가능한 경우
        if not recommendation.outdoor_possible or recommendation.air_quality == WeatherQuality.BAD:
            # 실내 활동 위주 (습도가 높거나 온도/바람이 극단적인 경우 포함)
            return ["cafe", "museum", "shopping", "entertainment", "education"]
        elif recommendation.weather_condition in ["Rain", "Snow", "Thunderstorm"]:
            # 비/눈/번개 시 실내 활동
            return ["cafe", "museum", "shopping", "entertainment"]
        elif recommendation.uv_risk == WeatherQuality.BAD:
            # 자외선 위험 시 그늘진 곳이나 실내
            return ["cafe", "museum", "park", "shopping"]
        elif recommendation.air_quality == WeatherQuality.NORMAL:
            # 날씨가 보통인 경우 (습도나 다른 조건이 약간 부적합)
            return ["cafe", "park", "museum", "shopping", "education"]
        else:
            # 좋은 날씨 시 실외 활동 포함
            return ["park", "outdoor", "cafe", "museum", "sports"]
