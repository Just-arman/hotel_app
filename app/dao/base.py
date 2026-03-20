from typing import ClassVar, Generic, List, Type, TypeVar
from sqlalchemy import delete, insert, select
from sqlalchemy.exc import SQLAlchemyError
from app.database import async_session_maker
from app.logger import log
from app.database import Base


# Объявляем типовой параметр T с ограничением, что это наследник Base
T = TypeVar("T", bound=Base)


class BaseDAO(Generic[T]):
    model: Type[T]

    # для проверки на отсутствие пустых значений модели в дочерних классах
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.model is None:
            raise ValueError(f"В классе {cls.__name__} должна быть указана модель")

    @classmethod
    async def find_by_id(cls, model_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=model_id)
            result = await session.execute(query)
            return result.mappings().one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().one_or_none()
     
    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().all()
        
    @classmethod
    async def add(cls, **data):
        try:
            query = insert(cls.model).values(**data).returning(cls.model.id)
            async with async_session_maker() as session:
                result = await session.execute(query)
                await session.commit()
                return result.mappings().first()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot insert data into table"
            else:
                msg = "Unknown Exc: Cannot insert data into table"

            log.error(msg, extra={"table": cls.model.__tablename__}, exc_info=True)
            return None
    
    @classmethod
    async def delete(cls, **filter_by):
        async with async_session_maker() as session:
            query = delete(cls.model).filter_by(**filter_by)
            await session.execute(query)
            await session.commit()
    

    @classmethod
    async def add_bulk(cls, *data):
        # Для загрузки массива данных [{"id": 1}, {"id": 2}]
        # нужно обрабатывать его через позиционные аргументы *args.
        try:
            query = insert(cls.model).values(*data).returning(cls.model.id)
            async with async_session_maker() as session:
                result = await session.execute(query)
                await session.commit()
                return result.mappings().first()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            else:
                msg = "Unknown Exc"
            msg += ": Cannot bulk insert data into table"

            log.error(msg, extra={"table": cls.model.__tablename__}, exc_info=True)
            return None