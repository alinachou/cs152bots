import json
import os

import openai
from parseDatabase import DataParser

class openAIClassifier:
    def __init__(self, openai_key, openai_org):
        openai.api_key = openai_key
        openai.organization = openai_org
        self.dataParser = DataParser("stored_responses.txt")

    def check_message(self, message):
        all_messages = self.dataParser.createArray()
        all_messages.append({"role": "user", "content": message})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=all_messages
        )

        output = response['choices'][0]['message']['content']
        return output

    # def evaluate_categories(self, message):
    #     prompt = "You are a moderation bot built to determine if messages can be classified as one of the following categories: fraud, harassment, and violence. You will be given messages that have previously been sent in a Discord server, and it will be your job to give it a score between 0 and 1 for each of the categories on whether the message should be flagged as one of the categories. You will return a value between 0 to 1 for each of the categories with 0 being not that category and 1 being definitely that category. Multiple categories can have a score greater than 0, or it can also be possible that the message doesn't get flagged, which all categories will have score of 0."
    #     response = openai.ChatCompletion.create(
    #         model="gpt-3.5-turbo",
    #         messages=[
    #             {"role": "system", "content": prompt},
    #             {"role": "user", "content": message}
    #         ]
    #     )

    #     output = response['choices'][0]['message']['content']
    #     return output