import logging
import time

from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

import doublemap

# 9 Knights Landing / Research Park
route_9_id = 13
route_5_id = 43
cdl_stop_id = 82
research_pavilion_stop_id = 31

# process_before_response must be True when running on FaaS
app = App(process_before_response=True)

@app.event("app_home_opened")
def update_home_tab(client, event, logger):
  try:
    # views.publish is the method that your app uses to push a view to the Home tab
    client.views_publish(
      # the user that opened your app's app home
      user_id=event["user"],
      # the view object that appears in the app home
      view={
        "type": "home",
        "callback_id": "home_view",

        # body of the view
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Welcome to your _App's Home tab_* :tada:"
            }
          },
          {
            "type": "divider"
          },
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "This button won't do much for now but you can set up a listener for it using the `actions()` method and passing its unique `action_id`. See an example in the `examples` folder within your Bolt app."
            }
          },
          {
            "type": "actions",
            "elements": [
              {
                "type": "button",
                "text": {
                  "type": "plain_text",
                  "text": "Click me!"
                }
              }
            ]
          }
        ]
      }
    )

  except Exception as e:
    logger.error(f"Error publishing home tab: {e}")

@app.middleware  # or app.use(log_request)
def log_request(logger, body, next):
    logger.debug(body)
    return next()


command = "/hello-bolt-python-lambda"


def respond_to_slack_within_3_seconds(body, ack):
    if body.get("text") is None:
        ack(f":x: Usage: {command} (description here)")
    else:
        title = body["text"]
        ack(f"Accepted! (task: {title})")


def process_request(respond, body):
    time.sleep(5)
    title = body["text"]
    respond(f"Completed! (task: {title})")


app.command(command)(ack=respond_to_slack_within_3_seconds, lazy=[process_request])

@app.command("/bus")
def bus_command(ack, body):
    route_9 = doublemap.get_route(route_9_id)
    route_5 = doublemap.get_route(route_5_id)
    is_route_9_active = route_9["active"]
    is_route_5_active = route_5["active"]
    if body.get("text") is None or body["text"] == "":
        if is_route_5_active:
            res = "CDL Stop: Next bus in "
            cdl_etas = doublemap.get_etas(cdl_stop_id)
            for eta in cdl_etas:
                last_stop_id = doublemap.get_last_stop(eta["bus_id"])
                last_stop = "Unknown"
                stops_left = 0
                if last_stop_id == 81:
                    last_stop = "CDL"
                    stops_left = 4
                elif last_stop_id == 95:
                    last_stop = "9 at Central"
                    stops_left = 3
                elif last_stop_id == 29:
                    last_stop = "Village at Science Dr"
                    stops_left = 2
                elif last_stop_id == 30:
                    last_stop = "Research Pavilion"
                    stops_left = 1
                elif last_stop_id == 31:
                    last_stop = "UCF"
                    stops_left = 0
                res += f"\n\t{eta['avg']} minutes, last stop: {last_stop}, {stops_left} stops left"
        else:
            res = "Route 5 is not active"
        if is_route_9_active:
            pavilion_etas = doublemap.get_etas(research_pavilion_stop_id)
            res += "\nResearch Pavilion Stop: Next bus in "
            for eta in pavilion_etas:
                last_stop = doublemap.get_last_stop(eta["bus_id"])
                res += f"\n\t{eta['avg']} minutes, last stop: {last_stop}"
        else:
            res += "\nRoute 9 is not active"
    else:
        if is_route_5_active:
            stop_id = int(body["text"])
            etas = doublemap.get_etas(stop_id)
            res = "Next bus in "
            for eta in etas:
                res += f"{eta['avg']} minutes, "
            res = res[:-2]
        else:
            res = "Route 5 is not active"

    ack(res)


SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)


def handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)


# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***

# rm -rf vendor && cp -pr ../../src/* vendor/
# pip install python-lambda
# lambda deploy --config-file aws_lambda_config.yaml --requirements requirements.txt