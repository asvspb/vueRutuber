import time
import sqlite3
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin

# --- Config ---
CHANNEL_URL = "https://rutube.ru/channel/32869212/"
DB_FILE = "rutube_videos.db"

def get_with_retry(driver, url, retries=3, delay=5):
    for i in range(retries):
        try:
            driver.get(url)
            return True
        except Exception as e:
            print(f"Failed to get {url}, attempt {i+1}/{retries}. Error: {e}")
            time.sleep(delay)
    return False

def init_db(db_path):
    """Инициализирует БД."""
    print(f"Инициализация базы данных: {db_path}")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                thumbnail_url TEXT,
                duration TEXT,
                views TEXT,
                publication_date_text TEXT,
                source_name TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def get_playlist_urls(driver, channel_url):
    """Находит все URL плейлистов на странице канала."""
    print(f"Захожу на страницу канала {channel_url} для поиска плейлистов...")
    if not get_with_retry(driver, channel_url):
        print(f"Failed to get channel page {channel_url} after multiple retries.")
        return []
    time.sleep(5)
    
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    print("Прокручиваю страницу канала для обнаружения всех плейлистов...")
    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    playlist_urls = set()
    playlist_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/plst/')]")
    for elem in playlist_elements:
        url = elem.get_attribute('href')
        if url:
            playlist_urls.add(url)
    
    print(f"Найдено {len(playlist_urls)} уникальных плейлистов.")
    return list(playlist_urls)

def save_videos_to_db(db_path, videos, source_name):
    """Сохраняет видео в БД."""
    if not videos:
        return 0
    print(f"Сохранение {len(videos)} видео из источника '{source_name}' в {db_path}...")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        video_data = [
            (v.get('title'), v.get('url'), v.get('thumbnail_url'), v.get('duration'), v.get('views'), v.get('publication_date_text'), source_name)
            for v in videos
        ]
        cursor.executemany(
            'INSERT OR IGNORE INTO videos (title, url, thumbnail_url, duration, views, publication_date_text, source_name) VALUES (?, ?, ?, ?, ?, ?, ?)',
            video_data
        )
        new_rows = cursor.rowcount
        conn.commit()
    return new_rows

def scrape_page(driver, page_url):
    """Собирает все видео с одной страницы с продвинутой логикой скроллинга и повторными попытками."""
    videos = []
    source_name = "Unknown"
    expected_count = 0
    
    print(f"\n--- Обработка страницы: {page_url} ---")
    if not get_with_retry(driver, page_url):
        print(f"Failed to get page {page_url} after multiple retries.")
        return

    time.sleep(5)

    try:
        page_title = driver.title
        source_name = page_title.split(' на RUTUBE')[0]
        print(f"Название источника: '{source_name}'")
        # Используем re.IGNORECASE для большей устойчивости
        match = re.search(r'(\d+)\s+видео', page_title, re.IGNORECASE)
        if match:
            expected_count = int(match.group(1))
            print(f"Заявлено на странице: {expected_count} видео.")
    except Exception as e:
        print(f"Не удалось получить заголовок или количество видео: {e}")

    found_count = 0
    scroll_attempts = 0
    max_scroll_attempts = 5 # Максимальное количество полных циклов прокрутки

    while scroll_attempts < max_scroll_attempts:
        scroll_attempts += 1
        print(f"\nПопытка прокрутки #{scroll_attempts}/{max_scroll_attempts}...")
        
        patience = 5 # Увеличим терпение для медленных загрузок
        patience_counter = 0
        last_height = driver.execute_script("return document.documentElement.scrollHeight")
        
        print("Начинаю полную прокрутку страницы с 'терпением'...")
        while True:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(3) # Сделаем паузу между скроллами чуть меньше
            new_height = driver.execute_script("return document.documentElement.scrollHeight")
            
            if new_height == last_height:
                patience_counter += 1
                print(f"Высота страницы не изменилась. Попытка {patience_counter}/{patience}...")
                if patience_counter >= patience:
                    print("Достигнут конец страницы для текущей попытки.")
                    break
            else:
                patience_counter = 0
            last_height = new_height

        print("\nИзвлекаю информацию о видео после прокрутки...")
        video_articles = driver.find_elements(By.XPATH, "//article[.//a[starts-with(@href, '/video/')]]")
        current_found_count = len(video_articles)
        print(f"Найдено {current_found_count} видео-карточек на странице.")

        if current_found_count > found_count:
            found_count = current_found_count
            print(f"Количество найденных видео увеличилось до {found_count}.")
        
        if expected_count == 0 or found_count >= expected_count:
            print("Найдено ожидаемое количество видео или больше. Прекращаю прокрутку.")
            break
        else:
            print(f"Расхождение: найдено {found_count} из {expected_count}. Будет предпринята новая попытка прокрутки через 5 секунд.")
            time.sleep(5)

    if expected_count > 0 and found_count < expected_count:
        print(f'''
        *********************************************************
        ВНИМАНИЕ: Итоговое расхождение в количестве видео!
        Заявлено: {expected_count}
        Найдено: {found_count}
        Не удалось загрузить все видео после {max_scroll_attempts} попыток прокрутки.
        *********************************************************
        ''')

    # Собираем финальный список видео
    videos = []
    video_articles = driver.find_elements(By.XPATH, "//article[.//a[starts-with(@href, '/video/')]]")
    for article in video_articles:
        video_info = {}
        try:
            title_element = article.find_element(By.XPATH, ".//a[@title and starts-with(@href, '/video/')]")
            video_info['title'] = title_element.get_attribute('title')
            relative_url = title_element.get_attribute('href')
            video_info['url'] = urljoin(page_url, relative_url)
            videos.append(video_info)
        except Exception:
            continue
            
    newly_added = save_videos_to_db(DB_FILE, videos, source_name)
    print(f"Добавлено {newly_added} новых видео из источника '{source_name}'.")
    print(f"--- Завершена обработка: {page_url} ---")

if __name__ == "__main__":
    init_db(DB_FILE)
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # 1. Найти все плейлисты
        playlist_urls = get_playlist_urls(driver, CHANNEL_URL)
        
        # 2. Создать полный список для сканирования (канал + плейлисты)
        urls_to_scrape = [CHANNEL_URL] + playlist_urls
        print(f"\nВсего будет обработано {len(urls_to_scrape)} страниц.")

        # 3. Последовательно обработать каждую страницу
        for url in urls_to_scrape:
            scrape_page(driver, url)

    finally:
        driver.quit()
        print("\n\nВсе задачи выполнены. Скрапинг завершен.")