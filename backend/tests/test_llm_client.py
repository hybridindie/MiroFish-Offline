from types import SimpleNamespace

from app.utils.llm_client import LLMClient


class FakeStream:
    def __init__(self, chunks):
        self._chunks = chunks
        self.closed = False

    def __iter__(self):
        return iter(self._chunks)

    def close(self):
        self.closed = True


class FakeCompletions:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.result


class FakeHttpResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeHttpClient:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def post(self, url, json):
        self.calls.append({'url': url, 'json': json})
        return FakeHttpResponse(self.payload)


def make_client(base_url, model, completions):
    client = object.__new__(LLMClient)
    client.api_key = 'test'
    client.base_url = base_url
    client.model = model
    client.timeout = 180.0
    client._num_ctx = 8192
    client.client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    client.http_client = None
    return client


def make_chunk(content=None, reasoning_content=None):
    delta = SimpleNamespace(content=content, reasoning_content=reasoning_content)
    choice = SimpleNamespace(delta=delta)
    return SimpleNamespace(choices=[choice])


def test_chat_streams_ollama_and_aggregates_chunks(monkeypatch):
    monkeypatch.setattr('app.utils.llm_client.Config.LLM_STREAM_RESPONSES', 'auto')
    stream = FakeStream([
        make_chunk(content='<think>reasoning</think>{"entities":['),
        make_chunk(content='],"relations":[]}'),
    ])
    completions = FakeCompletions(stream)
    client = make_client('https://ollama.example/v1', 'qwen3.5:27b', completions)

    response = client.chat(
        messages=[{"role": "user", "content": "extract"}],
        temperature=0.1,
        max_tokens=256,
        response_format={"type": "json_object"},
    )

    assert response == '{"entities":[],"relations":[]}'
    assert stream.closed is True
    assert completions.calls[0]['stream'] is True
    assert 'response_format' not in completions.calls[0]
    assert completions.calls[0]['extra_body'] == {'options': {'num_ctx': 8192}}


def test_chat_streams_reasoning_models_in_auto_mode(monkeypatch):
    monkeypatch.setattr('app.utils.llm_client.Config.LLM_STREAM_RESPONSES', 'auto')
    stream = FakeStream([
        make_chunk(reasoning_content='<think>plan</think>'),
        make_chunk(content='{"ok":true}'),
    ])
    completions = FakeCompletions(stream)
    client = make_client('https://api.example.com/v1', 'qwen3:14b', completions)

    response = client.chat(
        messages=[{"role": "user", "content": "extract"}],
        temperature=0.1,
        max_tokens=128,
    )

    assert response == '{"ok":true}'
    assert completions.calls[0]['stream'] is True


def test_chat_keeps_non_streamed_path_when_disabled(monkeypatch):
    monkeypatch.setattr('app.utils.llm_client.Config.LLM_STREAM_RESPONSES', 'false')
    result = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content='{"ok": true}'))]
    )
    completions = FakeCompletions(result)
    client = make_client('https://api.openai.com/v1', 'gpt-4o-mini', completions)

    response = client.chat(
        messages=[{"role": "user", "content": "extract"}],
        temperature=0.1,
        max_tokens=128,
        response_format={"type": "json_object"},
    )

    assert response == '{"ok": true}'
    assert 'stream' not in completions.calls[0]
    assert completions.calls[0]['response_format'] == {'type': 'json_object'}


def test_parse_json_response_prefers_expected_schema():
    client = object.__new__(LLMClient)
    noisy = '''Thinking Process:\n{"name":"Alice","type":"Person"}\nAnd final output:\n{"entities":[],"relations":[]}'''

    parsed = client._parse_json_response(noisy, expected_keys=['entities', 'relations'])

    assert parsed == {'entities': [], 'relations': []}


def test_chat_json_uses_native_ollama_api_for_structured_calls():
    client = make_client('https://ollama.example/v1', 'qwen3.5:27b', FakeCompletions(None))
    client.http_client = FakeHttpClient({
        'message': {
            'content': '```json\n{"entities": [], "relations": []}\n```'
        }
    })

    parsed = client.chat_json(
        messages=[{'role': 'user', 'content': 'extract'}],
        temperature=0.1,
        max_tokens=256,
        expected_keys=['entities', 'relations'],
    )

    assert parsed == {'entities': [], 'relations': []}
    assert client.http_client.calls[0]['url'] == 'https://ollama.example/api/chat'
    assert client.http_client.calls[0]['json']['think'] is False
    assert client.http_client.calls[0]['json']['options']['num_predict'] == 256