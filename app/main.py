import asyncio
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta
import time
import sentry_sdk
from typing import AsyncIterator, List, Optional
from fastapi_versioning import VersionedFastAPI
from fastapi import APIRouter, Depends, FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from fastapi_versioning import VersionedFastAPI
from pydantic import BaseModel, TypeAdapter, parse_obj_as
from redis import asyncio as aioredis
from sqladmin import Admin, ModelView
from prometheus_fastapi_instrumentator import Instrumentator

from app.admin.auth import authentication_backend
from app.admin.views import BookingsAdmin, HotelsAdmin, RoomsAdmin, UsersAdmin
from app.bookings.router import router as router_bookings
from app.config import settings
from app.database import engine
from app.exceptions import CannotBookHotelForLongPeriod, DateFromCannotBeAfterDateTo
from app.hotels.dao import HotelDAO
from app.hotels.rooms.router import router as router_rooms
from app.hotels.router import router as router_hotels
from app.hotels.schemas import SHotelInfo
from app.images.router import router as router_images
from app.pages.router import router as router_pages
from app.importer.router import router as router_import
from app.users.models import Users
from app.users.router import router_auth, router_users
from app.logger import logger

app = FastAPI()

# sentry_sdk.init(
    # dsn=f"https://{settings.SENTRY_DSN}",
    # traces_sample_rate=1.0,
    # profiles_sample_rate=1.0,
# )

# async def get_data():
    # data = await asyncio.sleep(3)

# async def get_cache():
    # while True:
        # await get_data()
        # await asyncio.sleep(60*5)


    # Для кэширования без redis
#@asynccontextmanager
#async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    #FastAPICache.init(InMemoryBackend())
    #yield


    # Подключение redis
@asynccontextmanager
async def lifespan(_: FastAPI):
    redis = aioredis.from_url(
        url=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        encoding="utf8",
        decode_responses=True,
    )
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    yield

    # Подключение redis
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # при запуске
#     redis = aioredis.from_url(
#         "redis://redis:6379",
#         encoding="utf8",
#         decode_responses=True,
#     )
#     # await redis.set("key", "value")
#     # logger.warning(await redis.get("key"))
#     FastAPICache.init(RedisBackend(redis), prefix="cache")
#     # await get_data()
#     # asyncio.create_task(get_cache())
#     yield
#     # при выключении


router = APIRouter(
    prefix="/hotels", 
    tags=["Отели"],
)

    # Подключаем роутеры
app.include_router(router_auth)
app.include_router(router_users)
app.include_router(router_hotels)
app.include_router(router_rooms)
app.include_router(router_bookings)
app.include_router(router_pages)
app.include_router(router_images)
app.include_router(router_import)



    # Настройки CORS
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", 
                   "Access-Control-Allow-Origin",
                   "Authorization"],
)


    # Версионирование API
app = VersionedFastAPI(app,
    version_format='{major}',
    prefix_format='/v{major}',
    lifespan=lifespan,
    # description='Greet users with a nice message',
    # middleware=[
        # Middleware(SessionMiddleware, secret_key='mysecretkey')
    # ]
)

    # Подключение сбора метрик
instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"]
)
Instrumentator().instrument(app).expose(app)

    # Подключение админки
admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(UsersAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)
admin.add_view(BookingsAdmin)

    # Статические файлы
app.mount("/static", StaticFiles(directory="app/static"), "static")


    # Middleware для замера времени запросов
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)# 
    process_time = time.time() - start_time
    logger.info("Request handling time", extra={
        "process_time": round(process_time, 4)
    })
    return response
