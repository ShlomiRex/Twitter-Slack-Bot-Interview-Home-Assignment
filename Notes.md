# Tools used

* Postman
* DBeaver
* PyCharm Professional
* Google
* ngrok - For public domain for testing

# Why I use SQLite database?

I tried searching the slack messages. But due to lack of time, and legacy issues with the new slack API, the search API
request returns:
```
{
    "ok": false,
    "error": "not_allowed_token_type"
}
```

The issue (from 2020) is still not solved, according to:

https://github.com/mishk0/slack-bot-api/issues/147

Furthermore, instead of searching the entire slack messages which can contain garbage, we can use our own DB which
contains only the bot's messages.

Lastly, using SQLite instead of merely API request is more challenging.
