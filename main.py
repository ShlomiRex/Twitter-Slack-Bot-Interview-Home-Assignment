import configparser
import datetime
import os.path
import pickle
import threading
import time
from dotenv import load_dotenv
from flask import Flask, Response
import logging

import slack_worker
import twitter_worker

# Environment
from twitter_worker.twitter_worker import Tweet

load_dotenv()

# Configuration files
config = configparser.ConfigParser()
config.read("config.ini")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Flask
app = Flask(__name__)

# Globals / others
running = False
pickled_timestamps_file = "scan_timestamps.pkl"


@app.route("/new-content", methods=["POST"])
def command_new_content():
    """
    Command handler for '/new-content'.
    :return:
    """
    logger.info("Command 'new-content' called")
    # data = request.form
    # channel_id = data.get("channel_id")
    # client.chat_postMessage(channel=channel_id, text="Ok")

    for page in twitter_worker.pages_to_pull:
        tweets = twitter_worker.pull_tweets_last_hour(page)
        slack_worker.post_new_content(page, tweets)

    return Response(), 200


@app.route("/now", methods=["POST"])
def command_now():
    logger.info("Command 'now' called")
    slack_worker.post_current_datetime()

    return Response(), 200


def get_last_scan_timestamp(twitter_id: str):
    if os.path.exists(pickled_timestamps_file):
        with open(pickled_timestamps_file, "rb") as file:
            obj = pickle.load(file)
            if obj:
                return obj[twitter_id]


def push_scan_timestamp(twitter_id: str, timestamp: datetime.datetime):
    if not os.path.exists(pickled_timestamps_file):
        open(pickled_timestamps_file, "x")
    with open(pickled_timestamps_file, "rb") as file:
        try:
            obj = pickle.load(file)
        except EOFError:
            obj = None

    with open(pickled_timestamps_file, "wb") as file:
        if obj:
            obj[twitter_id] = timestamp
        else:
            obj = {twitter_id: timestamp}
        pickle.dump(obj, file)


def dispatch_bot(twitter_username: str, every: int):
    """
    Run the time bot. It writes to channel every X seconds the current time. It also scans for new tweets.
    :param twitter_username:
    :param every:Amount of seconds to wait between sends.
    :return:
    """
    def time_loop():
        while running:
            timestamp = get_last_scan_timestamp(twitter_username)
            utc_now = datetime.datetime.utcnow() - datetime.timedelta(minutes=60)  # TODO: Remove timedelta
            push_scan_timestamp(twitter_username, utc_now)
            if timestamp:
                tweets = twitter_worker.pull_tweets(twitter_username, timestamp)
                if tweets:
                    slack_worker.post_tweets(twitter_username, tweets)
            slack_worker.post_current_datetime()
            time.sleep(every)

    threading.Thread(target=time_loop).start()


def get_new_tweets(twitter_id: str) -> [Tweet]:
    """
    Posts to slack new tweets made by a user, without posting the same tweet twice.
    :param twitter_id:
    :return:
    """
    # First get the tweets of the last hour.
    last_hour_tweets = twitter_worker.pull_tweets_last_hour(twitter_id)

    # Because the bot can be down for some time, we need to know what is the last message of the bot.
    # When we have the time of last activity, we can filter all slack messages (persistent) since then, and
    # post only new tweets.


    print(last_hour_tweets)

    pass


if __name__ == "__main__":
    running = True

    # Run flask
    kwargs = {'host': '127.0.0.1', 'port': 5000, 'threaded': True, 'use_reloader': False, 'debug': False}
    flaskThread = threading.Thread(target=app.run, daemon=True, kwargs=kwargs).start()

    # Run bot's time functionality in separate thread
    dispatch_bot(twitter_username="DomnenkoShlomi", every=3600)


