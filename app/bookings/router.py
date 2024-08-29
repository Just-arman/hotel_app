from datetime import date
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from pydantic import TypeAdapter

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


@router.get("/")
async def get_bookings(
    user: Users = Depends(get_current_user)
) -> List[SBookingInfo]:
    return await BookingDAO.find_all(user_id=user.id)


@router.post("/")
async def add_booking(
    background_tasks: BackgroundTasks,
    room_id: int, 
    date_from: date, 
    date_to: date,
    user: Users = Depends(get_current_user)
):
    booking = await BookingDAO.add(
        user.id, 
        room_id, 
        date_from, 
        date_to)
    booking_dict = SBooking.model_validate(booking).model_dump()
    # вариант с selery
    send_booking_confirmation_email.delay(booking_dict, user.email)
    # вариант встроенный background tasks
    background_tasks.add_task(send_booking_confirmation_email, booking_dict, user.email)
    return booking_dict


@router.delete("/{booking_id}")
async def remove_booking(
    booking_id: int,
    current_user: Users = Depends(get_current_user),
):
    await BookingDAO.delete(id=booking_id, user_id=current_user.id)