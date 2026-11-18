import os

from config import load_config


def test_loads_project_env_from_another_working_directory(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=test-key\n", encoding="utf-8")
    monkeypatch.setattr("config.ENV_FILE", env_file)
    monkeypatch.setattr(os, "getcwd", lambda: "/")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    load_config()

    assert os.environ["OPENAI_API_KEY"] == "test-key"


def test_preserves_existing_environment_variables(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=file-key\n", encoding="utf-8")
    monkeypatch.setattr("config.ENV_FILE", env_file)
    monkeypatch.setenv("OPENAI_API_KEY", "existing-key")

    load_config()

    assert os.environ["OPENAI_API_KEY"] == "existing-key"


def test_missing_env_file_is_optional(tmp_path, monkeypatch):
    monkeypatch.setattr("config.ENV_FILE", tmp_path / ".env")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    load_config()

    assert "OPENAI_API_KEY" not in os.environ
