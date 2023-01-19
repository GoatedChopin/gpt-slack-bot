import os
import openai
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import json

# import logging
# logging.basicConfig(level=logging.DEBUG)

openai.api_key = os.getenv("OPENAI_API_KEY")

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)


def find_val(key, hashmap):
    for k, v in hashmap.items():
        if k == key:
            return hashmap[k]
        elif type(v) == dict:
            if (subres := find_val(key, v)) is not None:
                return subres
        elif type(v) == list:
            for element in v:
                if type(element) == dict and (subres := find_val(key, element)) is not None:
                    return subres
    return None


def generate_prompt(prompt) -> str:
    return prompt


def ask_gpt(prompt, temperature=0.6, max_tokens=250) -> str:
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=generate_prompt(prompt),
        temperature=temperature,
        max_tokens=max_tokens,
        )
    return response


@app.event("app_mention")
def handle_gpt_mention(body, say, logger):
    logger.info(body)
    print(body)
    response = ask_gpt(body["event"]["text"])
    logger.info(response)
    print(response.choices)
    say(str(response.choices[0].text))


@app.command("/ask")
def handle_ask_command(body, ack, respond, client, logger):
    logger.info(body)
    ack(
        text="Accepted!",
        blocks=[
            {
                "type": "section",
                "block_id": "b",
                "text": {
                    "type": "mrkdwn",
                    "text": ":white_check_mark: Accepted!",
                },
            }
        ],
    )

    res = client.views_open(
        trigger_id=body["trigger_id"],
        view=json.dumps({
            "type": "modal",
            "callback_id": "view-id",
            "title": {
                "type": "plain_text",
                "text": "My App",
            },
            "submit": {
                "type": "plain_text",
                "text": "Submit",
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel",
            },
            "blocks": [
                {
                    "block_id": "channel_select_block",
                    "type": "input",
                    "optional": False,
                    "label": {
                        "type": "plain_text",
                        "text": "Select a channel to post the result on"
                    },
                    "element": {
                        "action_id": "channel_select_action_id",
                        "type": "channels_select",
                        "response_url_enabled": True
                    }
                },
                {
                    "type": "input",
                    "element": {"type": "plain_text_input", "action_id": "prompt"},
                    "label": {
                        "type": "plain_text",
                        "text": "Prompt",
                    },
                },
                {
                    "type": "input",
                    "element": {
                        "type": "number_input",
                        "is_decimal_allowed": False,
                        "action_id": "response_length",
                        "min_value": "50",
                        "max_value": "500"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Response Length (Characters)",
                        "emoji": True
                    }
                },
                {
                    "type": "input",
                    "element": {
                        "type": "number_input",
                        "is_decimal_allowed": True,
                        "action_id": "temperature",
                        "min_value": "0",
                        "max_value": "1"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Temperature",
                        "emoji": True
                    }
                },
            ],
        })
    )
    logger.info(res)


@app.view("view-id")
def handle_view_submission_events(ack, body, respond, logger):
    ack()

    channel = find_val("channel_id", body)

    answers = list(body["view"]["state"]["values"].values())
    prompt = answers[1]["prompt"]["value"]
    max_tokens = answers[2]["response_length"]["value"]
    temperature = answers[3]["temperature"]["value"]

    response = ask_gpt(prompt, float(temperature), int(max_tokens))
    response = str(response.choices[0].text)

    app.client.chat_postMessage(channel=channel, text="Prompt:\n{}\nResponse: {}".format(prompt, response))


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
