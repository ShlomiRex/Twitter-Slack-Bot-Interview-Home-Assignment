import configparser
import logging
import os
from datetime import datetime
import slack
from dotenv import load_dotenv
from twitter_worker.twitter_worker import Tweet
from database import tweets_db

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

            # Save tweet
            tweets_db.insert_tweet(tweet.id, twitter_username)

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


def search_bot_tweet_mention_user(user_tweet_id: str):

    return None