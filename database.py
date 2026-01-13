import sqlite3
from datetime import datetime

class MeetingDatabase:
    def __init__(self, db_path="meetings.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        """Create the meetings table if it doesn't exist"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                date TEXT NOT NULL,
                audio_file TEXT,
                transcript TEXT,
                notes TEXT,
                duration INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def save_meeting(self, title, audio_file, transcript, notes, duration=0):
        """Save a new meeting to the database"""
        cursor = self.conn.execute("""
            INSERT INTO meetings (title, date, audio_file, transcript, notes, duration)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            title or "Untitled Meeting",
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            audio_file,
            transcript,
            notes,
            duration
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_all_meetings(self):
        """Get list of all meetings (without full content)"""
        cursor = self.conn.execute("""
            SELECT id, title, date, duration FROM meetings
            ORDER BY date DESC
        """)
        return cursor.fetchall()
    
    def get_meeting(self, meeting_id):
        """Get full details of a specific meeting"""
        cursor = self.conn.execute("""
            SELECT id, title, date, audio_file, transcript, notes, duration
            FROM meetings WHERE id = ?
        """, (meeting_id,))
        return cursor.fetchone()
    
    def search_meetings(self, keyword):
        """Search meetings by keyword in title, transcript, or notes"""
        cursor = self.conn.execute("""
            SELECT id, title, date, duration FROM meetings
            WHERE title LIKE ? OR transcript LIKE ? OR notes LIKE ?
            ORDER BY date DESC
        """, (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        return cursor.fetchall()
    
    def delete_meeting(self, meeting_id):
        """Delete a meeting"""
        self.conn.execute("DELETE FROM meetings WHERE id = ?", (meeting_id,))
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        self.conn.close()