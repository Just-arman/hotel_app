from fastapi import HTTPException, status


class BaseException(HTTPException):
    status_code = 500
    detail = "" # Можно не указывать комментарий, потому что для статуса 500 
                # по умолчанию отображается комментарий "Internal server error"
    
    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(BaseException):
    status_code=status.HTTP_409_CONFLICT
    detail="Пользователь уже зарегистрирован в системе"
        
class IncorrectEmailOrPasswordException(BaseException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Неверная почта или пароль"
        
class TokenExpiredException(BaseException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Срок действия токена истек"
        
class TokenAbsentException(BaseException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Токен отсутствует"
        
class IncorrectTokenFormatException(BaseException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Неверный формат токена"

class IncorrectTokenTypeException(BaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный тип токена"
        
class UserIsNotPresentException(BaseException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Указаны некорректные данные пользователя"

class UserNotFoundByIDException(BaseException):
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Не найден пользователь с таким ID'

class UserIsNotAdminException(BaseException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Недостаточно прав для выполнения данного действия"

class HotelNotFound(BaseException):
    status_code=status.HTTP_409_CONFLICT
    detail="Отель не найден"

class RoomFullyBooked(BaseException):
    status_code=status.HTTP_409_CONFLICT
    detail="Не осталось свободных номеров"

class RoomCannotBeBooked(BaseException):
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    detail="Не удалось забронировать номер ввиду неизвестной ошибки"

class DateFromCannotBeAfterDateTo(BaseException):
    status_code=status.HTTP_400_BAD_REQUEST
    detail="Дата заезда не может быть позже даты выезда"

class CannotBookHotelForLongPeriod(BaseException):
    status_code=status.HTTP_400_BAD_REQUEST
    detail="Невозможно забронировать отель сроком более месяца"

class CannotAddDataToDatabase(BaseException):
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    detail="Не удалось добавить запись"

class CannotProcessCSV(BaseException):
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    detail="Не удалось обработать CSV файл"

