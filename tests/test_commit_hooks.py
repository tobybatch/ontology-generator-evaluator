import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("message", "valid"),
    [
        ("feat: add a provider\n", True),
        ("fix(api): handle errors\n\nExplain the change.\n", True),
        ("docs: update the guide\n", True),
        ("Merge branch 'main'\n", True),
        ("not a conventional commit\n", False),
        ("feature: add a provider\n", False),
        ("feat: \n", False),
        ("feat:\nbody is not a subject\n", False),
        ("fix(): empty scope\n", False),
    ],
)
def test_commit_message_hook(tmp_path, message, valid):
    message_file = tmp_path / "COMMIT_EDITMSG"
    message_file.write_text(message, encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pre_commit",
            "run",
            "commitizen",
            "--all-files",
            "--hook-stage",
            "commit-msg",
            "--commit-msg-filename",
            str(message_file),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert (result.returncode == 0) is valid, result.stdout + result.stderr
    assert ("Passed" if valid else "Failed") in result.stdout, result.stdout + result.stderr


def test_installed_hooks_validate_git_commits(tmp_path):
    env = os.environ | {
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "SKIP": "ruff,ruff-format",
    }

    def run(*args):
        return subprocess.run(args, cwd=tmp_path, env=env, capture_output=True, text=True, check=True)

    run("git", "init", "--template=")
    run("git", "config", "user.name", "Test")
    run("git", "config", "user.email", "test@example.com")
    for filename in (".pre-commit-config.yaml", "pyproject.toml"):
        shutil.copy(PROJECT_ROOT / filename, tmp_path / filename)
    (tmp_path / ".venv").symlink_to(Path(sys.prefix).resolve(), target_is_directory=True)
    run("git", "add", ".pre-commit-config.yaml", "pyproject.toml")
    run(sys.executable, "-m", "pre_commit", "install")

    for hook in ("pre-commit", "commit-msg"):
        assert (tmp_path / ".git" / "hooks" / hook).is_file()

    invalid = subprocess.run(
        ["git", "commit", "-m", "invalid message"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert invalid.returncode != 0
    assert "commitizen" in invalid.stdout + invalid.stderr
    run("git", "commit", "-m", "feat: valid message")
