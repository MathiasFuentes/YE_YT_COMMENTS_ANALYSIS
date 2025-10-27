from googleapiclient.discovery import build
import sqlite3, os

API_KEY = AIzaSyAR5nJQHPWMyHgDk7NJUI2kAF44Zxuwoz4
VIDEO_ID = "qxOeWuAHOiw"

yt = build("youtube", "v3", developerKey=API_KEY)
conn = sqlite3.connect("databaser.db")
cur = conn.cursor()

page = None
while True:
    resp = yt.commentThreads().list(
        part="snippet,replies",
        videoId=VIDEO_ID,
        maxResults=100,
        pageToken=page,
        textFormat="plainText"
    ).execute()

    rows = []
    for it in resp.get("items", []):
        top = it["snippet"]["topLevelComment"]["snippet"]
        comment_id = it["snippet"]["topLevelComment"]["id"]
        rows.append((
            comment_id,
            VIDEO_ID,
            None,  # parent_id si es reply (para replies anidados, it.get("replies",{}))
            top.get("authorChannelId",{}).get("value"),
            top.get("authorDisplayName"),
            top.get("textDisplay"),  # o None si no guardar texto
            top.get("likeCount"),
            top.get("publishedAt"),
            f"https://www.youtube.com/watch?v={VIDEO_ID}&lc={comment_id}",
            None  # extra_json opcional
        ))

    cur.executemany("""
        INSERT OR IGNORE INTO yt_comments
        (comment_id, video_id, parent_id, author_id, author_name, text, like_count, published_at, url, extra_json)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, rows)
    conn.commit()

    page = resp.get("nextPageToken")
    if not page:
        break

conn.close()
