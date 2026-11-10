from pathlib import Path

from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parent / ".env"


def load_config() -> None:
    load_dotenv(ENV_FILE, override=False)
