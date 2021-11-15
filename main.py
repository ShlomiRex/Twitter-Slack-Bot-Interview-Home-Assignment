import configparser
import datetime
import os.path
import pickle
import threading
import time
from dotenv import load_dotenv
from flask import Flask, Response, request
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

    # In order to not get "operation_timeout" we can run this in another thread
    def threaded_task():
        for page in twitter_worker.pages_to_pull:
            scan_timestamp = get_last_scan_timestamp(page)
            if not scan_timestamp:
                # Defaults to one hour as per instructions.
                tweets = twitter_worker.pull_tweets_last_hour(page)
                push_scan_timestamp(page, datetime.datetime.utcnow() - datetime.timedelta(hours=1))
            else:
                # Else, we scan again from the scan timestamp. If new tweets appear, it will be because of from the delta
                # timing.
                tweets = twitter_worker.pull_tweets(page, start_time=scan_timestamp)
                push_scan_timestamp(page, datetime.datetime.utcnow())
            slack_worker.post_new_content(page, tweets)

    threading.Thread(target=threaded_task).start()

    return Response(), 200


@app.route("/now", methods=["POST"])
def command_now():
    logger.info("Command 'now' called")
    slack_worker.post_current_datetime()

    return Response(), 200


@app.route("/tweet", methods=["POST"])
def command_tweet():
    logger.info("Command 'tweet' called")
    command_text = request.form.get("text")
    if command_text:
        s = command_text.split(" ", 1)
        if len(s) != 2:
            return Response("No recipient and no message was given.", 400)

        twitter_id = s[0]
        msg = s[1]

        success, reason = twitter_worker.tweet(twitter_id, msg)
        if success:
            return Response(), 200
        else:
            return Response(reason, 400)
    else:
        return Response("No tweeter id specified.", 400)




def get_last_scan_timestamp(twitter_id: str):
    """
    Read pickle file and return the scan timestamp for this user.
    :param twitter_id:
    :return:
    """
    if os.path.exists(pickled_timestamps_file):
        with open(pickled_timestamps_file, "rb") as file:
            obj = pickle.load(file)
            if obj and obj.get(twitter_id):
                return obj[twitter_id]


def push_scan_timestamp(twitter_id: str, timestamp: datetime.datetime):
    """
    Write scan timestamp for a user.
    :param twitter_id:
    :param timestamp:
    :return:
    """
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
            #utc_now = datetime.datetime.utcnow() - datetime.timedelta(minutes=60)  # TODO: Remove timedelta
            utc_now = datetime.datetime.utcnow()
            push_scan_timestamp(twitter_username, utc_now)
            if timestamp:
                tweets = twitter_worker.pull_tweets(twitter_username, timestamp)
                if tweets:
                    slack_worker.post_tweets(twitter_username, tweets)
            slack_worker.post_current_datetime()
            time.sleep(every)

    threading.Thread(target=time_loop).start()


if __name__ == "__main__":
    running = True

    # Run flask
    kwargs = {'host': '127.0.0.1', 'port': 5000, 'threaded': True, 'use_reloader': False, 'debug': False}
    flaskThread = threading.Thread(target=app.run, daemon=True, kwargs=kwargs).start()

    # Run bot's time functionality in separate thread
    dispatch_bot(twitter_username="DomnenkoShlomi", every=3600)


