from typing import TYPE_CHECKING
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.database import Base, str_uniq


# Убирает предупреждения отсутствия импорта
if TYPE_CHECKING:
    from bookings.models import Bookings


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    phone_number: Mapped[str_uniq]
    email: Mapped[str_uniq]
    hashed_password: Mapped[str]
    role: Mapped[str] = mapped_column(default="user", server_default="user")

    bookings: Mapped[list["Bookings"]] = relationship(back_populates="user")

    def __str__(self):
        return f"Пользователь {self.email}"