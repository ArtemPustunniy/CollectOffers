import sqlite3

DATABASE = 'processed_posts.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS channel_last_post (
            channel_name TEXT PRIMARY KEY,
            last_post_time TEXT
        )
    ''')
    conn.commit()
    conn.close()


def get_last_post_time(channel_name):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT last_post_time FROM channel_last_post WHERE channel_name = ?', (channel_name,))
    row = cur.fetchone()
    conn.close()
    return row['last_post_time'] if row else None


def update_last_post_time(channel_name, new_time):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO channel_last_post (channel_name, last_post_time)
        VALUES (?, ?)
        ON CONFLICT(channel_name) DO UPDATE SET last_post_time = excluded.last_post_time
    ''', (channel_name, new_time))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_db()
    channel = "@nevolk_vacancies"
    last_time = get_last_post_time(channel)
    if last_time:
        print(f"Последнее обработанное время для канала {channel}: {last_time}")
    else:
        print(f"Для канала {channel} ещё не было обработанных постов.")
    new_time = "2025-01-31T15:30:00"
    update_last_post_time(channel, new_time)
    print(f"Обновлено время для канала {channel}: {new_time}")
    print("Новое сохранённое время:", get_last_post_time(channel))
