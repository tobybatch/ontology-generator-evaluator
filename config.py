import os.path
from pathlib import Path

from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parent / ".env"
STORAGE_PATH = 'storage'
RUN_MODEL_STORAGE_PATH = os.path.join(STORAGE_PATH, 'run_model')
DEFAULT_PROMPT = 'As an expert on content schema and meta data, can you extract the content schema and meta data from the document and return it in TTL format?'
AWS_REGION = 'eu-east-2'


def load_config() -> None:
    load_dotenv(ENV_FILE, override=False)


def get_storage_path() -> Path:
    return Path(STORAGE_PATH)


def get_run_model_storage_path() -> Path:
    return Path(RUN_MODEL_STORAGE_PATH)
