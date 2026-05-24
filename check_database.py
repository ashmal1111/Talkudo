#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime

def check_database():
    db_path = 'talkudo.db'
    
    print("=" * 70)
    print("🔍 TALKUDO DATABASE INSPECTOR")
    print("=" * 70)
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"\n❌ Database '{db_path}' not found!")
        print("   The database will be created automatically when you run the server.")
        return
    
    # Get file info
    file_size = os.path.getsize(db_path)
    print(f"\n📁 Database File: {db_path}")
    print(f"📊 File Size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
    print(f"🕐 Last Modified: {datetime.fromtimestamp(os.path.getmtime(db_path))}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"\n📋 TABLES FOUND: {len(tables)}")
    print("-" * 70)
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  📌 {table_name}: {count} records")
    
    # Show Users
    print("\n👥 USERS TABLE:")
    print("-" * 70)
    try:
        cursor.execute("SELECT user_id, username, email, status, custom_status, last_seen FROM users")
        users = cursor.fetchall()
        if users:
            for user in users:
                print(f"  ID: {user[0]} | Username: {user[1]} | Email: {user[2]} | Status: {user[3]} | Custom: {user[4]}")
        else:
            print("  No users found. Register some users first!")
    except sqlite3.OperationalError:
        print("  Users table not created yet. Run the server first!")
    
    # Show Messages
    print("\n💬 MESSAGES TABLE:")
    print("-" * 70)
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM messages
        """)
        msg_count = cursor.fetchone()[0]
        print(f"  Total messages: {msg_count}")
        
        if msg_count > 0:
            cursor.execute("""
                SELECT m.message_id, u1.username as sender, u2.username as receiver, 
                       substr(m.content, 1, 50) as content, m.timestamp
                FROM messages m
                JOIN users u1 ON m.sender_id = u1.user_id
                JOIN users u2 ON m.receiver_id = u2.user_id
                ORDER BY m.timestamp DESC LIMIT 5
            """)
            recent = cursor.fetchall()
            print("\n  Recent 5 messages:")
            for msg in recent:
                print(f"    [{msg[4]}] {msg[1]} → {msg[2]}: {msg[3]}")
    except sqlite3.OperationalError:
        print("  Messages table not created yet")
    
    # Show Reactions
    print("\n❤️ REACTIONS TABLE:")
    print("-" * 70)
    try:
        cursor.execute("SELECT COUNT(*) FROM message_reactions")
        react_count = cursor.fetchone()[0]
        print(f"  Total reactions: {react_count}")
    except sqlite3.OperationalError:
        print("  Reactions table not created yet")
    
    # Database Statistics
    print("\n📈 DATABASE STATISTICS:")
    print("-" * 70)
    
    # Get database page count
    cursor.execute("PRAGMA page_count")
    page_count = cursor.fetchone()[0]
    cursor.execute("PRAGMA page_size")
    page_size = cursor.fetchone()[0]
    
    print(f"  Database Pages: {page_count}")
    print(f"  Page Size: {page_size} bytes")
    print(f"  Total Size: {page_count * page_size:,} bytes")
    
    # Check integrity
    cursor.execute("PRAGMA integrity_check")
    integrity = cursor.fetchone()[0]
    print(f"  Integrity Check: {integrity}")
    
    conn.close()
    
    # Suggest actions
    print("\n" + "=" * 70)
    print("💡 WHAT YOU CAN DO:")
    print("=" * 70)
    print("  1. View full data: sqlite3 talkudo.db")
    print("  2. Export users: python3 -c \"import sqlite3; conn = sqlite3.connect('talkudo.db'); print([row for row in conn.execute('SELECT username, email FROM users')])\"")
    print("  3. Backup database: cp talkudo.db talkudo_backup.db")
    print("  4. Clear all data: rm talkudo.db (then restart server)")

def export_full_database():
    """Export all data to JSON for backup"""
    import json
    
    db_path = 'talkudo.db'
    if not os.path.exists(db_path):
        print("Database not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    export_data = {}
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Convert to list of dicts
        table_data = []
        for row in rows:
            table_data.append(dict(zip(columns, row)))
        
        export_data[table_name] = table_data
    
    # Save to JSON
    with open('talkudo_backup.json', 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print(f"\n✅ Database exported to talkudo_backup.json")
    conn.close()

if __name__ == "__main__":
    check_database()
    
    # Option to export
    choice = input("\n\nExport database to JSON? (y/n): ")
    if choice.lower() == 'y':
        export_full_database()
