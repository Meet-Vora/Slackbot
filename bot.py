import json
import threading
import requests

# Set the webhook_url to the one provided by Slack when you create the
# webhook at https://my.slack.com/services/new/incoming-webhook/
webhook_url = 'https://hooks.slack.com/services/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'
# queuing
# webhook_url = 'https://hooks.slack.com/services/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'
# #shepherd-bot-testing

def team_numbers_on_deck(b1, b2, g1, g2):
    """
    Since many of the slackbot commands will display the same message, this is
    provided for convenience.
    """
    send_plain_message("The following teams are now on deck: \n On the blue side\
, we have team #%i and team #%i \n On the gold side, we\
 have team #%i and team #%i" % (b1, b2, g1, g2))

def send_plain_message(message):
    """
    This will post the message to slack, based on the webhook above.
    """
    slack_data = {'text': message}
    response = requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
        )
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )
