import datetime
import os
import threading
import time

import slack
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger()

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

client = slack.WebClient(token=os.environ["SLACK_TOKEN"])
# slack_event_adapter = SlackEventAdapter(os.environ["SLACK_SIGNING_SECRET"], "/slack/events", app)

channel_content = "content"
running = False


# @slack_event_adapter.on("message")
# def msg(payload):
#     print(payload)


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
    client.chat_postMessage(channel=channel_content, text="Ok")

    return Response(), 200


@app.route("/now", methods=["POST"])
def command_now():
    logger.info("Command 'now' called")
    post_current_datetime()

    return Response(), 200


def post_current_datetime():
    """
    Post to channel the current time.
    :return:
    """
    logger.info("Posting current datetime")
    client.chat_postMessage(channel=channel_content, text=f"Current time: {datetime.datetime.now()}")


def dispatch_time_bot(every):
    """
    Run the time bot. It writes to channel every X seconds the current time.
    :param every:Amount of seconds to wait between sends.
    :return:
    """

    def time_loop():
        while running:
            post_current_datetime()
            time.sleep(every)

    threading.Thread(target=time_loop).start()


if __name__ == "__main__":
    running = True

    kwargs = {'host': '127.0.0.1', 'port': 5000, 'threaded': True, 'use_reloader': False, 'debug': False}
    flaskThread = threading.Thread(target=app.run, daemon=True, kwargs=kwargs).start()

    dispatch_time_bot(every=3600)
