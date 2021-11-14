import configparser
import logging
import os
from datetime import datetime
import slack
from dotenv import load_dotenv

from twitter_api import Tweet

# Environment
load_dotenv()

# Logging
logger = logging.getLogger()

# Config
config = configparser.ConfigParser()
config.read("config.ini")

# Globals
client = slack.WebClient(token=os.environ["SLACK_TOKEN"])
channel = config["SLACK"]["channel"]


# slack_event_adapter = SlackEventAdapter(os.environ["SLACK_SIGNING_SECRET"], "/slack/events", app)

# @slack_event_adapter.on("message")
# def msg(payload):
#     print(payload)

def post_new_content(page: str, tweets: [Tweet]):
    """
    Post new content to slack.
    :param page: User ID / page / username
    :param tweets: List of tweets
    :return:
    """
    if tweets:
        client.chat_postMessage(channel=channel, text=f"New content for: {page}", )
    for tweet in tweets:
        client.chat_postMessage(channel=channel, text=tweet.text)


def post_current_datetime():
    """
    Post to channel the current time.
    :return:
    """
    logger.info("Posting current datetime")
    client.chat_postMessage(channel=channel, text=f"Current time: {datetime.now()}")
