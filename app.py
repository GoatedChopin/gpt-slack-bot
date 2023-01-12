import os
import openai
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


openai.api_key = os.getenv("OPENAI_API_KEY")

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)


def generate_prompt(prompt) -> str:
    return prompt


def ask_gpt(prompt) -> str:
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=generate_prompt(prompt),
        temperature=0.6,
        max_tokens=250,
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


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
