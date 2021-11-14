import os
import slack
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
import logging

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger()

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

client = slack.WebClient(token=os.environ["SLACK_TOKEN"])
slack_event_adapter = SlackEventAdapter(os.environ["SIGNING_SECRET"], "/slack/events", app)


@slack_event_adapter.on("message")
def msg(payload):
    print(payload)


@app.route("/new-content", methods=["POST"])
def new_content():
    print("New content called")
    data = request.form
    channel_id = data.get("channel_id")
    client.chat_postMessage(channel=channel_id, text="Ok")
    return Response(), 200


if __name__ == "__main__":
    # client.chat_postMessage(channel="#content", text="Hello World!")
    app.run(debug=True, port=5000)
