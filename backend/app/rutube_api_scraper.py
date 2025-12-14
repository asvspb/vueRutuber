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
    """Получить видео из канала через Rutube API"""
    videos = []
    page = 1
    page_size = 20

    async with aiohttp.ClientSession() as session:
        while len(videos) < limit:
            url = f"{RUTUBE_API_BASE}/video/person/{CHANNEL_ID}/?page={page}&page_size={page_size}"

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


if __name__ == "__main__":
    print("Starting Rutube API scraper...")
    asyncio.run(run_api_scraper())

