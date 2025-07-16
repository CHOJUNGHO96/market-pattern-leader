import asyncio
import logging
from typing import Dict, List, Optional

import aiohttp
from aiohttp import ClientSession, ClientTimeout


class OpenStreetMapClient:
    """OpenStreetMap Overpass API 클라이언트"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.base_url = "https://overpass-api.de/api/interpreter"
        self.timeout = ClientTimeout(total=30, connect=10)
        self._session: Optional[ClientSession] = None

    async def _get_session(self) -> ClientSession:
        """세션을 가져오거나 생성합니다."""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=10,
                limit_per_host=5,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )
            self._session = ClientSession(
                timeout=self.timeout,
                connector=connector,
                headers={"User-Agent": "WeatherVibe/1.0"}
            )
        return self._session

    async def _make_request(self, query: str) -> Dict:
        """Overpass API에 요청을 보내고 응답을 반환합니다."""
        session = None
        try:
            session = await self._get_session()
            data = {"data": query}
            
            async with session.post(self.base_url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.info(f"OpenStreetMap API 요청 성공: {len(result.get('elements', []))}개 결과")
                    return result
                else:
                    self.logger.error(f"OpenStreetMap API 오류: {response.status}")
                    return {"elements": []}
                    
        except asyncio.TimeoutError:
            self.logger.error("OpenStreetMap API 요청 타임아웃")
            return {"elements": []}
        except aiohttp.ClientError as e:
            self.logger.error(f"OpenStreetMap API 클라이언트 오류: {str(e)}")
            return {"elements": []}
        except Exception as e:
            self.logger.error(f"OpenStreetMap API 요청 실패: {str(e)}")
            return {"elements": []}

    def _build_query(self, lat: float, lon: float, radius: int, amenity_types: List[str]) -> str:
        """Overpass QL 쿼리를 생성합니다."""
        amenity_conditions = []
        for amenity_type in amenity_types:
            if "=" in amenity_type:
                # key=value 형태 (예: "leisure=park")
                key, value = amenity_type.split("=", 1)
                amenity_conditions.append(f'["{key}"="{value}"]')
            else:
                # amenity 타입만 지정 (예: "cafe")
                amenity_conditions.append(f'["amenity"="{amenity_type}"]')

        # 각 amenity 타입에 대해 node와 way 모두 검색
        search_parts = []
        for condition in amenity_conditions:
            search_parts.extend(
                [f"node{condition}(around:{radius},{lat},{lon});", f"way{condition}(around:{radius},{lat},{lon});"]
            )

        query = f"""
        [out:json][timeout:25];
        (
          {chr(10).join(search_parts)}
        );
        out geom;
        """
        return query

    async def search_places(self, lat: float, lon: float, activity_type: str, radius: int = 2000) -> List[Dict]:
        """활동 타입에 따라 주변 장소를 검색합니다."""

        # 활동 타입별 OpenStreetMap 태그 매핑
        activity_mapping = {
            "cafe": ["cafe", "restaurant", "fast_food", "bar"],
            "park": ["leisure=park", "leisure=garden", "leisure=playground", "natural=park"],
            "museum": ["tourism=museum", "tourism=gallery", "tourism=attraction"],
            "shopping": ["shop", "tourism=hotel", "amenity=marketplace"],
            "sports": ["leisure=sports_centre", "leisure=fitness_centre", "leisure=swimming_pool", "leisure=stadium"],
            "education": ["amenity=library", "amenity=university", "amenity=school"],
            "entertainment": ["amenity=cinema", "amenity=theatre", "leisure=amusement_arcade"],
            "outdoor": ["leisure=park", "natural=beach", "leisure=nature_reserve", "tourism=viewpoint"],
            "transport": ["highway=bus_stop", "railway=station", "amenity=parking"],
        }

        amenity_types = activity_mapping.get(activity_type, ["cafe"])
        query = self._build_query(lat, lon, radius, amenity_types)

        self.logger.info(f"OpenStreetMap 검색: {activity_type} (위도: {lat}, 경도: {lon}, 반경: {radius}m)")

        result = await self._make_request(query)
        places = []

        for element in result.get("elements", []):
            try:
                place = self._parse_element(element)
                if place:
                    places.append(place)
            except Exception as e:
                self.logger.warning(f"장소 파싱 실패: {str(e)}")
                continue

        self.logger.info(f"검색 완료: {len(places)}개 장소 발견")
        return places[:20]  # 최대 20개로 제한

    def _parse_element(self, element: Dict) -> Optional[Dict]:
        """OSM 요소를 파싱하여 장소 정보를 추출합니다."""
        tags = element.get("tags", {})

        # 이름이 없는 장소는 제외
        name = tags.get("name")
        if not name:
            return None

        # 폐업한 가게 필터링
        if self._is_closed_business(tags):
            return None

        # 좌표 추출
        if element["type"] == "node":
            lat = element.get("lat")
            lon = element.get("lon")
        elif element["type"] == "way" and "geometry" in element:
            # way의 경우 중심점 계산
            geometry = element["geometry"]
            if geometry:
                lat = sum(point["lat"] for point in geometry) / len(geometry)
                lon = sum(point["lon"] for point in geometry) / len(geometry)
            else:
                return None
        else:
            return None

        # 장소 정보 구성
        place = {
            "id": element.get("id"),
            "name": name,
            "lat": lat,
            "lon": lon,
            "type": self._determine_place_type(tags),
            "description": self._create_description(tags),
            "opening_hours": tags.get("opening_hours"),
            "website": tags.get("website"),
            "phone": tags.get("phone"),
            "address": self._extract_address(tags),
        }

        return place

    def _is_closed_business(self, tags: Dict) -> bool:
        """폐업한 가게인지 확인합니다."""
        # 폐업 관련 태그들
        closed_indicators = [
            "disused:",
            "abandoned:",
            "demolished:",
            "former:",
            "historic:",
        ]
        
        # 폐업 관련 값들
        closed_values = [
            "disused",
            "abandoned", 
            "demolished",
            "closed",
            "former",
            "no",
        ]
        
        # 태그 키에 폐업 관련 접두사가 있는지 확인
        for key in tags.keys():
            for indicator in closed_indicators:
                if key.startswith(indicator):
                    return True
        
        # 특정 태그 값들 확인
        for key, value in tags.items():
            if isinstance(value, str):
                value_lower = value.lower()
                for closed_value in closed_values:
                    if closed_value in value_lower:
                        return True
        
        # opening_hours가 "closed" 또는 빈 값인 경우
        opening_hours = tags.get("opening_hours", "").lower()
        if opening_hours in ["closed", "off", "none"]:
            return True
            
        return False

    def _determine_place_type(self, tags: Dict) -> str:
        """태그를 기반으로 장소 타입을 결정합니다."""
        if tags.get("amenity"):
            return tags["amenity"]
        elif tags.get("leisure"):
            return tags["leisure"]
        elif tags.get("tourism"):
            return tags["tourism"]
        elif tags.get("shop"):
            return tags["shop"]
        else:
            return "unknown"

    def _create_description(self, tags: Dict) -> str:
        """태그 정보를 기반으로 설명을 생성합니다."""
        description_parts = []

        # 주요 카테고리
        if tags.get("amenity"):
            description_parts.append(f"편의시설: {tags['amenity']}")
        if tags.get("leisure"):
            description_parts.append(f"여가시설: {tags['leisure']}")
        if tags.get("tourism"):
            description_parts.append(f"관광지: {tags['tourism']}")
        if tags.get("shop"):
            description_parts.append(f"상점: {tags['shop']}")

        # 추가 정보
        if tags.get("cuisine"):
            description_parts.append(f"요리: {tags['cuisine']}")
        if tags.get("wifi") == "yes":
            description_parts.append("WiFi 제공")

        return " | ".join(description_parts) if description_parts else "정보 없음"

    def _extract_address(self, tags: Dict) -> Optional[str]:
        """주소 정보를 추출합니다."""
        address_parts = []

        for key in ["addr:full", "addr:street", "addr:housenumber", "addr:city", "addr:postcode"]:
            if tags.get(key):
                address_parts.append(tags[key])

        return " ".join(address_parts) if address_parts else None

    async def close(self):
        """세션을 정리합니다."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
