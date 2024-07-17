import json
from openai import OpenAI
from config.config import OPENAI_API_MODEL, GPT_SYSTEM_DESC, GPT_EXAMPLES, \
                   JSON_KEY_CONFLICTS, JSON_KEY_DIAGNOSIS


class GPTModel:
    _client = None
    _messages = None

    def __init__(self):
        self._client = OpenAI()

    def get_solution(self, fol):
        start_message = f'{GPT_SYSTEM_DESC}\
                          {GPT_EXAMPLES}'
        self._messages = [{'role': 'system', 'content': start_message}]
        self._messages.append({'role': 'user', 'content': fol})
        response = self._client.chat.completions.create(
            model=f'{OPENAI_API_MODEL}',
            response_format={'type': 'json_object'},
            messages=self._messages
        )
        json_response = json.loads(response.choices[0].message.content)

        if JSON_KEY_CONFLICTS not in json_response or JSON_KEY_DIAGNOSIS not in json_response:
            json_response = self._check_if_all_parameters_in_output(json_response)

        self._messages.clear()

        return json_response[JSON_KEY_CONFLICTS], json_response[JSON_KEY_DIAGNOSIS]

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
