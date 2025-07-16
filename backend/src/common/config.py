from os import environ

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    PROJECT_NAME: str = "Feed Service"
    VERSION: str = "0.1.0"

    # Postgresql
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_HOST: str = ""
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = ""

    # Redis
    REDIS_HOST: str = ""
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""

    # RabbitMQ
    RABBITMQ_HOST: str = ""
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = ""
    RABBITMQ_PASSWORD: str = ""

    # Google OAuth2
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = ""

    # OpenWeatherMap
    OPEN_WEATHER_MAP_API_KEY: str = ""
    OPEN_WEATHER_WEATHER_API_URL_2_5: str = (
        "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric&lang=kr"
    )
    OPEN_WEATHER_WEATHER_API_URL_3: str = (
        "https://api.openweathermap.org/data/3.0/onecall?lat={}&lon={}&appid={}&units=metric"
    )
    GEOCODING_API: str = "https://api.openweathermap.org/geo/1.0/direct?q={}&limit=1&appid={}"

    class Config:
        env_file = ".env"


class LocalConfig(Config):
    DEBUG: bool = True
    SQL_PRINT: bool = True

    POSTGRES_SERVER: str = ""
    POSTGRES_SCHEMA: str = "public"

    REDIS_SERVER: str = ""


def conf():
    c = dict(local=LocalConfig)
    return c[environ.get("API_ENV", "local")]()
