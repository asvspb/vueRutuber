from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.sql import func
from .database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)           # Название фильма
    year = Column(Integer)                       # Год выпуска
    image_url = Column(String)                   # URL изображения
    thumbnail_url = Column(String)               # URL миниатюры
    views = Column(Integer, default=0)           # Количество просмотров
    added_at = Column(DateTime, default=func.now()) # Дата добавления
    source_url = Column(String)                  # Исходный URL
    duration = Column(String)                    # Длительность
    description = Column(Text)                   # Описание
    genre = Column(String)                       # Жанр
    rating = Column(Float)                       # Рейтинг
    is_active = Column(Boolean, default=True)    # Активность