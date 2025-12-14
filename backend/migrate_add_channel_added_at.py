#!/usr/bin/env python3
"""
Migration script to add channel_added_at column to movies table.
Run this script once after deploying the backend changes.
"""
import os
from sqlalchemy import text
from app.database import sync_engine

def run_migration():
    """Add channel_added_at column to movies table."""
    with sync_engine.connect() as conn:
        # Add the column if it doesn't exist
        conn.execute(text("""
            ALTER TABLE movies
            ADD COLUMN IF NOT EXISTS channel_added_at TIMESTAMP WITH TIME ZONE NULL;
        """))

        # Create index if it doesn't exist
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_movies_channel_added_at
            ON movies (channel_added_at);
        """))

        conn.commit()
        print("Migration completed: added channel_added_at column and index")

if __name__ == "__main__":
    run_migration()