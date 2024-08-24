import re
import json
from openai import OpenAI
from config.config import OPENAI_API_MODEL, GPT_INSTRUCTION, \
    JSON_KEY_CONFLICTS, JSON_KEY_DIAGNOSES, GPT_INSTRUCTION_PART_2, JSON_KEY_MSO


class GPTModel:
    _client = None

    def __init__(self):
        self._client = OpenAI()
        self._assistant = self._client.beta.assistants.create(
            name="FaultDiagnosis",
            instructions=GPT_INSTRUCTION_PART_2,
            temperature=0.01,
            top_p=1.0,
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
            minimal_conflicts = self._extract_conflicts(self._messages.data[0].content[0].text.value)
            # minimal_diagnoses = self._extract_diagnoses(self._messages.data[0].content[0].text.value)
            return minimal_conflicts, []
            # mso = self._extract_mso(self._messages.data[0].content[0].text.value)
            # return mso, []
        return ['OpenAI Error'], ['OpenAI Error']

    def _extract_conflicts(self, message):
        minimal_conflicts = self._extract_from_message(JSON_KEY_CONFLICTS, message)
        return minimal_conflicts

    def _extract_diagnoses(self, message):
        minimal_diagnoses = self._extract_from_message(JSON_KEY_DIAGNOSES, message)
        return minimal_diagnoses

    def _extract_mso(self, message):
        mso = self._extract_from_message(JSON_KEY_MSO, message)
        return mso

    def _extract_from_message(self, key, message):
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
