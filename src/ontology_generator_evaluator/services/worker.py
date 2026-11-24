import argparse
import json
import logging
import threading
import time
from pathlib import Path

import config
from ontology_generator_evaluator.services import job_queue
from ontology_generator_evaluator.services.ontology_pipeline import build_ontology

logger = logging.getLogger(__name__)


def run_one() -> bool:
    job = job_queue.claim()
    if job is None:
        return False
    job_id, token = job["id"], job["token"]
    stopped = threading.Event()

    def renew():
        while not stopped.wait(job_queue.LEASE_SECONDS / 3):
            if not job_queue.heartbeat(job_id, token):
                logger.error("Lease lost for job %s", job_id)
                return

    heartbeat = threading.Thread(target=renew, daemon=True)
    heartbeat.start()
    output = Path(config.STORAGE_PATH) / "job_results" / job_id / token
    try:
        build_ontology(
            json.loads(job["snapshot"]),
            output,
            lambda stage: job_queue.progress(job_id, token, stage),
        )
        if not job_queue.finish(job_id, token, result_dir=str(output)):
            logger.error("Could not publish job %s: lease lost", job_id)
    except Exception as exc:
        logger.exception("Job %s failed", job_id)
        job_queue.finish(job_id, token, error=str(exc))
    finally:
        stopped.set()
        heartbeat.join()
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Process ontology generation jobs.")
    parser.add_argument("--once", action="store_true", help="Process at most one job and exit.")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    while True:
        processed = run_one()
        if args.once:
            return
        if not processed:
            time.sleep(2)


if __name__ == "__main__":
    main()
