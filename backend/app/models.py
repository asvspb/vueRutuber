from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
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
    image_url = Column(String, nullable=True)    # URL изображения (может быть NULL)
    thumbnail_url = Column(String, nullable=True) # URL миниатюры (может быть NULL)
    views = Column(Integer, default=0)           # Количество просмотров
    added_at = Column(DateTime, default=func.now()) # Дата добавления в систему
    channel_added_at = Column(DateTime(timezone=True), nullable=True, index=True) # Дата публикации на Rutube
    source_url = Column(String)                  # Исходный URL
    duration = Column(String)                    # Длительность
    description = Column(Text)                   # Описание
    genre = Column(String)                       # Жанр
    rating = Column(Float)                       # Рейтинг
    is_active = Column(Boolean, default=True)    # Активность

    # Foreign key and relationships for playlists and channels
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)  # FK to channels
    rutube_video_id = Column(String, unique=True, index=True)                # Rutube video ID for idempotency


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, index=True)
    rutube_id = Column(String, unique=True, index=True)  # Rutube playlist ID
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    # Relationship with movies through association table
    movies = relationship("Movie", secondary="playlist_movies", back_populates="playlists")


class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    rutube_id = Column(String, unique=True, index=True)  # Rutube channel ID
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    # Relationship with movies
    movies = relationship("Movie", back_populates="channel")


class PlaylistMovie(Base):
    __tablename__ = "playlist_movies"

    playlist_id = Column(Integer, ForeignKey("playlists.id"), primary_key=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), primary_key=True)


# Update Movie model to include reverse relationships
Movie.playlists = relationship("Playlist", secondary="playlist_movies", back_populates="movies")
Movie.channel = relationship("Channel", back_populates="movies")