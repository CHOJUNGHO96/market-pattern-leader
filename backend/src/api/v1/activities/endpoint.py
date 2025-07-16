from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from api.v1.activities.services import PlaceService, RecommendationService, WeatherService

router = APIRouter()


@router.get("/")
@inject
async def get_recommendation_info(
    city: str,
    radius: int = Query(2000, description="장소 검색 반경 (미터)", ge=500, le=10000),
    recommendation_service: RecommendationService = Depends(Provide["activities_container.recommendation_service"]),
):
    """
    날씨 정보를 토대로 활동 추천 및 실제 장소 정보를 제공하는 엔드포인트

    - **city**: 검색할 도시명
    - **radius**: 장소 검색 반경 (미터, 기본값: 2000m)

    날씨 조건을 분석하여 적합한 활동을 추천하고, 실제 장소 정보도 함께 제공합니다.
    """
    try:
        # 날씨 기반 추천 및 장소 정보를 항상 포함하여 반환
        response = await recommendation_service.get_complete_recommendation_info(city=city, radius=radius)

        return response

    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"서비스 오류가 발생했습니다: {str(e)}"}


@router.get("/places")
@inject
async def search_places_by_activity(
    city: str,
    activity_type: str = Query(
        ...,
        description="활동 타입 (cafe, park, museum, shopping, sports, education, entertainment, outdoor, transport)",
    ),
    radius: int = Query(2000, description="검색 반경 (미터)", ge=500, le=10000),

    place_service: PlaceService = Depends(Provide["activities_container.place_service"]),
    weather_service: WeatherService = Depends(Provide["activities_container.weather_service"]),
):
    """
    특정 활동 타입의 장소들을 검색하는 엔드포인트

    - **city**: 검색할 도시명
    - **activity_type**: 활동 타입
    - **radius**: 검색 반경 (미터, 기본값: 2000m)

    지정된 활동 타입에 맞는 장소들을 OpenStreetMap에서 검색하여 반환합니다.
    """
    try:
        # 지오코딩 수행
        geocoding_entity = await weather_service.get_geocoding(city)

        # 장소 검색
        place_search = await place_service.search_places_by_activity(
            geocoding_entity=geocoding_entity, city=city, activity_type=activity_type, radius=radius
        )

        # 응답 포맷팅
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

        return {
            "city": city,
            "activity_type": activity_type,
            "activity_type_korean": place_service.translate_activity_type(activity_type),
            "total_count": place_search.total_count,
            "search_radius": radius,
            "places": places_list,
        }

    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"장소 검색 중 오류가 발생했습니다: {str(e)}"}
