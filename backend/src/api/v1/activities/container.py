from dependency_injector import containers, providers

from api.v1.activities.formatters import ResponseFormatter
from api.v1.activities.services import ActivityService, PlaceService, RecommendationService, WeatherService
from api.v1.activities.services.weather_match_service import WeatherMatchService
from infrastructure.external.openstreetmap_client import OpenStreetMapClient


class ActivitiesContainer(containers.DeclarativeContainer):
    """Activities 모듈의 의존성 주입 컨테이너"""

    # Configuration
    config = providers.Configuration()

    # Logger
    logger = providers.Object("")

    # Infrastructure dependencies (from main container)
    postgres_engine = providers.Object("")
    redis_client = providers.Object("")
    rabbitmq_connection = providers.Object("")

    # External clients

    osm_client = providers.Singleton(OpenStreetMapClient, logger=logger)
    # Business logic services
    weather_service = providers.Singleton(WeatherService, config=config)
    weather_match_service = providers.Singleton(WeatherMatchService)
    place_service = providers.Singleton(PlaceService, osm_client=osm_client)

    activity_service = providers.Singleton(ActivityService)

    # Presentation layer
    response_formatter = providers.Singleton(ResponseFormatter)

    # Application service (orchestration)
    recommendation_service = providers.Singleton(
        RecommendationService,
        weather_service=weather_service,
        place_service=place_service,
        activity_service=activity_service,
        response_formatter=response_formatter,
        weather_match_service=weather_match_service,
    )
