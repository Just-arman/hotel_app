from datetime import date
from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import TypeAdapter
from fastapi_versioning import version
from fastapi_cache.decorator import cache
from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBooking, SBookingInfo, SNewBooking
from app.exceptions import RoomCannotBeBooked
from app.tasks.tasks import send_booking_confirmation_email
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
)


@router.get("")
async def get_bookings(user: Users = Depends(get_current_user)) -> list[SBookingInfo]:
    return await BookingDAO.find_all(user_id=user.id)


@router.post("")
@cache(expire=30)
async def add_booking(
    room_id: int, date_from: date, date_to: date,
    # background_tasks: BackgroundTasks,
    user: Users = Depends(get_current_user),
):  
    # print(type(user), "======================")
    booking = await BookingDAO.add(
        user.id,
        room_id,
        date_from,
        date_to,
    )
    if not booking:
        raise RoomCannotBeBooked
    # TypeAdapter и model_dump - это новинки новой версии Pydantic 2.0
    booking_dict = TypeAdapter(SNewBooking).validate_python(booking).model_dump()
    # Celery - отдельная библиотека
    send_booking_confirmation_email.delay(booking_dict, user.email)
    # Background Tasks - встроено в FastAPI
    # background_tasks.add_task(send_booking_confirmation_email, booking, user.email)
    return booking_dict


@router.delete("/{booking_id}")
# @version(1)
async def remove_booking(
    booking_id: int,
    current_user: Users = Depends(get_current_user),
):
    await BookingDAO.delete(id=booking_id, user_id=current_user.id)