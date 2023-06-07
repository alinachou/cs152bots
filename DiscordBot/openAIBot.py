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