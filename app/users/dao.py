from app.dao.base import BaseDAO
from app.users.models import Roles, Users


class UsersDAO(BaseDAO):
    model = Users

class RolesDAO(BaseDAO):
    model = Roles