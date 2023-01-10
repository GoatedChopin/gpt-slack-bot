import os
from slack_bolt import App
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

# Initializes your app with your bot token and signing secret
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
        )
    return response.choices[0].text


@app.event("app_mention")
def handle_gpt_mention(body, say, logger):
    logger.info(body)
    response = ask_gpt(body)
    say(response)


if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))