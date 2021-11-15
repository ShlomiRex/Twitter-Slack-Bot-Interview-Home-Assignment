import configparser
import logging
import os
from datetime import datetime, timedelta
from typing import Optional

import slack
from dotenv import load_dotenv
from twitter_worker.twitter_worker import Tweet

load_dotenv()

# Logging
logger = logging.getLogger()

# Config
config = configparser.ConfigParser()
config.read("config.ini")

# Globals
#client = slack.WebClient(token=os.environ["SLACK_TOKEN"])
client = slack.WebClient(token=os.environ["SLACK_BOT_USER_TOKEN"])
channel = config["SLACK"]["channel"]
channel_id = config["SLACK"]["channel_id"]


# slack_event_adapter = SlackEventAdapter(os.environ["SLACK_SIGNING_SECRET"], "/slack/events", app)

# @slack_event_adapter.on("message")
# def msg(payload):
#     print(payload)

def post_new_content(twitter_username: str, tweets: [Tweet]):
    """
    Post new content to slack.
    :param twitter_username: User ID / page / username
    :param tweets: List of tweets
    :return:
    """
    logger.info("Posting new content")
    tweets_begin_blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Showing new content for :star:{twitter_username}:star:",
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
                "text": f"End content for :star:{twitter_username}:star:",
                "emoji": True
            }
        }
    ]

    tweets_no_new_content_blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"No new content for :star:{twitter_username}:star:",
                "emoji": True
            }
        }
    ]

    if tweets:
        # Begin header
        client.chat_postMessage(channel=channel, blocks=tweets_begin_blocks)

        # Content
        for tweet in tweets:
            client.chat_postMessage(channel=channel, text=tweet.text)

        # End footer
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


def get_recent_time_activity() -> Optional[datetime]:
    #result = client.conversations_history(channel=channel_id, limit=5, inclusive=True, oldest=)

    # Get the messages of last hour. (and a bit of gap in extreme case)
    _oldest = datetime.now() - timedelta(hours=1, minutes=1)
    _oldest = datetime.timestamp(_oldest)
    result = client.conversations_history(channel=channel_id, inclusive=True, oldest=_oldest)
    messages = result.get("messages")

    # Sort messages by timestamp
    messages = sorted(messages, key=lambda d: d["ts"])

    # Reverse (so we can iterate the most recent messages)
    messages.reverse()

    for msg in messages:
        ts = msg.get("ts")
        text = msg.get("text")

        _datetime = datetime.fromtimestamp(float(ts))

        if "Current time" in text:
            # We found latest activity.
            logger.info("Latest bot activity timestamp: " + str(_datetime) + f" and the text is: '{text}'")
            return _datetime


def post_tweets(twitter_username: str, tweets: [Tweet]):
    if tweets:
        logger.info(f"Posting {len(tweets)} tweets to slack...")

        tweets_begin_blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"New tweets from: :star:{twitter_username}:star:",
                    "emoji": True
                }
            },
            {
                "type": "divider"
            }
        ]
        client.chat_postMessage(channel=channel, blocks=tweets_begin_blocks)
        for tweet in tweets:
            client.chat_postMessage(channel=channel, text=tweet.text)

