from typing import Any, Dict

from api.v1.activities.entity import PlaceSearchEntity, WeatherEntity


class ResponseFormatter:
    """응답 데이터 포맷팅을 담당하는 서비스"""

    def __init__(self):
        pass

    async def format_basic_response(
        self, city: str, weather_entity: WeatherEntity, activities: Dict[str, Any], weather_description: str
    ) -> Dict[str, Any]:
        """기본 추천 응답을 프론트엔드 형식으로 포맷팅"""
        return {
            "city": city,
            "weather": {
                "condition": weather_entity.condition,
                "temperature": weather_entity.temperature,
                "humidity": weather_entity.humidity,
                "windSpeed": weather_entity.wind_speed,
                "description": weather_description,
            },
            "recommendations": activities,
        }

    async def format_places_response(self, places_by_type: Dict[str, PlaceSearchEntity]) -> Dict[str, Any]:
        """장소 검색 결과를 프론트엔드 형식으로 포맷팅"""
        formatted_places = {}

        for activity_type, place_search in places_by_type.items():
            places_list = []
            for place in place_search.places:
                place_info = {
                    "id": place.id,
                    "name": place.name,
                    "lat": place.lat,
                    "lon": place.lon,
                    "type": place.type,
                    "description": place.description,
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

                places_list.append(place_info)

            formatted_places[activity_type] = {
                "activity_type": place_search.activity_type,
                "total_count": place_search.total_count,
                "places": places_list,
            }

        # 비어있는 경우를 위한 기본값
        city = ""
        search_radius = 2000

        # 첫 번째 place_search에서 공통 정보 추출
        if places_by_type:
            first_place_search = next(iter(places_by_type.values()))
            city = first_place_search.city
            search_radius = first_place_search.search_radius

        return {
            "city": city,
            "search_radius": search_radius,
            "places_by_type": formatted_places,
        }
            "places_by_type": formatted_places,
        }

    async def format_complete_response(
        self, basic_response: Dict[str, Any], places_response: Dict[str, Any], radius: int
    ) -> Dict[str, Any]:
        """기본 응답과 장소 정보를 결합하여 완전한 응답을 생성"""
        complete_response = basic_response.copy()

        if places_response and "places_by_type" in places_response:
            complete_response["places"] = places_response["places_by_type"]
            complete_response["search_radius"] = radius
            complete_response["total_places_found"] = sum(
                info.get("total_count", 0) for info in places_response["places_by_type"].values()
            )

        return complete_response
