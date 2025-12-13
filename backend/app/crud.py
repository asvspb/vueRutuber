from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas


# CRUD операции для Item
async def get_item(db: AsyncSession, item_id: int):
    result = await db.execute(select(models.Item).filter(models.Item.id == item_id))
    return result.scalar_one_or_none()


async def get_items(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Item).offset(skip).limit(limit))
    items = result.scalars().all()
    return items


async def create_item(db: AsyncSession, item: schemas.ItemCreate):
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


# CRUD операции для User
async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    return result.scalar_one_or_none()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


# CRUD операции для Movie
async def get_movie(db: AsyncSession, movie_id: int):
    result = await db.execute(select(models.Movie).filter(models.Movie.id == movie_id))
    return result.scalar_one_or_none()


async def get_movies(db: AsyncSession, skip: int = 0, limit: int = 100, is_active: bool = True):
    result = await db.execute(
        select(models.Movie)
        .filter(models.Movie.is_active == is_active)
        .offset(skip)
        .limit(limit)
    )
    movies = result.scalars().all()
    return movies


async def get_movies_by_year(db: AsyncSession, year: int, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.Movie)
        .filter(models.Movie.year == year, models.Movie.is_active == True)
        .offset(skip)
        .limit(limit)
    )
    movies = result.scalars().all()
    return movies


async def get_movies_by_genre(db: AsyncSession, genre: str, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.Movie)
        .filter(models.Movie.genre == genre, models.Movie.is_active == True)
        .offset(skip)
        .limit(limit)
    )
    movies = result.scalars().all()
    return movies


async def create_movie(db: AsyncSession, movie: schemas.MovieCreate):
    db_movie = models.Movie(**movie.model_dump())
    db.add(db_movie)
    await db.commit()
    await db.refresh(db_movie)
    return db_movie


async def update_movie(db: AsyncSession, movie_id: int, movie_update: schemas.MovieUpdate):
    db_movie = await get_movie(db, movie_id)
    if db_movie:
        update_data = movie_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_movie, field, value)
        await db.commit()
        await db.refresh(db_movie)
        return db_movie
    return None


async def delete_movie(db: AsyncSession, movie_id: int):
    db_movie = await get_movie(db, movie_id)
    if db_movie:
        db_movie.is_active = False  # Логическое удаление
        await db.commit()
        return db_movie
    return None


async def increment_movie_views(db: AsyncSession, movie_id: int):
    db_movie = await get_movie(db, movie_id)
    if db_movie:
        db_movie.views += 1
        await db.commit()
        await db.refresh(db_movie)
        return db_movie
    return None