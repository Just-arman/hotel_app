from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi_cache.decorator import cache
from fastapi_versioning import version
from pydantic import TypeAdapter

from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBookingInfo, SNewBooking
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
    bookings = await BookingDAO.find_all_with_images(user_id=user.id)
    bookings_list = [SBookingInfo.model_validate(dict(booking)) for booking in bookings]
    return bookings_list


@router.post("")
# @cache(expire=30)
async def add_new_booking(
    booking_data: SNewBooking,
    # background_tasks: BackgroundTasks,
    user: Users = Depends(get_current_user),
):
    booking = await BookingDAO.add_booking(
        user.id,
        booking_data.room_id,
        booking_data.date_from,
        booking_data.date_to,
    )
    if not booking:
        raise RoomCannotBeBooked
    # TypeAdapter и model_dump - это новинки новой версии Pydantic 2.0
    booking_dict = TypeAdapter(SNewBooking).validate_python(booking).model_dump()
    send_booking_confirmation_email.delay(booking_dict, user.email)  # type: ignore[attr-defined]
    # background_tasks.add_task(send_booking_confirmation_email, booking_dict, user.email)
    return booking_dict


@router.delete("/{booking_id}")
# @version(1)
async def remove_booking(
    booking_id: int,
    current_user: Users = Depends(get_current_user),
):
    await BookingDAO.delete(id=booking_id, user_id=current_user.id)