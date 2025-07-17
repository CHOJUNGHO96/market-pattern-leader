import asyncio
from typing import Dict, List

from dependency_injector.wiring import inject

from api.v1.activities.entity import GeocodingEntity, PlaceEntity, PlaceSearchEntity
from infrastructure.external.openstreetmap_client import OpenStreetMapClient


class PlaceService:
    """장소 검색 및 관련 기능을 담당하는 서비스"""

    @inject
    def __init__(self, osm_client: OpenStreetMapClient):
        self.osm_client = osm_client

    async def search_places_by_activity(
        self, geocoding_entity: GeocodingEntity, city: str, activity_type: str, radius: int = 2000
    ) -> PlaceSearchEntity:
        """특정 활동 타입에 맞는 장소들을 OpenStreetMap에서 검색합니다."""
        # OpenStreetMap에서 장소 검색
        places_data = await self.osm_client.search_places(
            lat=geocoding_entity.lat, lon=geocoding_entity.lon, activity_type=activity_type, radius=radius
        )

        # PlaceEntity 객체로 변환
        places = []
        for place_data in places_data:
            place = PlaceEntity(
                id=place_data["id"],
                name=place_data["name"],
                lat=place_data["lat"],
                lon=place_data["lon"],
                type=place_data["type"],
                description=place_data["description"],
                opening_hours=place_data.get("opening_hours"),
                website=place_data.get("website"),
                phone=place_data.get("phone"),
                address=place_data.get("address"),
            )
            places.append(place)

        return PlaceSearchEntity(
            city=city, activity_type=activity_type, places=places, total_count=len(places), search_radius=radius
        )

    async def search_places_by_multiple_activities(
        self, geocoding_entity: GeocodingEntity, city: str, activity_types: List[str], radius: int = 2000
    ) -> Dict[str, PlaceSearchEntity]:
        """여러 활동 타입의 장소들을 병렬로 검색합니다."""

        async def search_single_activity(activity_type: str):
            try:
                places_data = await self.osm_client.search_places(
                    lat=geocoding_entity.lat, lon=geocoding_entity.lon, activity_type=activity_type, radius=radius
                )

                # PlaceEntity 객체로 변환
                places = []
                for place_data in places_data:
                    place = PlaceEntity(
                        id=place_data["id"],
                        name=place_data["name"],
                        lat=place_data["lat"],
                        lon=place_data["lon"],
                        type=place_data["type"],
                        description=place_data["description"],
                        opening_hours=place_data.get("opening_hours"),
                        website=place_data.get("website"),
                        phone=place_data.get("phone"),
                        address=place_data.get("address"),
                    )
                    places.append(place)

                return activity_type, PlaceSearchEntity(
                    city=city, activity_type=activity_type, places=places, total_count=len(places), search_radius=radius
                )

            except Exception as e:
                print(f"장소 검색 실패 ({activity_type}): {str(e)}")
                return activity_type, None

        # 모든 활동 타입을 병렬로 검색
        search_tasks = [search_single_activity(activity_type) for activity_type in activity_types]
        results = await asyncio.gather(*search_tasks, return_exceptions=True)

        # 결과 수집
        places_by_type = {}
        for result in results:
            if isinstance(result, tuple) and result[1] is not None:
                activity_type, place_search = result
                places_by_type[activity_type] = place_search

        return places_by_type

    async def close(self):
        """리소스 정리"""
        if hasattr(self.osm_client, 'close'):
            await self.osm_client.close()

    def translate_activity_type(self, activity_type: str) -> str:
        """활동 타입을 한글로 변환"""
        activity_type_korean = {
            "cafe": "카페",
            "park": "공원",
            "museum": "박물관/미술관",
            "shopping": "쇼핑",
            "sports": "스포츠시설",
            "education": "교육시설",
            "entertainment": "엔터테인먼트",
            "outdoor": "야외관광지",
            "transport": "교통시설",
        }
        return activity_type_korean.get(activity_type, activity_type)
