import re
import json
from openai import OpenAI
from config.config import OPENAI_API_MODEL, GPT_INSTRUCTION, GPT_INSTRUCTION_PART_1, \
    GPT_INSTRUCTION_PART_2, GPT_INSTRUCTION_PART_3, \
    JSON_KEY_CONFLICTS, JSON_KEY_DIAGNOSES, JSON_KEY_MSO, ACTUAL_PART
from enums import PartEnum


class GPTModel:
    _client = None

    def __init__(self):
        return
        self._client = OpenAI()
        self._assistant = self._client.beta.assistants.create(
            name="FaultDiagnosis",
            instructions=GPT_INSTRUCTION if ACTUAL_PART == PartEnum.ALL.value else
            GPT_INSTRUCTION_PART_1 if ACTUAL_PART == PartEnum.MSO.value else
            GPT_INSTRUCTION_PART_2 if ACTUAL_PART == PartEnum.MINIMAL_CONFLICTS.value else
            GPT_INSTRUCTION_PART_3 if ACTUAL_PART == PartEnum.MINIMAL_DIAGNOSES.value else
            "",
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
            if ACTUAL_PART == PartEnum.MSO.value:
                gpt_mso = self._extract_mso(self._messages.data[0].content[0].text.value)
                return gpt_mso, [], []
            elif ACTUAL_PART == PartEnum.MINIMAL_CONFLICTS.value:
                gpt_minimal_conflicts = self._extract_conflicts(self._messages.data[0].content[0].text.value)
                return [], gpt_minimal_conflicts, []
            elif ACTUAL_PART == PartEnum.MINIMAL_DIAGNOSES.value:
                gpt_minimal_diagnoses = self._extract_diagnoses(self._messages.data[0].content[0].text.value)
                return [], [], gpt_minimal_diagnoses
            elif ACTUAL_PART == PartEnum.ALL.value:
                gpt_mso = self._extract_mso(self._messages.data[0].content[0].text.value)
                gpt_minimal_conflicts = self._extract_conflicts(self._messages.data[0].content[0].text.value)
                gpt_minimal_diagnoses = self._extract_diagnoses(self._messages.data[0].content[0].text.value)
                return gpt_mso, gpt_minimal_conflicts, gpt_minimal_diagnoses
        else:
            if ACTUAL_PART == PartEnum.MSO.value:
                return ['OpenAI Error'], [], []
            elif ACTUAL_PART == PartEnum.MINIMAL_CONFLICTS.value:
                return [], ['OpenAI Error'], []
            elif ACTUAL_PART == PartEnum.MINIMAL_DIAGNOSES.value:
                return [], [], ['OpenAI Error']
            elif ACTUAL_PART == PartEnum.ALL.value:
                return ['OpenAI Error'], ['OpenAI Error'], ['OpenAI Error']

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
