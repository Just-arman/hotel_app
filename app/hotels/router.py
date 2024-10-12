import asyncio
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta
from typing import List, Optional
import aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi import APIRouter, Depends, FastAPI, Query
from fastapi_cache.decorator import cache
from pydantic import TypeAdapter, parse_obj_as
import pydantic
import redis
from app.config import settings
from app.bookings.schemas import SBooking
from app.exceptions import CannotBookHotelForLongPeriod, DateFromCannotBeAfterDateTo, HotelNotFound
from app.hotels.dao import HotelDAO
from app.hotels.schemas import SHotel, SHotelInfo


router = APIRouter(
    prefix="/hotels", 
    tags=["Отели"],
)


@router.get("/{location}")
@cache(expire=30)
async def get_hotels_by_location_and_time(
    location: str,
    date_from: date = Query(..., description=f"Например, {datetime.now().date()}"),
    date_to: date = Query(..., description=f"Например, {(datetime.now() + timedelta(days=14)).date()}"),
):
    await asyncio.sleep(3)
    hotels = await HotelDAO.find_all(location, date_from, date_to)
    hotels_json = TypeAdapter(List[SHotelInfo]).validate_python(hotels)
    # hotels_json = parse_obj_as(List[SHotelInfo], hotels)
    return hotels_json



@router.get("/id/{hotel_id}", include_in_schema=True)
async def get_hotel_by_id(
    hotel_id: int,
) -> Optional[SHotel]:
    return await HotelDAO.find_one_or_none(id=hotel_id)


    

