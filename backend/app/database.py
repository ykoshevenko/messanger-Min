from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pydantic import BaseModel
from sqlalchemy import select

class User(BaseModel):
    username: str
    password: str

engine = create_async_engine('postgresql+asyncpg://user:password@localhost/dbname')

new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = 'Users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    password: Mapped[str]

async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def add_user(data: User, session):
    new_user = UserModel(
        username=data.username,
        password=data.password
    )

    session.add(new_user)
    await session.commit()
    return {'status': 200}

async def get_user_by_username(username: str, session: AsyncSession):
    query = select(UserModel).where(UserModel.username == username)
    result = await session.execute(query)
    return result.scalar_one_or_none()