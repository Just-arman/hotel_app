from datetime import date
from typing import List

from app.hotels.rooms.dao import RoomDAO
from app.hotels.rooms.schemas import SRoomInfo
from app.hotels.router import router


@router.get("/{hotel_id}/rooms")
# Этот эндпоинт можно и нужно кэшировать, но этого не сделано, чтобы
# можно было проследить разницу в работе /rooms (без кэша) и /hotels (с кэшем).
async def get_rooms_by_time(
    hotel_id: int,
    date_from: date,
    date_to: date,
) -> List[SRoomInfo]:
    rooms = await RoomDAO.search_for_rooms(hotel_id, date_from, date_to)
    return rooms