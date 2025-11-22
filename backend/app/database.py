# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
# from sqlalchemy import select

# # Синхронный движок вместо асинхронного
# engine = create_engine('sqlite:///./data.db')

# # Синхронная сессия
# new_session = sessionmaker(engine, expire_on_commit=False)

# def get_session():
#     with new_session() as session:
#         yield session

# class Base(DeclarativeBase):
#     pass

# class UserModel(Base):
#     __tablename__ = 'Users'
#     id: Mapped[int] = mapped_column(primary_key=True)
#     username: Mapped[str]
#     password: Mapped[str]

# def setup_database():
#     # Создаем все таблицы
#     Base.metadata.create_all(engine)
#     print("Tables created successfully")

# def add_user(data, session):
#     new_user = UserModel(
#         username=data.username,
#         password=data.password
#     )
#     session.add(new_user)
#     session.commit()
#     return {'status': 200}

# def get_user_by_username(username: str, session):
#     query = select(UserModel).where(UserModel.username == username)
#     result = session.execute(query)
#     return result.scalar_one_or_none()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select

# Синхронный движок
engine = create_engine('sqlite:///./data.db')

# Синхронная сессия
new_session = sessionmaker(engine, expire_on_commit=False)

def get_session():
    with new_session() as session:
        yield session

class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = 'Users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    password: Mapped[str]

def setup_database():
    Base.metadata.create_all(engine)
    print("Tables created successfully")

def add_user(data, session):
    new_user = UserModel(
        username=data.username,
        password=data.password
    )
    session.add(new_user)
    session.commit()
    return {'status': 200}

def get_user_by_username(username: str, session):
    query = select(UserModel).where(UserModel.username == username)
    result = session.execute(query)
    return result.scalar_one_or_none()