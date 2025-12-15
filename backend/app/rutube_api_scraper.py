"""
Rutube API-based scraper - более надежная альтернатива Selenium
"""
import asyncio
import aiohttp
from datetime import datetime
from app.database import AsyncSessionLocal
from app.models import Movie, Channel, Playlist, PlaylistMovie
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import os


RUTUBE_API_BASE = "https://rutube.ru/api"
CHANNEL_ID = os.getenv("RUTUBE_CHANNEL_ID", "32869212")


async def fetch_channel_videos(limit: int = 100):
    """Deprecated: use fetch_channel_videos_by_id with explicit channel_id."""
    return await fetch_channel_videos_by_id(CHANNEL_ID, limit)

async def fetch_channel_videos_by_id(channel_id: str, limit: int = 100):
    """Получить видео из канала через Rutube API"""
    videos = []
    page = 1
    page_size = 20

    async with aiohttp.ClientSession() as session:
        while len(videos) < limit:
            url = f"{RUTUBE_API_BASE}/video/person/{channel_id}/?page={page}&page_size={page_size}"

            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        print(f"API returned status {response.status}")
                        break

                    data = await response.json()
                    results = data.get('results', [])

                    if not results:
                        break

                    for video in results:
                        if len(videos) >= limit:
                            break

                        video_info = {
                            'title': video.get('title', ''),
                            'url': f"https://rutube.ru/video/{video.get('id', '')}/",
                            'thumbnail_url': video.get('thumbnail_url', ''),
                            'views': video.get('hits', 0),
                            'duration': video.get('duration', 0),
                            'description': video.get('description', ''),
                            'publication_date': video.get('created_ts', ''),
                            'category': video.get('category', {}).get('name', 'Видео'),
                        }
                        videos.append(video_info)

                    page += 1
                    await asyncio.sleep(0.5)  # Rate limiting

            except Exception as e:
                print(f"Error fetching page {page}: {e}")
                break

    return videos


async def fetch_playlist_videos(playlist_id: str, limit: int = 100):
    """Получить видео из плейлиста через Rutube API"""
    videos = []
    page = 1
    page_size = 20

    async with aiohttp.ClientSession() as session:
        while len(videos) < limit:
            # Using the playlist API endpoint
            url = f"{RUTUBE_API_BASE}/video/playlist/{playlist_id}/?page={page}&page_size={page_size}"

            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        print(f"Playlist API returned status {response.status}")
                        # Try alternative endpoint
                        alt_url = f"{RUTUBE_API_BASE}/playlist/{playlist_id}/?page={page}&page_size={page_size}"
                        async with session.get(alt_url, timeout=aiohttp.ClientTimeout(total=30)) as alt_response:
                            if alt_response.status != 200:
                                print(f"Alternative playlist API also failed: {alt_response.status}")
                                break
                            data = await alt_response.json()
                    else:
                        data = await response.json()

                    results = data.get('results', [])

                    if not results:
                        break

                    for video in results:
                        if len(videos) >= limit:
                            break

                        # Extract channel information
                        channel = video.get('person', {}) or video.get('author', {})

                        video_info = {
                            'title': video.get('title', ''),
                            'url': f"https://rutube.ru/video/{video.get('id', '')}/",
                            'thumbnail_url': video.get('thumbnail_url', ''),
                            'views': video.get('hits', 0),
                            'duration': video.get('duration', 0),
                            'description': video.get('description', ''),
                            'publication_date': video.get('created_ts', ''),
                            'category': video.get('category', {}).get('name', 'Видео'),
                            'rutube_video_id': video.get('id', ''),
                            'channel_data': {
                                'rutube_id': str(channel.get('id', '')),
                                'title': channel.get('name', ''),
                                'avatar_url': channel.get('avatar_url', ''),
                            }
                        }
                        videos.append(video_info)

                    page += 1
                    # Rate limiting
                    await asyncio.sleep(0.25)  # Reduced delay for playlist fetching

            except Exception as e:
                print(f"Error fetching playlist page {page}: {e}")
                break

    return videos


async def import_rutube_playlist_videos(db, rutube_playlist_url: str, playlist_id: str, limit: int = 100):
    """Import videos from a Rutube playlist into the database"""
    print(f"Importing videos from playlist {playlist_id} (limit: {limit})")

    # Get or create the playlist
    existing_playlist = await db.execute(
        select(Playlist).where(Playlist.rutube_id == playlist_id)
    )
    playlist = existing_playlist.scalar_one_or_none()

    if not playlist:
        # Create new playlist
        playlist_data = {
            'rutube_id': playlist_id,
            'title': f"Playlist {playlist_id}",
            'description': f"Imported from {rutube_playlist_url}",
            'is_active': True
        }

        playlist = Playlist(**playlist_data)
        db.add(playlist)
        await db.flush()  # Get the ID without committing

    imported_count = 0
    updated_count = 0
    linked_count = 0

    # Fetch videos from the playlist
    videos = await fetch_playlist_videos(playlist_id, limit)

    for video in videos:
        # Get or create channel
        existing_channel = await db.execute(
            select(Channel).where(Channel.rutube_id == video['channel_data']['rutube_id'])
        )
        channel = existing_channel.scalar_one_or_none()

        if not channel:
            channel_data = {
                'rutube_id': video['channel_data']['rutube_id'],
                'title': video['channel_data']['title'],
                'avatar_url': video['channel_data'].get('avatar_url'),
                'is_active': True
            }
            channel = Channel(**channel_data)
            db.add(channel)
            await db.flush()  # Get the ID without committing

        # Get or create movie by rutube_video_id
        existing_movie = await db.execute(
            select(Movie).where(Movie.rutube_video_id == video['rutube_video_id'])
        )
        movie = existing_movie.scalar_one_or_none()

        if movie:
            # Update existing movie
            update_data = {
                'title': video.get('title', movie.title),
                'thumbnail_url': video.get('thumbnail_url', movie.thumbnail_url),
                'views': video.get('views', movie.views),
                'description': video.get('description', movie.description),
                'duration': format_duration(video.get('duration', movie.duration)),
                'genre': video.get('category', movie.genre),
                'source_url': video.get('url', movie.source_url),
                'channel_id': channel.id,
                'channel_added_at': parse_channel_added_at(video.get('publication_date', '')),
            }
            for key, value in update_data.items():
                setattr(movie, key, value)

            updated_count += 1
        else:
            # Create new movie
            movie_data = {
                'title': video.get('title', ''),
                'year': extract_year_from_date(video.get('publication_date', '')),
                'thumbnail_url': video.get('thumbnail_url', ''),
                'views': video.get('views', 0),
                'source_url': video.get('url', ''),
                'duration': format_duration(video.get('duration', 0)),
                'description': video.get('description', ''),
                'genre': video.get('category', 'Видео'),
                'rating': None,
                'is_active': True,
                'channel_added_at': parse_channel_added_at(video.get('publication_date', '')),
                'channel_id': channel.id,
                'rutube_video_id': video['rutube_video_id']
            }
            movie = Movie(**movie_data)
            db.add(movie)
            imported_count += 1

        await db.flush()  # Ensure movie ID is available

        # Link movie to playlist if not already linked
        existing_link = await db.execute(
            select(PlaylistMovie).where(
                PlaylistMovie.playlist_id == playlist.id,
                PlaylistMovie.movie_id == movie.id
            )
        )
        existing_link_result = existing_link.scalar_one_or_none()

        if not existing_link_result:
            playlist_movie = PlaylistMovie(
                playlist_id=playlist.id,
                movie_id=movie.id
            )
            db.add(playlist_movie)
            linked_count += 1

    await db.commit()

    return {
        "imported": imported_count,
        "updated": updated_count,
        "linked": linked_count,
        "playlist_id": playlist.id,
        "playlist_title": playlist.title
    }


def extract_year_from_date(date_str):
    """Extract year from publication date string."""
    if not date_str:
        return datetime.now().year

    try:
        # Try parsing ISO format
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.year
    except Exception:
        return datetime.now().year


def parse_channel_added_at(date_str):
    """Parse created_ts from Rutube API to datetime with timezone."""
    if not date_str:
        return None

    try:
        # Parse ISO format with Z/UTC handling
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt
    except Exception:
        return None


def format_duration(seconds):
    """Convert duration in seconds to HH:MM:SS string format."""
    if not seconds or seconds == 0:
        return "00:00:00"

    try:
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    except Exception:
        return "00:00:00"


async def save_videos_to_db(videos, source_name="Rutube API"):
    """Save videos to PostgreSQL database using SQLAlchemy ORM."""
    print(f"Saving {len(videos)} videos from '{source_name}' to PostgreSQL database...")
    
    if not videos:
        return 0

    new_videos_count = 0
    async with AsyncSessionLocal() as db:
        for video in videos:
            # Check if this video already exists
            existing_video = await db.execute(
                select(Movie).where(Movie.source_url == video.get('url'))
            )
            existing = existing_video.scalar_one_or_none()
            
            if existing is None:
                # Prepare data for Movie model
                movie_data = {
                    'title': video.get('title', ''),
                    'year': extract_year_from_date(video.get('publication_date', '')),
                    'image_url': video.get('thumbnail_url'),
                    'thumbnail_url': video.get('thumbnail_url'),
                    'views': video.get('views', 0),
                    'source_url': video.get('url'),
                    'duration': format_duration(video.get('duration')),
                    'description': video.get('description', f'Video from {source_name}'),
                    'genre': video.get('category', 'Видео'),
                    'rating': None,
                    'is_active': True,
                    'channel_added_at': parse_channel_added_at(video.get('publication_date', '')),
                }
                
                # Create new movie object and add to database
                new_movie = Movie(**movie_data)
                db.add(new_movie)
                new_videos_count += 1
        
        if new_videos_count > 0:
            await db.commit()
            print(f"Saved {new_videos_count} new videos to database.")
        else:
            print("No new videos were added - all videos already existed in database.")
    
    return new_videos_count


async def run_api_scraper(limit: int = 100):
    """Main function to run the API scraping process."""
    print(f"Starting Rutube API scraper. Scraping limit: {limit} videos")
    
    try:
        # Fetch videos from API
        videos = await fetch_channel_videos(limit=limit)
        print(f"Fetched {len(videos)} videos from Rutube API")
        
        # Save collected videos to database
        if videos:
            print(f"Saving {len(videos)} videos to database...")
            new_videos_saved = await save_videos_to_db(videos, "Rutube API Scraper")
            print(f"Successfully saved {new_videos_saved} new videos to database.")
            return len(videos)
        else:
            print("No videos were found.")
            return 0
            
    except Exception as e:
        print(f"Error during API scraping: {e}")
        raise


# Channel import utilities
async def fetch_channel_details(channel_id: str):
    """Fetch channel details (name, avatar, description) from Rutube API by channel id."""
    async with aiohttp.ClientSession() as session:
        url = f"{RUTUBE_API_BASE}/person/{channel_id}/"
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    print(f"Channel details API returned status {response.status}")
                    return None
                data = await response.json()
                # API may return fields like name, avatar_url, description
                return {
                    'rutube_id': str(data.get('id', channel_id)),
                    'title': data.get('name', f'Channel {channel_id}'),
                    'avatar_url': data.get('avatar_url', None),
                    'description': data.get('description', None),
                }
        except Exception as e:
            print(f"Error fetching channel details: {e}")
            return None

async def import_rutube_channel(db, rutube_channel_url: str, channel_id: str, channel_videos_limit: int | None = None, scan_playlists: bool = True, per_playlist_limit: int = 100):
    """Create or update a Channel by rutube channel id. Optionally import recent videos."""
    # Check existing channel
    existing = await db.execute(select(Channel).where(Channel.rutube_id == channel_id))
    channel = existing.scalar_one_or_none()

    details = await fetch_channel_details(channel_id)

    if channel:
        # update basic fields
        if details:
            channel.title = details['title']
            channel.avatar_url = details.get('avatar_url')
            channel.description = details.get('description')
    else:
        # create new channel
        channel = Channel(
            rutube_id=channel_id,
            title=(details and details['title']) or f"Channel {channel_id}",
            avatar_url=details.get('avatar_url') if details else None,
            description=details.get('description') if details else None,
            is_active=True,
        )
        db.add(channel)
        await db.flush()

    imported_videos = 0
    playlists_found = 0
    playlists_processed = 0
    # Optionally import videos for this channel
    if channel_videos_limit and channel_videos_limit > 0:
        videos = await fetch_channel_videos_by_id(channel_id, limit=channel_videos_limit)
        for v in videos:
            # Use rutube video id if possible; for channel endpoint we didn't add it, so extract from url
            rutube_video_id = None
            try:
                rutube_video_id = v.get('url', '').rstrip('/').split('/')[-1]
            except Exception:
                rutube_video_id = None

            existing_movie = await db.execute(select(Movie).where(Movie.rutube_video_id == rutube_video_id))
            movie = existing_movie.scalar_one_or_none() if rutube_video_id else None

            if movie:
                # update
                movie.title = v.get('title', movie.title)
                movie.thumbnail_url = v.get('thumbnail_url', movie.thumbnail_url)
                movie.views = v.get('views', movie.views)
                movie.description = v.get('description', movie.description)
                movie.duration = format_duration(v.get('duration', 0))
                movie.genre = v.get('category', movie.genre)
                movie.source_url = v.get('url', movie.source_url)
                movie.channel_added_at = parse_channel_added_at(v.get('publication_date', ''))
                movie.channel_id = channel.id
            else:
                # create
                movie = Movie(
                    title=v.get('title', ''),
                    year=extract_year_from_date(v.get('publication_date', '')),
                    thumbnail_url=v.get('thumbnail_url', ''),
                    views=v.get('views', 0),
                    source_url=v.get('url', ''),
                    duration=format_duration(v.get('duration', 0)),
                    description=v.get('description', ''),
                    genre=v.get('category', 'Видео'),
                    is_active=True,
                    channel_added_at=parse_channel_added_at(v.get('publication_date', '')),
                    channel_id=channel.id,
                    rutube_video_id=rutube_video_id,
                )
                db.add(movie)
                imported_videos += 1
        await db.flush()

    # Optionally scan playlists and import them
    if scan_playlists:
        try:
            playlists = await fetch_channel_playlists_by_id(channel_id)
            playlists_found = len(playlists)
            for p in playlists:
                try:
                    playlist_rutube_id = str(p.get('rutube_id')) if isinstance(p, dict) else str(p)
                    if not playlist_rutube_id:
                        continue
                    playlist_url = f"https://rutube.ru/plst/{playlist_rutube_id}/"
                    await import_rutube_playlist_videos(db, playlist_url, playlist_rutube_id, per_playlist_limit)
                    playlists_processed += 1
                    await asyncio.sleep(0.25)
                except Exception as inner_e:
                    print(f"Error importing playlist {p}: {inner_e}")
        except Exception as e:
            print(f"Error fetching playlists for channel {channel_id}: {e}")

    await db.commit()

    return {
        'channel_id': channel.id,
        'rutube_channel_id': channel.rutube_id,
        'title': channel.title,
        'imported_videos': imported_videos,
        'playlists_found': playlists_found,
        'playlists_imported': playlists_processed,
    }

# Fetch playlists for a channel via Rutube API
async def fetch_channel_playlists_by_id(channel_id: str, limit: int | None = None):
    """Return list of playlists for a given channel id using Rutube API.
    Each item: { rutube_id, title, image_url?, description? }
    """
    results = []
    page = 1
    page_size = 20
    async with aiohttp.ClientSession() as session:
        while True:
            url_primary = f"{RUTUBE_API_BASE}/playlist/person/{channel_id}/?page={page}&page_size={page_size}"
            try:
                async with session.get(url_primary, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    data = None
                    if resp.status == 200:
                        data = await resp.json()
                    else:
                        # try alternative endpoint if available
                        alt = f"{RUTUBE_API_BASE}/person/{channel_id}/playlists/?page={page}&page_size={page_size}"
                        async with session.get(alt, timeout=aiohttp.ClientTimeout(total=30)) as alt_resp:
                            if alt_resp.status == 200:
                                data = await alt_resp.json()
                            else:
                                break
                    items = data.get('results', []) if isinstance(data, dict) else []
                    if not items:
                        break
                    for it in items:
                        playlist_id = str(it.get('id') or it.get('rutube_id') or '')
                        if not playlist_id:
                            continue
                        results.append({
                            'rutube_id': playlist_id,
                            'title': it.get('name') or it.get('title') or f"Playlist {playlist_id}",
                            'image_url': it.get('thumbnail_url') or it.get('image_url'),
                            'description': it.get('description')
                        })
                    page += 1
                    if limit and len(results) >= limit:
                        break
                    await asyncio.sleep(0.25)
            except Exception as e:
                print(f"Error fetching playlists page {page} for channel {channel_id}: {e}")
                break
    return results

if __name__ == "__main__":


    print("Starting Rutube API scraper...")
    asyncio.run(run_api_scraper())

