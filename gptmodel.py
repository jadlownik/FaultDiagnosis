from openai import OpenAI
from config import OPENAI_API_KEY


class GPTModel:
    _client = None

    def __init__(self):
        self._client = OpenAI()
        self._client.api_key = OPENAI_API_KEY
        self._client.models
