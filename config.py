import os.path
from pathlib import Path

from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parent / ".env"
STORAGE_PATH = 'storage'
RUN_MODEL_STORAGE_PATH = os.path.join(STORAGE_PATH, 'run_model')


def load_config() -> None:
    load_dotenv(ENV_FILE, override=False)


def get_storage_path() -> Path:
    return Path(STORAGE_PATH)


def get_run_model_storage_path() -> Path:
    return Path(RUN_MODEL_STORAGE_PATH)
