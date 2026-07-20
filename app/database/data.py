from sqlalchemy import BigInteger, Column, String, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from datetime import datetime
import pytz

from config import sqlalchemy_url


#Все названия отвечают сами за себя
engine = create_async_engine(sqlalchemy_url)

async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    tg_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, default='unspecified_username')
    date_started = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Krasnoyarsk')))
    notify_vk = Column(Boolean, default=False)
    quick_menu = Column(Boolean, default=False)
    requests_ai: Mapped[int] = mapped_column(default=35)
    refresh_token: Mapped[str] = mapped_column(default='None')
    access_token: Mapped[str] = mapped_column(default='None')
    shift: Mapped[int] = mapped_column(default=1)
    extended_diary = Column(Boolean, default=False)
    tester = Column(Boolean, default=False)
    notify_diary: Mapped[bool] = mapped_column(default=False)
    allow_valentines: Mapped[bool] = mapped_column(default=True) 


class Admin(Base):
    __tablename__ = 'admins'

    tg_id = Column(BigInteger, primary_key=True, unique=True, nullable=False)
    username = Column(String, nullable=False)


class Images(Base):
    __tablename__ = 'images'

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, nullable=False)
    image_id: Mapped[str] = mapped_column(unique=False)
    image_name: Mapped[str] = mapped_column()


class Advert(Base):
    __tablename__ = 'advert'

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    title: Mapped[str] = mapped_column(default='Без заголовка')
    description: Mapped[str] = mapped_column(default='Без описания')
    file_id: Mapped[str] = mapped_column()
    date_created = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Krasnoyarsk')))


class ReportTicket(Base):
    __tablename__ = 'reportticket'

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    from_username: Mapped[str] = mapped_column(default='unknown')
    from_id: Mapped[int] = mapped_column(BigInteger)
    closed: Mapped[bool] = mapped_column(Boolean, default=False)
    topic: Mapped[str] = mapped_column()


class Valentines(Base):
    __tablename__ = 'valentines'

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    receiver_id: Mapped[str] = mapped_column()
    sender_id: Mapped[int] = mapped_column(BigInteger)
    message: Mapped[str] = mapped_column()
    is_read: Mapped[bool] = mapped_column(default=False)
    may_react: Mapped[bool] = mapped_column(default=True)


class InprocessValentines(Base):
    __tablename__ = 'in_process_valentines'

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    receiver_username: Mapped[int] = mapped_column(BigInteger)
    sender_id: Mapped[int] = mapped_column(BigInteger)
    message: Mapped[str] = mapped_column()
    is_read: Mapped[bool] = mapped_column(default=False)


class StringsUI(Base):
    __tablename__ = 'strings_ui'

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    text: Mapped[str] = mapped_column()



async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
