import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager

from api.v1.activities.endpoint import router as activities_router
from container import Container

container = Container()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리"""
    # 시작 시 초기화
    yield
    # 종료 시 정리
    try:
        # Activities 컨테이너의 리소스 정리
        activities_container = container.activities_container()
        
        # PlaceService의 세션 정리
        if hasattr(activities_container, 'place_service'):
            place_service = activities_container.place_service()
            if hasattr(place_service, 'close'):
                await place_service.close()
                
    except Exception as e:
        print(f"애플리케이션 종료 중 오류: {e}")


def create_app(_config) -> FastAPI:
    _app = FastAPI(title=_config["PROJECT_NAME"], lifespan=lifespan)

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=("GET", "POST", "PUT", "DELETE"),
        allow_headers=["*"],
    )

    _app.include_router(activities_router, prefix="/api/v1/activities")

    def game_credit_openapi():
        if _app.openapi_schema:
            return _app.openapi_schema
        openapi_schema = get_openapi(
            title=_config["PROJECT_NAME"],
            version=_config["VERSION"],
            routes=_app.routes,
        )
        _app.openapi_schema = openapi_schema
        return _app.openapi_schema

    _app.openapi = game_credit_openapi

    # 컨테이너를 앱에 연결
    _app.container = container

    return _app


app = create_app(container.config())


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
