from enum import Enum


class TableName(str, Enum):
    hotels = "hotels"
    rooms = "rooms"
    bookings = "bookings"