from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Схемы для Item
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Схемы для User
class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Схемы для Movie
class MovieBase(BaseModel):
    title: str
    year: int
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    views: Optional[int] = 0
    source_url: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    rating: Optional[float] = None
    is_active: Optional[bool] = True
    channel_id: Optional[int] = None  # Make channel_id optional
    rutube_video_id: Optional[str] = None  # Add rutube_video_id to base schema


class MovieCreate(MovieBase):
    pass


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    year: Optional[int] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    views: Optional[int] = None
    source_url: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    rating: Optional[float] = None
    is_active: Optional[bool] = None
    channel_added_at: Optional[datetime] = None
    channel_id: Optional[int] = None
    rutube_video_id: Optional[str] = None


class Movie(MovieBase):
    id: int
    added_at: Optional[datetime] = None
    channel_added_at: Optional[datetime] = None
    channel: Optional["Channel"] = None

    class Config:
        from_attributes = True


# Схемы для Channel
class ChannelBase(BaseModel):
    rutube_id: str
    title: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = True


class ChannelCreate(ChannelBase):
    pass


class ChannelUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


class Channel(ChannelBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Схемы для Playlist
class PlaylistBase(BaseModel):
    rutube_id: str
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = True


class PlaylistCreate(PlaylistBase):
    pass


class PlaylistUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class Playlist(PlaylistBase):
    id: int
    created_at: Optional[datetime] = None
    videos_count: Optional[int] = 0  # Number of videos in playlist

    class Config:
        from_attributes = True


# Response schemas for endpoints
class PlaylistWithVideosCount(BaseModel):
    id: int
    title: str
    image_url: Optional[str] = None
    videos_count: int

    class Config:
        from_attributes = True


class ChannelWithVideosCount(BaseModel):
    id: int
    title: str
    avatar_url: Optional[str] = None
    videos_count: int

    class Config:
        from_attributes = True