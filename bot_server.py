import json
import threading
from flask import Flask, request, make_response, render_template

from slack import *

app = Flask(__name__)

def _event_handler(slack_event):
    """
    slack_event : dict
        response from a Slack command
    Returns
    ----------
    obj
        Response object with 200 - ok
    """
    try:
        cmmd =  command_to_function[slack_event.get("command")]
        thread = threading.Thread(target=cmmd, args=(slack_event,), daemon=True)
        thread.start()
        return make_response("Command being processed...", 200, {"X-Slack-No-Retry": 1})
    except Exception as e:
    # If the event_command wasn't recognized
        print(e)
        print(command_to_function)
        return make_response("I don't recognize that command", 200, {"X-Slack-No-Retry": 1})

@app.route("/listening", methods=["GET", "POST"])
def hears():
    """
    This route listens for incoming commands from Slack and uses the event
    handler helper function to route commands to our Bot.
    """
    slack_event = request.form
    print('request.data')
    # ============= Slack URL Verification ============ #
    # In order to verify the url of our endpoint, Slack will send a challenge
    # token in a request and check for this token in the response our endpoint
    # sends back.
    #       For more info: https://api.slack.com/events/url_verification
    if "challenge" in slack_event.keys():
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                             })

    # ============ Slack Token Verification =========== #
    # We can verify the request is coming from Slack by checking that the
    # verification token in the request matches our app's settings
    if "dcpFgBZ9cyC67H1lyCLvaxBP" != slack_event.get("token"):
        message = "Invalid Slack verification token: %s \npyBot has: \
                   %s\n\n" % (slack_event["token"], dcpFgBZ9cyC67H1lyCLvaxBP)
        # By adding "X-Slack-No-Retry" : 1 to our response headers, we turn off
        # Slack's automatic retries during development.
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    # ====== Process Incoming Events from Slack ======= #
    # If the incoming request is an Event we've subcribed to
    if "text" in slack_event and "command" in slack_event:
        # Then handle the event by event_type and have your bot respond
        return _event_handler(slack_event)
    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})

command_to_function = {}

def add_function(command, func):
    assert isinstance(command, str)
    assert callable(func)
    command_to_function[command] = func

if __name__ == '__main__':
    app.run(threaded=True)
