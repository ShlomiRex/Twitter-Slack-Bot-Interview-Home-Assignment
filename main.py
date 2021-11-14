import configparser
import threading
import time
from dotenv import load_dotenv
from flask import Flask, Response
import logging

import slack_worker
import twitter_worker

# Environment
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


def dispatch_time_bot(every):
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


if __name__ == "__main__":
    running = True

    # Run flask
    kwargs = {'host': '127.0.0.1', 'port': 5000, 'threaded': True, 'use_reloader': False, 'debug': False}
    flaskThread = threading.Thread(target=app.run, daemon=True, kwargs=kwargs).start()

    # Run bot's time functionality in separate thread
    dispatch_time_bot(every=3600)
