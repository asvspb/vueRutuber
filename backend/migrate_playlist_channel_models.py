"""
Migration script to add Playlist, Channel, and playlist_movies tables
and update the movies table with channel_id and rutube_video_id columns.
"""
import os
import sys
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the Python path
sys.path.append('/app')

from app.database import DATABASE_URL


def run_migration():
    # Create synchronous engine and session for migration
    engine = create_engine(DATABASE_URL.replace('+asyncpg', ''))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with SessionLocal() as db:
        # Add channel_id column to movies table if it doesn't exist
        try:
            db.execute(text("ALTER TABLE movies ADD COLUMN IF NOT EXISTS channel_id INTEGER"))
            print("Added channel_id column to movies table")
        except Exception as e:
            print(f"Error adding channel_id column: {e}")
            # If IF NOT EXISTS is not supported, we'll try the old way
            if "IF NOT EXISTS" in str(e).upper():
                # Check if column exists first
                result = db.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name='movies' AND column_name='channel_id'
                """))
                if not result.fetchone():
                    db.execute(text("ALTER TABLE movies ADD COLUMN channel_id INTEGER"))
                    print("Added channel_id column to movies table")

        # Add rutube_video_id column to movies table if it doesn't exist
        try:
            db.execute(text("ALTER TABLE movies ADD COLUMN IF NOT EXISTS rutube_video_id VARCHAR(255) UNIQUE"))
            print("Added rutube_video_id column to movies table")
        except Exception as e:
            print(f"Error adding rutube_video_id column: {e}")
            # If IF NOT EXISTS is not supported, we'll try the old way
            if "IF NOT EXISTS" in str(e).upper():
                # Check if column exists first
                result = db.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name='movies' AND column_name='rutube_video_id'
                """))
                if not result.fetchone():
                    db.execute(text("ALTER TABLE movies ADD COLUMN rutube_video_id VARCHAR(255) UNIQUE"))
                    print("Added rutube_video_id column to movies table")

        # Create index for rutube_video_id if it doesn't exist
        try:
            db.execute(text("CREATE INDEX IF NOT EXISTS ix_movies_rutube_video_id ON movies (rutube_video_id)"))
            print("Created index for rutube_video_id")
        except Exception as e:
            print(f"Error creating index for rutube_video_id: {e}")

        # Create channels table if it doesn't exist
        try:
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS channels (
                    id SERIAL PRIMARY KEY,
                    rutube_id VARCHAR(255) UNIQUE NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    avatar_url VARCHAR(500),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))
            print("Created channels table")
        except Exception as e:
            print(f"Error creating channels table: {e}")

        # Create playlists table if it doesn't exist
        try:
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS playlists (
                    id SERIAL PRIMARY KEY,
                    rutube_id VARCHAR(255) UNIQUE NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    image_url VARCHAR(500),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))
            print("Created playlists table")
        except Exception as e:
            print(f"Error creating playlists table: {e}")

        # Create playlist_movies association table if it doesn't exist
        try:
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS playlist_movies (
                    playlist_id INTEGER NOT NULL,
                    movie_id INTEGER NOT NULL,
                    PRIMARY KEY (playlist_id, movie_id),
                    FOREIGN KEY (playlist_id) REFERENCES playlists (id) ON DELETE CASCADE,
                    FOREIGN KEY (movie_id) REFERENCES movies (id) ON DELETE CASCADE
                )
            """))
            print("Created playlist_movies table")
        except Exception as e:
            print(f"Error creating playlist_movies table: {e}")

        # Create indexes if they don't exist
        try:
            db.execute(text("CREATE INDEX IF NOT EXISTS ix_movies_channel_id ON movies (channel_id)"))
            print("Created index for movies channel_id")
        except Exception as e:
            print(f"Error creating index for movies channel_id: {e}")

        try:
            db.execute(text("CREATE INDEX IF NOT EXISTS ix_channels_rutube_id ON channels (rutube_id)"))
            print("Created index for channels rutube_id")
        except Exception as e:
            print(f"Error creating index for channels rutube_id: {e}")

        try:
            db.execute(text("CREATE INDEX IF NOT EXISTS ix_playlists_rutube_id ON playlists (rutube_id)"))
            print("Created index for playlists rutube_id")
        except Exception as e:
            print(f"Error creating index for playlists rutube_id: {e}")

        # Create foreign key constraint for movies channel_id if not exists
        try:
            db.execute(text("""
                ALTER TABLE movies
                ADD CONSTRAINT fk_movies_channel_id
                FOREIGN KEY (channel_id) REFERENCES channels (id)
            """))
            print("Added foreign key constraint for movies channel_id")
        except Exception as e:
            # This might fail if constraint already exists, which is fine
            if "already exists" not in str(e).lower():
                print(f"Error adding foreign key constraint for movies channel_id: {e}")

        db.commit()

    print("Migration completed successfully!")
    print("- Added channel_id and rutube_video_id columns to movies table")
    print("- Created channels table")
    print("- Created playlists table")
    print("- Created playlist_movies association table")
    print("- Created all necessary indexes")


if __name__ == "__main__":
    run_migration()