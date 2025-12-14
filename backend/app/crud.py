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
        .filter(models.Movie.year == year, models.Movie.is_active)
        .offset(skip)
        .limit(limit)
    )
    movies = result.scalars().all()
    return movies


async def get_movies_by_genre(db: AsyncSession, genre: str, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.Movie)
        .filter(models.Movie.genre == genre, models.Movie.is_active)
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


# CRUD операции для Channel
async def get_channel(db: AsyncSession, channel_id: int):
    result = await db.execute(select(models.Channel).filter(models.Channel.id == channel_id))
    return result.scalar_one_or_none()


async def get_channels(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.Channel)
        .filter(models.Channel.is_active)
        .offset(skip)
        .limit(limit)
    )
    channels = result.scalars().all()
    return channels


async def get_channel_by_rutube_id(db: AsyncSession, rutube_id: str):
    result = await db.execute(select(models.Channel).filter(models.Channel.rutube_id == rutube_id))
    return result.scalar_one_or_none()


async def create_channel(db: AsyncSession, channel: schemas.ChannelCreate):
    db_channel = models.Channel(**channel.model_dump())
    db.add(db_channel)
    await db.commit()
    await db.refresh(db_channel)
    return db_channel


async def update_channel(db: AsyncSession, channel_id: int, channel_update: schemas.ChannelUpdate):
    db_channel = await get_channel(db, channel_id)
    if db_channel:
        update_data = channel_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_channel, field, value)
        await db.commit()
        await db.refresh(db_channel)
        return db_channel
    return None


# CRUD операции для Playlist
async def get_playlist(db: AsyncSession, playlist_id: int):
    result = await db.execute(select(models.Playlist).filter(models.Playlist.id == playlist_id))
    return result.scalar_one_or_none()


async def get_playlists(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.Playlist)
        .filter(models.Playlist.is_active)
        .offset(skip)
        .limit(limit)
    )
    playlists = result.scalars().all()
    return playlists


async def get_playlist_by_rutube_id(db: AsyncSession, rutube_id: str):
    result = await db.execute(select(models.Playlist).filter(models.Playlist.rutube_id == rutube_id))
    return result.scalar_one_or_none()


async def create_playlist(db: AsyncSession, playlist: schemas.PlaylistCreate):
    db_playlist = models.Playlist(**playlist.model_dump())
    db.add(db_playlist)
    await db.commit()
    await db.refresh(db_playlist)
    return db_playlist


async def update_playlist(db: AsyncSession, playlist_id: int, playlist_update: schemas.PlaylistUpdate):
    db_playlist = await get_playlist(db, playlist_id)
    if db_playlist:
        update_data = playlist_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_playlist, field, value)
        await db.commit()
        await db.refresh(db_playlist)
        return db_playlist
    return None


# Функции для работы с фильмами в плейлистах
async def get_playlist_movies(db: AsyncSession, playlist_id: int, skip: int = 0, limit: int = 24, channel_id: int = None):
    query = select(models.Movie).join(models.PlaylistMovie).filter(models.PlaylistMovie.playlist_id == playlist_id)

    if channel_id:
        query = query.filter(models.Movie.channel_id == channel_id)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    movies = result.scalars().all()
    return movies


async def get_playlist_movies_with_channel_filter(db: AsyncSession, playlist_id: int, channel_id: int = None,
                                                skip: int = 0, limit: int = 24, order_by: str = "-channel_added_at"):
    query = select(models.Movie).join(models.PlaylistMovie).filter(models.PlaylistMovie.playlist_id == playlist_id).join(models.Channel, models.Movie.channel_id == models.Channel.id, isouter=True)

    if channel_id:
        query = query.filter(models.Movie.channel_id == channel_id)

    # Apply ordering
    if order_by == "-channel_added_at":
        query = query.order_by(models.Movie.channel_added_at.desc())
    elif order_by == "channel_added_at":
        query = query.order_by(models.Movie.channel_added_at.asc())

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    movies = result.scalars().all()
    return movies


async def get_playlist_videos_count(db: AsyncSession, playlist_id: int, channel_id: int = None):
    query = select(models.Movie).join(models.PlaylistMovie).filter(models.PlaylistMovie.playlist_id == playlist_id)

    if channel_id:
        query = query.filter(models.Movie.channel_id == channel_id)

    result = await db.execute(query)
    movies = result.scalars().all()
    return len(movies)


async def get_all_movies_with_channel_filter(db: AsyncSession, playlist_id: int = None, channel_id: int = None,
                                           skip: int = 0, limit: int = 24, order_by: str = "-channel_added_at"):
    query = select(models.Movie)

    if playlist_id:
        query = query.join(models.PlaylistMovie).filter(models.PlaylistMovie.playlist_id == playlist_id)

    if channel_id:
        query = query.filter(models.Movie.channel_id == channel_id)

    # Apply ordering
    if order_by == "-channel_added_at":
        query = query.order_by(models.Movie.channel_added_at.desc())
    elif order_by == "channel_added_at":
        query = query.order_by(models.Movie.channel_added_at.asc())

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    movies = result.scalars().all()
    return movies


# CRUD операции для связей между плейлистами и фильмами
async def add_movie_to_playlist(db: AsyncSession, playlist_id: int, movie_id: int):
    playlist_movie = models.PlaylistMovie(playlist_id=playlist_id, movie_id=movie_id)
    db.add(playlist_movie)
    await db.commit()
    return playlist_movie


async def get_movies_by_channel(db: AsyncSession, channel_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.Movie)
        .filter(models.Movie.channel_id == channel_id, models.Movie.is_active)
        .offset(skip)
        .limit(limit)
    )
    movies = result.scalars().all()
    return movies


async def get_channels_with_videos_count(db: AsyncSession, skip: int = 0, limit: int = 100):
    from sqlalchemy import func
    result = await db.execute(
        select(
            models.Channel.id,
            models.Channel.title,
            models.Channel.avatar_url,
            func.count(models.Movie.id).label('videos_count')
        )
        .join(models.Movie, models.Channel.id == models.Movie.channel_id)
        .filter(models.Channel.is_active, models.Movie.is_active)
        .group_by(models.Channel.id, models.Channel.title, models.Channel.avatar_url)
        .offset(skip)
        .limit(limit)
    )
    channels_data = result.all()

    channels = []
    for channel_data in channels_data:
        channel = schemas.ChannelWithVideosCount(
            id=channel_data.id,
            title=channel_data.title,
            avatar_url=channel_data.avatar_url,
            videos_count=channel_data.videos_count
        )
        channels.append(channel)

    return channels


async def get_playlists_with_videos_count(db: AsyncSession, skip: int = 0, limit: int = 100):
    from sqlalchemy import func
    result = await db.execute(
        select(
            models.Playlist.id,
            models.Playlist.title,
            models.Playlist.image_url,
            func.count(models.PlaylistMovie.movie_id).label('videos_count')
        )
        .join(models.PlaylistMovie, models.Playlist.id == models.PlaylistMovie.playlist_id)
        .join(models.Movie, models.PlaylistMovie.movie_id == models.Movie.id)
        .filter(models.Playlist.is_active, models.Movie.is_active)
        .group_by(models.Playlist.id, models.Playlist.title, models.Playlist.image_url)
        .offset(skip)
        .limit(limit)
    )
    playlists_data = result.all()

    playlists = []
    for playlist_data in playlists_data:
        playlist = schemas.PlaylistWithVideosCount(
            id=playlist_data.id,
            title=playlist_data.title,
            image_url=playlist_data.image_url,
            videos_count=playlist_data.videos_count
        )
        playlists.append(playlist)

    return playlists