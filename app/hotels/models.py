from typing import TYPE_CHECKING
from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.database import Base


# Убирает предупреждения отсутствия импорта
if TYPE_CHECKING:
    from hotels.rooms.models import Rooms


class Hotels(Base):
    __tablename__ = "hotels"

    name: Mapped[str]
    location: Mapped[str]
    services: Mapped[list[str]] = mapped_column(JSON)
    rooms_quantity: Mapped[int]
    image_id: Mapped[int]
    
    rooms: Mapped[list["Rooms"]] = relationship(back_populates="hotel")

    def __str__(self):
        return f"Отель {self.name} {self.location[:30]}"

