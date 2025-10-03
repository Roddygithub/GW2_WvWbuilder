"""Script to fix the elite_specializations table by adding missing columns."""
import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from sqlite3 import Error


def get_database_connection():
    """Create a database connection to the SQLite database."""
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('gw2_wvwbuilder.db')
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None


def main():
    """Main function to add missing columns to the elite_specializations table."""
    # Get database connection
    conn = get_database_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='elite_specializations';
        """)
        
        if not cursor.fetchone():
            print("Error: 'elite_specializations' table does not exist.")
            return
        
        # Check if the columns already exist
        cursor.execute("PRAGMA table_info(elite_specializations);")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Add missing columns if they don't exist
        if 'weapon_type' not in columns:
            print("Adding 'weapon_type' column...")
            cursor.execute("""
                ALTER TABLE elite_specializations 
                ADD COLUMN weapon_type VARCHAR(50);
            """)
        
        if 'background_url' not in columns:
            print("Adding 'background_url' column...")
            cursor.execute("""
                ALTER TABLE elite_specializations 
                ADD COLUMN background_url VARCHAR(255);
            """)
        
        if 'is_active' not in columns:
            print("Adding 'is_active' column...")
            cursor.execute("""
                ALTER TABLE elite_specializations 
                ADD COLUMN is_active BOOLEAN DEFAULT 1;
            """)
        
        if 'created_at' not in columns:
            print("Adding 'created_at' column...")
            cursor.execute("""
                ALTER TABLE elite_specializations 
                ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            """)
        
        if 'updated_at' not in columns:
            print("Adding 'updated_at' column...")
            cursor.execute("""
                ALTER TABLE elite_specializations 
                ADD COLUMN updated_at TIMESTAMP;
            """)
        
        # Set default values for existing records
        print("Updating existing records...")
        cursor.execute("""
            UPDATE elite_specializations 
            SET 
                weapon_type = COALESCE(weapon_type, 'Greatsword'),
                is_active = COALESCE(is_active, 1),
                created_at = COALESCE(created_at, CURRENT_TIMESTAMP);
        """)
        
        # Commit the changes
        conn.commit()
        print("Database schema updated successfully!")
        
    except Error as e:
        print(f"Error updating database: {e}")
    finally:
        # Close the connection
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
