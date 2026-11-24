import json
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

import config

LEASE_SECONDS = 120


@contextmanager
def _connect():
    path = Path(config.STORAGE_PATH) / "jobs.sqlite3"
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=30)
    db.row_factory = sqlite3.Row
    db.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY, run_id TEXT NOT NULL, snapshot TEXT NOT NULL,
            state TEXT NOT NULL, stage TEXT NOT NULL, error TEXT,
            token TEXT, lease_until REAL, result_dir TEXT, created REAL NOT NULL
        )
    """)
    db.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS one_active_job_per_run
        ON jobs(run_id) WHERE state IN ('queued', 'running')
    """)
    try:
        with db:
            yield db
    finally:
        db.close()


def enqueue(run_id: str, snapshot: dict) -> str:
    job_id = uuid.uuid4().hex
    with _connect() as db:
        try:
            db.execute(
                "INSERT INTO jobs (id, run_id, snapshot, state, stage, created) VALUES (?, ?, ?, ?, ?, ?)",
                (job_id, run_id, json.dumps(snapshot), "queued", "Queued", time.time()),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("This run already has a queued or running job.") from exc
    return job_id


def latest(run_id: str) -> dict | None:
    with _connect() as db:
        row = db.execute(
            "SELECT * FROM jobs WHERE run_id = ? ORDER BY created DESC, rowid DESC LIMIT 1", (run_id,)
        ).fetchone()
    return dict(row) if row else None


def claim() -> dict | None:
    with _connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            """SELECT * FROM jobs
               WHERE state = 'queued' OR (state = 'running' AND lease_until < ?)
               ORDER BY created, rowid LIMIT 1""",
            (time.time(),),
        ).fetchone()
        if row is None:
            return None
        token = uuid.uuid4().hex
        db.execute(
            "UPDATE jobs SET state = 'running', token = ?, lease_until = ?, stage = ? WHERE id = ?",
            (token, time.time() + LEASE_SECONDS, "Starting", row["id"]),
        )
        job = dict(row)
        job["token"] = token
        return job


def heartbeat(job_id: str, token: str) -> bool:
    with _connect() as db:
        cursor = db.execute(
            "UPDATE jobs SET lease_until = ? WHERE id = ? AND token = ? AND state = 'running'",
            (time.time() + LEASE_SECONDS, job_id, token),
        )
        return cursor.rowcount == 1


def progress(job_id: str, token: str, stage: str) -> None:
    with _connect() as db:
        cursor = db.execute(
            "UPDATE jobs SET stage = ? WHERE id = ? AND token = ? AND state = 'running'",
            (stage, job_id, token),
        )
        if cursor.rowcount != 1:
            raise RuntimeError("The job lease was lost.")


def finish(job_id: str, token: str, *, result_dir: str | None = None, error: str | None = None) -> bool:
    with _connect() as db:
        cursor = db.execute(
            """UPDATE jobs SET state = ?, stage = ?, error = ?, result_dir = ?, lease_until = NULL
               WHERE id = ? AND token = ? AND state = 'running'""",
            ("failed" if error else "completed", "Failed" if error else "Completed", error, result_dir, job_id, token),
        )
        return cursor.rowcount == 1
