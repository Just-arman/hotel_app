from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
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
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), default=1, server_default="1")

    role: Mapped["Roles"] = relationship(back_populates="users", lazy="selectin")
    bookings: Mapped[list["Bookings"]] = relationship(back_populates="user")

    def __str__(self):
        return f"Пользователь {self.email}"
    

class Roles(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str_uniq]

    users: Mapped[list["Users"]] = relationship(back_populates="role")
    
    # def __repr__(self):
    #     return f"Roles(name={self.name!r})"

    @property
    def users_list(self):
        users = [f"{user.first_name} {user.last_name}" for user in self.users]
        if len(users) > 5:
            return ", ".join(users[:5]) + f" и ещё {len(users) - 5} польз."
        return ", ".join(users)