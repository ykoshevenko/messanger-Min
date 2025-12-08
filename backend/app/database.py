# app/database.py
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped
from sqlalchemy.sql import func
from datetime import datetime

# Используем одну базу данных
engine = create_engine('sqlite:///./messenger.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = "Users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=func.now())

class MessageModel(Base):
    __tablename__ = "Messages"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    recipient_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    content: Mapped[str]
    timestamp: Mapped[datetime] = mapped_column(default=func.now())

# Вспомогательные функции для auth.py
def get_user_by_username(username: str, session):
    return session.query(UserModel).filter(UserModel.username == username).first()

def add_user(data, session):
    new_user = UserModel(
        username=data.username,
        password=data.password
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

def get_all_users(session):
    return session.query(UserModel).all()

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def setup_database():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")