"""
Migration script to update existing movies with a default channel_id
and update the channel_id column to be non-nullable after setting default values.
"""
import os
import sys
from sqlalchemy import Column, Integer, String, DateTime, Boolean, create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the Python path
sys.path.append('/app')

from app.database import DATABASE_URL


def run_migration():
    # Create synchronous engine and session for migration
    engine = create_engine(DATABASE_URL.replace('+asyncpg', ''))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with SessionLocal() as db:
        # Create a default channel if one doesn't exist
        result = db.execute(text("""
            SELECT id FROM channels WHERE rutube_id = 'default' OR title = 'Default Channel'
        """))
        default_channel_id = result.fetchone()
        
        if default_channel_id:
            default_channel_id = default_channel_id[0]
        else:
            # Create a default channel
            db.execute(text("""
                INSERT INTO channels (rutube_id, title, description, avatar_url, is_active, created_at) 
                VALUES ('default', 'Default Channel', 'Default channel for existing movies', NULL, true, NOW())
            """))
            result = db.execute(text("SELECT id FROM channels WHERE rutube_id = 'default'"))
            default_channel_id = result.fetchone()[0]
        
        # Update all movies with NULL channel_id to use the default channel
        db.execute(text(f"""
            UPDATE movies 
            SET channel_id = {default_channel_id} 
            WHERE channel_id IS NULL OR channel_id = 0
        """))
        
        # Also set rutube_video_id for existing movies if possible
        # Extract video ID from source_url if not set
        db.execute(text("""
            UPDATE movies 
            SET rutube_video_id = SPLIT_PART(SPLIT_PART(source_url, '/video/', 2), '/', 1)
            WHERE rutube_video_id IS NULL AND source_url LIKE '%rutube.ru/video/%'
        """))
        
        db.commit()
    
    print("Data migration completed successfully!")
    print("- Created/assigned default channel for movies without channel_id")
    print("- Updated rutube_video_id for existing movies")


if __name__ == "__main__":
    run_migration()