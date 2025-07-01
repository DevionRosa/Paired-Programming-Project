import sqlite3
import json

def setup_db(db_name='youtube_antirec.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Videos (
            video_id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            tags TEXT,         -- stores as json string
            cached_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    conn.commit()
    conn.close()
    print(f" Created Database:'{db_name}")

def cache_video_metadata(video_id, title, description, tags, db_name='youtube_antirec.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    tags_json = json.dumps(tags)
    cursor.execute('''
        INSERT OR REPLACE INTO Videos (video_id, title, description, tags)
        VALUES (?, ?, ?, ?)
    ''', (video_id, title, description, tags_json))
    conn.commit()
    conn.close()

def get_video_metadata(video_id, db_name='youtube_antirec.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('SELECT title, description, tags FROM Videos WHERE video_id = ?', (video_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        title, description, tags_json = row
        tags = json.loads(tags_json)
        return {'title': title, 'description': description, 'tags': tags}
    return None

