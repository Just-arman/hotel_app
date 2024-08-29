from datetime import date
from typing import List, Optional

from fastapi import Query
from pydantic import BaseModel, ConfigDict


class SHotel(BaseModel):
    id: int
    name: str
    location: str
    services: List[str]
    rooms_quantity: int
    image_id: int

    # orm_mode поменял название во 2 версии Pydantic
    model_config = ConfigDict(from_attributes=True)


class SHotelInfo(SHotel):
    rooms_left: int

    # orm_mode поменял название во 2 версии Pydantic
    model_config = ConfigDict(from_attributes=True)


class HotelsSearchArgs:
    def __init__(
        self,
        location: str,
        date_from: date,
        date_to: date,
        has_spa: Optional[bool] = None,
        stars: Optional[int] = Query(None, ge=1, le=5)
    ):
        self.location = location
        self.date_from = date_from
        self.date_to = date_to
        self.has_spa = has_spa
        self.stars = stars