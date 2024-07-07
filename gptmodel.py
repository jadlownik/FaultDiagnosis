import json
from openai import OpenAI
from config import OPENAI_API_MODEL, GPT_SYSTEM_DESC, GPT_EXAMPLES


class GPTModel:
    _client = None
    _messages = None

    def __init__(self):
        self._client = OpenAI()
        system_content = f'{GPT_SYSTEM_DESC}\n{GPT_EXAMPLES}'
        self._messages = [{'role': 'system', 'content': system_content}]

    def get_solution(self, fol):
        self._messages.append({'role': 'user', 'content': fol})
        response = self._client.chat.completions.create(
            model=f'{OPENAI_API_MODEL}',
            response_format={'type': 'json_object'},
            messages=self._messages
        )
        json_response = json.loads(response.choices[0].message.content)

        minimal_conflicts = json_response["minimal_conflicts"]
        minimal_diagnosis = json_response["minimal_diagnosis"]

        return minimal_conflicts, minimal_diagnosis
