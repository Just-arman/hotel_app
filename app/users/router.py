from fastapi import APIRouter, Depends, HTTPException, Path, Response
from app.exceptions import (
    CannotAddDataToDatabase, 
    UserAlreadyExistsException, 
    UserIsNotPresentException, 
    UserNotFoundByIDException
)
from app.users.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash
)
from app.users.dao import RolesDAO, UsersDAO
from app.users.dependencies import get_current_admin_user, get_current_user
from app.users.models import Users
from app.users.schemas import (
    SAuthResponse, 
    SRoleUpdateByID, 
    SUserAuth, 
    SUserRead, 
    SUserRegister, 
    SUserRoleUpdate
)


router_auth = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

router_users = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)

@router_auth.post("/register")
async def register_user(user_data: SUserRegister):
    existing_user_email = await UsersDAO.find_one_or_none(email=user_data.email)
    if existing_user_email:
        raise UserAlreadyExistsException

    existing_user_phone = await UsersDAO.find_one_or_none(phone_number=user_data.phone_number)
    if existing_user_phone:
        raise UserAlreadyExistsException
    
    user_data_dict = user_data.model_dump()
    del user_data_dict['confirm_password']   # не нужно хранить в БД
    user_data_dict['hashed_password'] = get_password_hash(user_data_dict.pop('password'))
    
    new_user = await UsersDAO.add(**user_data_dict)
    if not new_user:
        raise CannotAddDataToDatabase
    return {'message': 'Вы успешно зарегистрированы!'}


@router_auth.post("/login")
async def login_user(response: Response, user_data: SUserAuth):
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise UserIsNotPresentException
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("booking_access_token", access_token, httponly=True)
    return SAuthResponse(
        ok=True,
        message=f'Авторизация прошла успешно! Здравствуйте, {user.first_name}'
    )


@router_auth.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("booking_access_token")    


@router_users.get("/me")
async def read_users_me(current_user: Users = Depends(get_current_user)) -> SUserRead:
    return SUserRead.model_validate(current_user)


@router_users.get("/all")
async def read_users_all(current_user: Users = Depends(get_current_admin_user)) -> list[SUserRead]:
    users = await UsersDAO.find_all()
    return [SUserRead.model_validate(user) for user in users]


@router_users.patch("/{user_id}/role", summary="Изменить роль пользователя. Вправе только админы.")
async def update_user_role(
    role_data: SUserRoleUpdate,
    user_id: int = Path(gt=0),
    # user_data: Users = Depends(get_current_admin_user),
    user_data: Users = Depends(get_current_user),
):
    """
    Меняет роль пользователя по названию роль. 
    """
    # 1. Получаем роль по name
    # if role_data.name is not None: здесь эта проверка не выполняется,
    # поскольку проверка и фильтрация пустых и приравненных к ним значений
    # у нас обработано валидатором в схеме SUserRoleUpdate
    role = await RolesDAO.find_one_or_none(name=role_data.name)
    if not role:
        raise HTTPException(status_code=404, detail="Роль с таким названием не найдена")

    # 2. Получаем пользователя
    user = await UsersDAO.find_one_or_none(id=user_id)
    if not user:
        raise UserNotFoundByIDException

    # 3. Проверка на то, есть ли уже у пользователя роль, которую хотим присвоить
    if user.role_id == role.id:
        return {"message": "Пользователь уже имеет данную роль"}

    # 4. Обновляем роль
    values = SRoleUpdateByID(role_id=role.id)
    await UsersDAO.update(values=values, id=user_id)
    return {"message": f"Роль пользователя обновлена на {role.name}"}