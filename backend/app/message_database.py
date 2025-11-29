from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped, ForeignKey

engine = create_engine('sqlite:///./message.db')

new_session = sessionmaker(engine, expire_on_commit=False)

def get_session():
    with new_session() as session:
        yield session

class Base(DeclarativeBase):
    pass

class MessageModel(Base):
    __table__ = 'Message'
    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    recipient_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    content: Mapped[str]