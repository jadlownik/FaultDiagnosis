from openai import OpenAI
from config.config import OPENAI_API_MODEL, GPT_INSTRUCTIONS, \
    JSON_KEY_CONFLICTS, JSON_KEY_DIAGNOSIS


class GPTModel:
    _client = None

    def __init__(self):
        self._client = OpenAI()
        return
        self._assistant = self._client.beta.assistants.create(
            name="FaultDiagnosis",
            instructions=GPT_INSTRUCTIONS,
            tools=[{"type": "code_interpreter"}],
            model=OPENAI_API_MODEL,
        )

        self._thread = self._client.beta.threads.create()

    def get_solution(self, input_data):
        self._message = self._client.beta.threads.messages.create(
            thread_id=self._thread.id,
            role="user",
            content=input_data
        )
        run = self._client.beta.threads.runs.create_and_poll(
            thread_id=self._thread.id,
            assistant_id=self._assistant.id,
            instructions="Use instructions from assistant."
        )

        if run.status == 'completed':
            messages = self._client.beta.threads.messages.list(
                thread_id=self._thread.id
            )
            print(messages)
        else:
            print(run.status)

        return messages[JSON_KEY_CONFLICTS], messages[JSON_KEY_DIAGNOSIS]
