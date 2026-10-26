from types import SimpleNamespace

import app.ask as ask_module


def test_ask_prints_input_and_output_tokens(monkeypatch, capsys):
    response = SimpleNamespace(
        text="回答です",
        usage_metadata=SimpleNamespace(prompt_token_count=123, candidates_token_count=45),
    )

    class FakeModelService:
        def generate_content(self, model, contents):
            assert model == ask_module.MODEL
            assert contents == "テスト質問"
            return response

    class FakeClient:
        def __init__(self, api_key):
            self.api_key = api_key
            self.models = FakeModelService()

    timer_values = iter([0.0, 1.234])
    monkeypatch.setattr(ask_module.genai, "Client", FakeClient)
    monkeypatch.setattr(ask_module, "MODEL", "gemini-test")
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "secret")
    monkeypatch.setattr(ask_module.time, "perf_counter", lambda: next(timer_values))

    result = ask_module.ask("テスト質問")

    assert result == "回答です"
    captured = capsys.readouterr().out
    assert "入力トークン数" in captured
    assert "出力トークン数" in captured
    assert "123" in captured
    assert "45" in captured
    assert "応答時間" in captured
    assert "1.23" in captured or "1.234" in captured
