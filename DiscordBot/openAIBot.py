import json
import os

import openai

class openAIClassifier:
    def __init__(self, openai_key, openai_org):
        openai.api_key = openai_key
        openai.organization = openai_org

    def check_message(self, message):
        prompt = "You are a moderation bot built to determine if messages can be classified as one of the following categories: fraud, harassment, and violence. You will be given messages that have previously been sent in a Discord server, and it will be your job to determine if the message should be reported for any of these categories. You will return either fraud, harassment, or violence if the message should be reported for any of the categories, or will indicate that the message is fine if it should not."
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Hey man wassup"},
                {"role": "assistant", "content": "Ignored"},
                {"role": "user", "content": "You suck, like you're the worst, you deserve nothing and im gonna keep spamming you til you respond. fuckin loser."},
                {"role": "assistant", "content": "Reported. This message has been flagged for: harassment."},
                {"role": "user", "content": "Hey I need ur credit card info for this super good deal i found online; i promise ill pay you back its just my card doesn't work rn"},
                {"role": "assistant", "content": "Reported. This message has been flagged for: fraud."},
                {"role": "user", "content": "I'm gonna beat you up next time i see you. you're dead kiddo."},
                {"role": "assistant", "content": "Reported. This message has been flagged for: violence."},
                {"role": "user", "content": "Hey I hope you're having a great day!"},
                {"role": "assistant", "content": "Ignored"},
                {"role": "user", "content": "hi this is discord support. could you dm me your email and password so i can figure out what's wrong with your account?"},
                {"role": "assistant", "content": "Reported. This message has been flagged for: fraud."},
                {"role": "user", "content": "I hate you so fucking much. you suck and you're ugly and no one loves you"},
                {"role": "assistant", "content": "Reported. This message has been flagged for: harassment."},
                {"role": "user", "content": "i'll literally shoot you like this isnt something to play about; i know where you live"},
                {"role": "assistant", "content": "Reported. This message has been flagged for: violence."},
                {"role": "user", "content": message}
            ]
        )

        output = response['choices'][0]['message']['content']
        return output