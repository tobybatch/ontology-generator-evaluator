import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from config import load_config
from services.run_service import _get_openai_models


class ConfigTests(unittest.TestCase):
    def test_loads_project_env_from_another_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text("OPENAI_API_KEY=test-key\n", encoding="utf-8")
            with (
                patch("config.ENV_FILE", env_file),
                patch.dict(os.environ, {}, clear=True),
                patch("os.getcwd", return_value="/"),
            ):
                load_config()
                self.assertEqual(os.environ["OPENAI_API_KEY"], "test-key")

    def test_preserves_existing_environment_variables(self):
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text("OPENAI_API_KEY=file-key\n", encoding="utf-8")
            with (
                patch("config.ENV_FILE", env_file),
                patch.dict(os.environ, {"OPENAI_API_KEY": "existing-key"}, clear=True),
            ):
                load_config()
                self.assertEqual(os.environ["OPENAI_API_KEY"], "existing-key")

    def test_missing_env_file_is_optional(self):
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch("config.ENV_FILE", Path(directory) / ".env"),
                patch.dict(os.environ, {}, clear=True),
            ):
                load_config()
                self.assertNotIn("OPENAI_API_KEY", os.environ)

    def test_openai_request_uses_configured_key(self):
        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True),
            patch("services.run_service.requests.get") as get,
        ):
            get.return_value.json.return_value = {"data": []}
            self.assertEqual(_get_openai_models(), [])
            get.assert_called_once_with(
                "https://api.openai.com/v1/models",
                headers={"Authorization": "Bearer test-key"},
            )

    def test_openai_requires_nonempty_key_before_request(self):
        for environment in ({}, {"OPENAI_API_KEY": ""}):
            with (
                self.subTest(environment=environment),
                patch.dict(os.environ, environment, clear=True),
                patch("services.run_service.requests.get") as get,
            ):
                with self.assertRaisesRegex(ValueError, "OPENAI_API_KEY"):
                    _get_openai_models()
                get.assert_not_called()
