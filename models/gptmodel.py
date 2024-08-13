import re
import json
from openai import OpenAI
from config.config import OPENAI_API_MODEL, GPT_INSTRUCTION, \
    JSON_KEY_CONFLICTS, JSON_KEY_DIAGNOSES


class GPTModel:
    _client = None

    def __init__(self):
        self._client = OpenAI()
        self._assistant = self._client.beta.assistants.create(
            name="FaultDiagnosis",
            instructions=GPT_INSTRUCTION,
            tools=[{"type": "code_interpreter"}],
            model=OPENAI_API_MODEL,
        )

        self._thread = self._client.beta.threads.create()

    def get_solution(self, input_data):
        self._messages = self._client.beta.threads.messages.create(
            thread_id=self._thread.id,
            role="user",
            content=input_data
        )
        self._run = self._client.beta.threads.runs.create_and_poll(
            thread_id=self._thread.id,
            assistant_id=self._assistant.id
        )

        if self._run.status == 'completed':
            self._messages = self._client.beta.threads.messages.list(
                thread_id=self._thread.id
            )
            minimal_conflicts = self.extract_from_message(JSON_KEY_CONFLICTS, self._messages.data[0].content[0].text.value)
            minimal_diagnoses = self.extract_from_message(JSON_KEY_DIAGNOSES, self._messages.data[0].content[0].text.value)
            return minimal_conflicts, minimal_diagnoses
        return ['OpenAI Error'], ['OpenAI Error']

    def extract_from_message(self, key, message):
        json_regex = re.search(r'\{[\s\S]*\}', message)

        if json_regex:
            json_data = json_regex.group(0)
            json_data = json_data.replace("'", '"')
            try:
                data = json.loads(json_data)
                return data.get(key, [])
            except json.JSONDecodeError:
                return ['Decode JSON Error']
        else:
            return ['No JSON']
