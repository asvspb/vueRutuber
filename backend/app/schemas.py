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
    image_url: str
    thumbnail_url: Optional[str] = None
    views: Optional[int] = 0
    source_url: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    rating: Optional[float] = None
    is_active: Optional[bool] = True


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


class Movie(MovieBase):
    id: int
    added_at: Optional[datetime] = None

    class Config:
        from_attributes = True