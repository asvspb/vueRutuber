"""
Rutube API-based scraper - более надежная альтернатива Selenium
"""
import asyncio
import aiohttp
from datetime import datetime
from app.database import AsyncSessionLocal
from app.models import Movie
from sqlalchemy import select
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


def extract_year_from_date(date_str):
    """Extract year from publication date string."""
    if not date_str:
        return datetime.now().year

    try:
        # Try parsing ISO format
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.year
    except:
        return datetime.now().year


def parse_channel_added_at(date_str):
    """Parse created_ts from Rutube API to datetime with timezone."""
    if not date_str:
        return None

    try:
        # Parse ISO format with Z/UTC handling
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt
    except:
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
    except:
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

