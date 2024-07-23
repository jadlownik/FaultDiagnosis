import json
import re
from openai import OpenAI
from config.config import OPENAI_API_MODEL, GPT_SYSTEM_DESC, GPT_EXAMPLES, \
                   JSON_KEY_CONFLICTS, JSON_KEY_DIAGNOSIS, GPT_KNOWN_MSO, \
                   GIVE_ME_FUCKING_JSON, GPT_TO_MSO_GENERATE


class GPTModel:
    _client = None
    _messages = None

    def __init__(self):
        self._client = OpenAI()

    def get_solution(self,input_data):
        # start_message = f'{GPT_SYSTEM_DESC}\
        #                   {GPT_EXAMPLES}'
        start_message = GPT_TO_MSO_GENERATE
        self._messages = [{'role': 'system', 'content': start_message}]
        self._messages.append({'role': 'user', 'content': mso_data})
        response = self._client.chat.completions.create(
            model=f'{OPENAI_API_MODEL}',
            messages=self._messages
        )
        print(response.choices[0].message.content)
        json_response = self._extract_json_from_text(response.choices[0].message.content)
        self._messages.clear()
        
        start_message = GPT_KNOWN_MSO
        self._messages = [{'role': 'system', 'content': start_message}]
        self._messages.append({'role': 'user', 'content': input_data})
        response = self._client.chat.completions.create(
            model=f'{OPENAI_API_MODEL}',
            messages=self._messages
        )

        raw_response = response.choices[0].message.content        
        json_response = self._extract_json_from_text(raw_response)

        # if JSON_KEY_CONFLICTS not in json_response or JSON_KEY_DIAGNOSIS not in json_response:
        #     json_response = self._check_if_all_parameters_in_output(json_response)

        self._messages.clear()

        return json_response[JSON_KEY_CONFLICTS], [] # json_response[JSON_KEY_DIAGNOSIS]

    def _check_if_all_parameters_in_output(self, json_response):
        second_message = 'Your answer was missing '
        second_message += JSON_KEY_CONFLICTS + " " if JSON_KEY_CONFLICTS not in json_response else ""
        second_message += JSON_KEY_DIAGNOSIS + " " if JSON_KEY_DIAGNOSIS not in json_response else ""
        self._messages.append({'role': 'user', 'content': second_message})
        response = self._client.chat.completions.create(
            model=f'{OPENAI_API_MODEL}',
            response_format={'type': 'json_object'},
            messages=self._messages
        )
        return json.loads(response.choices[0].message.content)

    def _extract_json_from_text(self, text):
        json_pattern = re.compile(r'```json\n(.*?)\n```', re.DOTALL)

        match = json_pattern.search(text)

        json_data = match.group(1)
        text = json.loads(json_data.replace("'", '"'))
        return text
