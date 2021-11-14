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
    logger.info("Posting new content")
    tweets_begin_blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Showing new content for :star:{page}:star:",
                "emoji": True
            }
        },
        {
            "type": "divider"
        }
    ]
    tweets_end_blocks = [
        {
            "type": "divider"
        },
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"End content for :star:{page}:star:",
                "emoji": True
            }
        }
    ]

    tweets_no_new_content_blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"No new content for :star:{page}:star:",
                "emoji": True
            }
        }
    ]

    if tweets:
        # Begin
        client.chat_postMessage(channel=channel, blocks=tweets_begin_blocks)

        # Content
        for tweet in tweets:
            client.chat_postMessage(channel=channel, text=tweet.text)

        # End
        client.chat_postMessage(channel=channel, blocks=tweets_end_blocks)
    else:
        # No new content.
        client.chat_postMessage(channel=channel, blocks=tweets_no_new_content_blocks)


def post_current_datetime():
    """
    Post current date and time to slack.
    :return:
    """
    logger.info("Posting current datetime")
    client.chat_postMessage(channel=channel, text=f"Current time: {datetime.now()}")
