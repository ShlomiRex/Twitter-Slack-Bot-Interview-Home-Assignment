import sqlite3

conn = sqlite3.connect("tweets.db", check_same_thread=False)

# Create the DB
# Note: We don't need to save the tweet text. We only care for tweet id and username.
# Timestamp is the insert timestamp of the row.
conn.cursor().execute(f"""
    CREATE TABLE IF NOT EXISTS Tweets (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        tweet_id INTEGER NOT NULL UNIQUE,
        twitter_username TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()


def insert_tweet(tweet_id: int, twitter_username: str):
    cur = conn.cursor()
    cur.execute("INSERT INTO Tweets (tweet_id, twitter_username) VALUES (?, ?)",
                [tweet_id, twitter_username])
    conn.commit()
