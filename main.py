import configparser
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


def dispatch_time_bot(every: int):
    """
    Run the time bot. It writes to channel every X seconds the current time.
    :param every:Amount of seconds to wait between sends.
    :return:
    """

    def time_loop():
        while running:
            slack_worker.post_current_datetime()
            time.sleep(every)

    threading.Thread(target=time_loop).start()


def dispatch_new_tweets_bot(every: int, twitter_username: str):
    """
    Runs the bot that checks if user has new tweets.
    :param every:
    :param twitter_username:
    :return:
    """
    def time_loop():
        while running:
            twitter_worker.pull_new_tweets(twitter_username)
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
    slack_worker.search_bot_tweet_mention_user(twitter_id)

    pass


if __name__ == "__main__":
    running = True

    # Run flask
    kwargs = {'host': '127.0.0.1', 'port': 5000, 'threaded': True, 'use_reloader': False, 'debug': False}
    flaskThread = threading.Thread(target=app.run, daemon=True, kwargs=kwargs).start()

    # Run bot's time functionality in separate thread
    dispatch_time_bot(every=3600)

    # Run the bot's tweet sense in separate thread
    dispatch_new_tweets_bot(every=30, twitter_username="DomnenkoShlomi")

