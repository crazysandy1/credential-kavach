#!/usr/bin/env python3
"""
Database migration script to add employer fields to existing database
"""
import os
import sqlite3
from pathlib import Path

def migrate_database():
    """Add employer fields to the users table"""
    
    # Database path
    db_path = Path("instance/credential_kavach.db")
    
    if not db_path.exists():
        print("Database doesn't exist. New database will be created when app starts.")
        return
    
    print(f"Migrating database at: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if employer fields already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        employer_fields = ['company_name', 'company_registration', 'industry', 'hr_contact']
        missing_fields = [field for field in employer_fields if field not in columns]
        
        if not missing_fields:
            print("Employer fields already exist in database.")
            conn.close()
            return
        
        print(f"Adding missing employer fields: {missing_fields}")
        
        # Add missing employer fields
        for field in missing_fields:
            if field == 'company_name':
                cursor.execute("ALTER TABLE users ADD COLUMN company_name VARCHAR(200)")
            elif field == 'company_registration':
                cursor.execute("ALTER TABLE users ADD COLUMN company_registration VARCHAR(100)")
            elif field == 'industry':
                cursor.execute("ALTER TABLE users ADD COLUMN industry VARCHAR(100)")
            elif field == 'hr_contact':
                cursor.execute("ALTER TABLE users ADD COLUMN hr_contact VARCHAR(200)")
        
        # Commit changes
        conn.commit()
        print("Database migration completed successfully!")
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(users)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        print(f"Updated columns: {updated_columns}")
        
        conn.close()
        
    except Exception as e:
        print(f"Migration failed: {e}")
        if conn:
            conn.close()

def backup_database():
    """Create a backup of the current database"""
    db_path = Path("instance/credential_kavach.db")
    if db_path.exists():
        backup_path = Path(f"instance/credential_kavach_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"Database backed up to: {backup_path}")
        return backup_path
    return None

if __name__ == "__main__":
    from datetime import datetime
    
    print("Database Migration Script")
    print("=" * 30)
    
    # Create backup first
    backup_path = backup_database()
    if backup_path:
        print(f"Backup created: {backup_path}")
    
    # Run migration
    migrate_database()
    
    print("\nMigration complete. You can now start the Flask app.")