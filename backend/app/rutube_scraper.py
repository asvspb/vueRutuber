import asyncio
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin
from datetime import datetime
import os
import sys

# Add the backend path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models import Movie
from sqlalchemy import select


# --- Config ---
CHANNEL_URL = os.getenv("RUTUBE_CHANNEL_URL", "https://rutube.ru/channel/32869212/")
SCRAPE_LIMIT = int(os.getenv("RUTUBE_SCRAPE_LIMIT", "100"))  # Limit to 100 videos for initial run

def get_with_retry(driver, url, retries=3, delay=5):
    """Attempts to get a URL with retries."""
    for i in range(retries):
        try:
            driver.get(url)
            return True
        except Exception as e:
            print(f"Failed to get {url}, attempt {i+1}/{retries}. Error: {e}")
            if i < retries - 1:
                time.sleep(delay)
    return False

def extract_year_from_date(date_str):
    """Extract year from publication date string."""
    if not date_str:
        return datetime.now().year

    # Look for 4-digit year in the string
    year_match = re.search(r'\b(19|20)\d{2}\b', str(date_str))
    if year_match:
        return int(year_match.group(0))

    return datetime.now().year

def parse_views(views_str):
    """Convert views string to integer."""
    if not views_str:
        return 0
    
    # Clean the string and try to extract numbers
    views_clean = re.sub(r'[^\d.,]', '', views_str.replace(' ', ''))
    
    if not views_clean:
        return 0
    
    try:
        # Handle decimal numbers and various formats
        if '.' in views_clean or ',' in views_clean:
            views_clean = views_clean.replace(',', '.')
            num = float(views_clean)
        else:
            num = int(views_clean)
        
        # Handle common format like "1.2K" or "2.5M"
        if 'K' in views_str.upper():
            return int(num * 1000)
        elif 'M' in views_str.upper():
            return int(num * 1000000)
        else:
            # If no K/M, assume it's already a number
            return int(num)
    except ValueError:
        return 0

def scrape_video_cards(driver):
    """Scrape video cards from current page."""
    print("Scraping video cards from current page...")
    
    # Wait for page to load
    time.sleep(3)
    
    # Find video elements using multiple selectors to catch most videos
    video_selectors = [
        "//div[contains(@class, 'video') and .//a[starts-with(@href, '/video/')]]",
        "//article[.//a[starts-with(@href, '/video/')]]",
        "//a[starts-with(@href, '/video/')]//parent::div[contains(@class, 'card') or contains(@class, 'item') or contains(@class, 'video')]"
    ]
    
    video_elements = []
    for selector in video_selectors:
        try:
            elements = driver.find_elements(By.XPATH, selector)
            video_elements.extend(elements)
        except:
            continue
    
    print(f"Found {len(video_elements)} video elements")
    
    videos = []
    for i, element in enumerate(video_elements):
        if len(videos) >= SCRAPE_LIMIT:
            print(f"Reached scraping limit of {SCRAPE_LIMIT} videos")
            break
            
        video_info = {}
        
        try:
            # Get video URL and ID
            link_element = None
            link_selectors = [
                ".//a[starts-with(@href, '/video/')]",
                ".//a[contains(@href, '/video/')]"
            ]
            
            for sel in link_selectors:
                try:
                    link_element = element.find_element(By.XPATH, sel)
                    break
                except:
                    continue
                    
            if link_element is None:
                continue  # Skip if no link found
                
            relative_url = link_element.get_attribute('href')
            video_info['url'] = urljoin('https://rutube.ru', relative_url)
            
            # Extract video ID from URL
            video_id_match = re.search(r'/video/([a-zA-Z0-9]+)/?', video_info['url'])
            if video_id_match:
                video_info['video_id'] = video_id_match.group(1)
            else:
                video_info['video_id'] = f'unknown_{i}'  # Fallback ID
            
            # Get video title
            title_selectors = [
                ".//div[@class='video-title']",
                ".//a[@title]",
                ".//h3",
                ".//span[contains(@class, 'title') or contains(@class, 'name') or contains(@class, 'caption')]",
                ".//div[contains(@class, 'title') or contains(@class, 'name') or contains(@class, 'caption')]"
            ]
            
            title_element = None
            for sel in title_selectors:
                try:
                    title_element = element.find_element(By.XPATH, sel)
                    break
                except:
                    continue

            if title_element:
                video_info['title'] = title_element.text.strip() or f'Video {i}'
            else:
                video_info['title'] = f'Video {i}'

            # Try to get thumbnail
            img_selectors = [
                ".//img[contains(@src, 'imagetools') or contains(@src, 'images')]",
                ".//img[contains(@alt, 'video') or contains(@alt, 'image')]"
            ]

            thumbnail_element = None
            for sel in img_selectors:
                try:
                    thumbnail_element = element.find_element(By.XPATH, sel)
                    break
                except:
                    continue

            if thumbnail_element:
                video_info['thumbnail_url'] = thumbnail_element.get_attribute('src')
            else:
                video_info['thumbnail_url'] = None

            # Try to get duration
            time_selectors = [
                ".//time",
                ".//span[contains(@class, 'duration') or contains(@class, 'time')]",
                ".//div[contains(@class, 'duration') or contains(@class, 'time')]"
            ]

            duration_element = None
            for sel in time_selectors:
                try:
                    duration_element = element.find_element(By.XPATH, sel)
                    break
                except:
                    continue

            if duration_element:
                video_info['duration'] = duration_element.text.strip()
            else:
                video_info['duration'] = None

            # Try to get views count
            views_selectors = [
                ".//span[contains(text(), 'просмотр') or contains(text(), 'view') or contains(text(), 'тыс.') or contains(text(), 'views') or contains(text(), 'K') or contains(text(), 'M')]",
                ".//div[contains(text(), 'просмотр') or contains(text(), 'view') or contains(text(), 'тыс.') or contains(text(), 'views') or contains(text(), 'K') or contains(text(), 'M')]"
            ]

            views_element = None
            for sel in views_selectors:
                try:
                    views_element = element.find_element(By.XPATH, sel)
                    break
                except:
                    continue

            if views_element:
                video_info['views'] = views_element.text.strip()
            else:
                video_info['views'] = "0"

            # Publication date and description might not be available on card view
            video_info['publication_date_text'] = str(datetime.now().date())  # Placeholder
            video_info['description'] = f'Video from Rutube: {video_info["title"]}'

            # Add to list if we have required fields
            if video_info.get('url') and video_info.get('title'):
                videos.append(video_info)
                
        except Exception as e:
            print(f"Error parsing video element {i}: {e}")
            continue
    
    return videos

async def save_videos_to_db(videos, source_name="Rutube Channel"):
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
                    'year': extract_year_from_date(video.get('publication_date_text', '')),
                    'image_url': video.get('thumbnail_url'),
                    'thumbnail_url': video.get('thumbnail_url'),
                    'views': parse_views(video.get('views', '0')),
                    'source_url': video.get('url'),
                    'duration': video.get('duration'),
                    'description': video.get('description', f'Video from {source_name}'),
                    'genre': 'Видео',  # Default genre for Rutube videos
                    'rating': None,  # Rating not available from Rutube
                    'is_active': True,
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

def scrape_page(driver, page_url, source_name="Rutube Channel", scrape_limit: int | None = None):
    """Scrape videos from a single page with scrolling logic."""
    limit = scrape_limit if scrape_limit is not None else SCRAPE_LIMIT
    all_videos = []
    
    print(f"\n--- Processing page: {page_url} ---")
    if not get_with_retry(driver, page_url):
        print(f"Failed to get page {page_url} after multiple retries.")
        return []

    time.sleep(5)

    scroll_attempts = 0
    max_scroll_attempts = 3  # Limit scroll attempts to prevent endless scrolling
    
    while scroll_attempts < max_scroll_attempts and len(all_videos) < limit:
        scroll_attempts += 1
        print(f"\nScroll attempt #{scroll_attempts}/{max_scroll_attempts}...")
        
        patience = 3  # Number of times to wait for new content to load
        patience_counter = 0
        last_height = driver.execute_script("return document.documentElement.scrollHeight")

        print("Starting complete page scroll with patience...")
        while patience_counter < patience and len(all_videos) < limit:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)  # Wait for content to load
            new_height = driver.execute_script("return document.documentElement.scrollHeight")

            if new_height == last_height:
                patience_counter += 1
                print(f"Page height unchanged. Attempt {patience_counter}/{patience}...")
                if patience_counter >= patience:
                    print("Reached end of scrollable content.")
                    break
            else:
                patience_counter = 0  # Reset counter when new content loads
            last_height = new_height

        print("\nExtracting video information after scroll...")
        current_videos = scrape_video_cards(driver)
        
        # Filter out duplicates before adding
        unique_current = []
        for video in current_videos:
            if not any(v['url'] == video['url'] for v in all_videos):
                unique_current.append(video)
        
        all_videos.extend(unique_current)
        current_count = len(all_videos)
        print(f"Found {len(unique_current)} new unique videos on this scroll, total: {current_count}")
        
        if current_count >= limit:
            print(f"Reached scraping limit of {SCRAPE_LIMIT} videos")
            break
    
    print(f"Collected {len(all_videos)} unique videos from {page_url}")
    return all_videos[:limit]  # Return only up to the limit

async def run_scraper(limit: int | None = None):
    """Main function to run the scraping process."""
    limit_to_use = limit if limit is not None else SCRAPE_LIMIT
    print(f"Starting Rutube scraper with PostgreSQL integration. Scraping limit: {limit_to_use} videos")
    
    # Set environment variable to disable crashpad
    os.environ['CHROME_CRASHPAD_PIPE_NAME'] = ''

    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/chromium"
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-crash-reporter")
    chrome_options.add_argument("--crash-dumps-dir=/tmp/crashpad")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--user-data-dir=/tmp/chrome-user-data")
    chrome_options.add_argument("--data-path=/tmp/chrome-data")
    chrome_options.add_argument("--disk-cache-dir=/tmp/chrome-cache")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    try:
        # Use system chromium-driver instead of ChromeDriverManager to avoid permission issues
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Scrape videos from the main channel page
        print(f"Starting to scrape videos from {CHANNEL_URL}")
        channel_videos = scrape_page(driver, CHANNEL_URL, "Rutube Main Channel", scrape_limit=limit_to_use)
        
        # Save collected videos to database
        if channel_videos:
            print(f"Saving {len(channel_videos)} videos to database...")
            new_videos_saved = await save_videos_to_db(channel_videos, "Rutube Scraper")
            print(f"Successfully saved {new_videos_saved} new videos to database.")
        else:
            print("No videos were found to save.")
        
        return len(channel_videos)

    finally:
        if 'driver' in locals():
            driver.quit()
        print("\n\nScraping completed.")

if __name__ == "__main__":
    print("Starting Rutube scraper with PostgreSQL integration...")
    asyncio.run(run_scraper())