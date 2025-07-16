from typing import Any, Dict

from dependency_injector.wiring import inject

from api.v1.activities.formatters.response_formatter import ResponseFormatter
from api.v1.activities.services.activity_service import ActivityService
from api.v1.activities.services.place_service import PlaceService
from api.v1.activities.services.weather_service import WeatherService
from api.v1.activities.services.weather_match_service import WeatherMatchService


class RecommendationService:
    """전체 추천 로직을 조율하는 서비스"""

    @inject
    def __init__(
        self,
        weather_service: WeatherService,
        place_service: PlaceService,
        activity_service: ActivityService,
        response_formatter: ResponseFormatter,
        weather_match_service: WeatherMatchService,
    ):
        self.weather_service = weather_service
        self.place_service = place_service
        self.activity_service = activity_service
        self.response_formatter = response_formatter
        self.weather_match_service = weather_match_service

    async def get_complete_recommendation_info(self, city: str, radius: int = 2000) -> Dict[str, Any]:
        """날씨 정보, 활동 추천, 장소 정보를 한 번에 가져오는 통합 함수"""

        # 1. 기본 날씨 및 추천 정보 가져오기
        geocoding_entity = await self.weather_service.get_geocoding(city)
        weather_entity = await self.weather_service.get_weather_info_3(geocoding_entity)
        recommendation_entity = await self.weather_service.get_recommendations(weather_entity)

        # 2. 활동 추천 생성
        activities_list = await self.activity_service.get_activities(recommendation_entity)
        classified_activities = await self.activity_service.classify_activities(activities_list, city)

        # 3. 기본 응답 구성
        weather_description = self.weather_service.translate_weather_condition(weather_entity.condition)
        response = await self.response_formatter.format_basic_response(
            city, weather_entity, classified_activities, weather_description
        )

        # 4. 장소 정보 추가 (항상 포함)
        # 날씨에 따른 활동 타입 결정
        activity_types = self.activity_service.get_activity_types_by_weather(recommendation_entity)

        # 장소 검색 (병렬 처리)
        places_by_type = await self.place_service.search_places_by_multiple_activities(
            geocoding_entity, city, activity_types, radius
        )

        # 장소 응답 포맷팅 (Weather Match Score 포함)
        translated_places = {}
        for activity_type, place_search in places_by_type.items():
            translated_key = self.place_service.translate_activity_type(activity_type)
            translated_places[translated_key] = {
                "activity_type": activity_type,
                "total_count": place_search.total_count,
                "places": [],
            }

            for place in place_search.places:
                # Weather Match Score 계산
                weather_match_score = await self.weather_match_service.calculate_weather_match_score(
                    weather_entity, place
                )
                optimal_timing = await self.weather_match_service.get_optimal_timing(
                    weather_entity, place
                )
                
                place_info = {
                    "id": place.id,
                    "name": place.name,
                    "lat": place.lat,
                    "lon": place.lon,
                    "type": place.type,
                    "description": place.description,
                    "weather_match_score": weather_match_score,
                    "optimal_timing": optimal_timing,
                }

                # 선택적 필드 추가
                if place.opening_hours:
                    place_info["opening_hours"] = place.opening_hours
                if place.website:
                    place_info["website"] = place.website
                if place.phone:
                    place_info["phone"] = place.phone
                if place.address:
                    place_info["address"] = place.address

                translated_places[translated_key]["places"].append(place_info)

        # Weather Match Score 기준으로 장소 정렬
        for activity_data in translated_places.values():
            activity_data["places"].sort(key=lambda x: x.get("weather_match_score", 0), reverse=True)

        # 완전한 응답 생성
        response["places"] = translated_places
        response["search_radius"] = radius
        response["total_places_found"] = sum(
            place_info.get("total_count", 0) for place_info in translated_places.values()
        )

        return response

    async def get_weather_based_places(self, city: str, radius: int = 2000) -> Dict[str, Any]:
        """하위 호환성을 위한 날씨 기반 장소 검색 (레거시 지원)"""
        result = await self.get_complete_recommendation_info(city, radius=radius)

        # 기존 형식으로 변환
        if "places" in result:
            return {"city": city, "search_radius": radius, "places_by_type": result["places"]}

        return {"city": city, "search_radius": radius, "places_by_type": {}}
