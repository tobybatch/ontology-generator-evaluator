from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from werkzeug.utils import secure_filename
from werkzeug.wrappers import Request

import config
from ontology_generator_evaluator.models.run_model import RunModel
from ontology_generator_evaluator.models.run_status_model import RunStatusModel
from ontology_generator_evaluator.services import job_queue
from ontology_generator_evaluator.services.ai_providers import AI_PROVIDERS
from ontology_generator_evaluator.services.lib_providers import LIB_PROVIDERS

config.load_config()


def _generate_timestamped_name(prefix: str) -> str:
    return f"{prefix}.{datetime.now():%Y-%m-%d.%H-%M-%S}"


def get_asset_storage_path(run_model_id: str) -> Path:
    return Path(config.STORAGE_PATH) / run_model_id


def _next_file_name(file_name: str):
    counter = file_name.split("_")[-1].split(".")[0]
    next_counter = str(int(counter) + 1).zfill(6)
    return f"chunk_{next_counter}.txt"


def _get_next_file(target_path):
    files = sorted([f.name for f in target_path.iterdir() if f.is_file()])
    return _next_file_name(str(files[-1])) if files else "chunk_000000.txt"


def _handle_post_request(request: Request) -> RunModel:
    run_model = RunModel.from_request(request.form)
    removed = set(request.form.getlist("documents"))
    run_model.input_sources = [source for source in run_model.input_sources if source not in removed]

    if not run_model.name:
        run_model.name = _generate_timestamped_name("run")

    if run_model.id:
        input_docs = request.files.get("input_docs")
        if input_docs:
            # TODO: add validation and error handling for input_docs
            files_path = get_asset_storage_path(run_model.id)
            files_path.mkdir(parents=True, exist_ok=True)

            raw_filename = input_docs.filename or _generate_timestamped_name("file")
            destination = files_path / secure_filename(raw_filename)
            input_docs.save(destination)

            destination_str = str(destination)
            if destination_str not in run_model.input_sources:
                run_model.input_sources.append(destination_str)

        run_model.save()

    return run_model


def get_dashboard_data(request: Request) -> dict[str, Any]:
    errors: dict[str, str] = {}

    if request.method == "GET":
        run_id = request.args.get("run")
        run_model = RunModel.load(run_id) if run_id else RunModel(_generate_timestamped_name("run"))
    else:
        run_model = _handle_post_request(request)

    previous_runs = [{"value": path.stem, "text": path.stem} for path in RunModel.list()]
    input_source_checkbox_values = [{"value": str(file), "text": str(file)} for file in run_model.input_sources]

    return {
        "lib_providers": [{"text": key, "value": key} for key in LIB_PROVIDERS],
        "ai_providers": [{"text": key, "value": key} for key in AI_PROVIDERS],
        "input_source_checkbox_values": input_source_checkbox_values,
        "run_model": run_model,
        "previous_runs": previous_runs,
        "errors": errors,
    }


def create_snapshot(run_model: RunModel) -> dict[str, Any]:
    if run_model.processing_library not in LIB_PROVIDERS:
        raise ValueError("Select a valid processing library.")
    if run_model.ai_provider not in AI_PROVIDERS:
        raise ValueError("Select a valid AI provider.")
    if not run_model.ai_model.strip() or not run_model.embedding_model.strip():
        raise ValueError("Select a generation model and an embedding model.")
    if not run_model.prompt.strip() or len(run_model.prompt) > 10000:
        raise ValueError("Enter a processing prompt of at most 10,000 characters.")
    iri = run_model.base_iri
    parsed = urlsplit(iri)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or not iri.endswith(("/", "#"))
        or parsed.query
        or any(c.isspace() or c in '<>"{}|\\^`' for c in iri)
        or (parsed.fragment and not iri.endswith("#"))
    ):
        raise ValueError("Enter an HTTP(S) base IRI ending in / or #.")
    if not run_model.input_sources:
        raise ValueError("Add at least one UTF-8 text document.")
    sources = [{"path": source, "text": Path(source).read_text(encoding="utf-8")} for source in run_model.input_sources]
    return {"run": run_model.to_dict(), "sources": sources}


def enqueue_run(run_model: RunModel) -> str:
    return job_queue.enqueue(run_model.id, create_snapshot(run_model))


def start_run(run_id: str) -> dict[str, Any]:
    run_model: RunModel = RunModel.load(run_id)
    if not run_model:
        raise Exception("Run model not found for run_id: " + run_id)
    chunker = LIB_PROVIDERS.get(run_model.processing_library, None)
    if not chunker:
        raise Exception("Chunker not found for processing_library: " + run_model.processing_library)
    status: RunStatusModel = RunStatusModel.load_or_create(run_model.id)

    for source in run_model.input_sources:
        if source in status.source_processed:
            continue

        text = Path(source).read_text(encoding="utf-8")
        chunks = chunker.split_text(text)
        source_id = sha256(source.encode("utf-8")).hexdigest()
        chunk_path = get_asset_storage_path(run_model.id) / "chunks" / source_id
        chunk_path.mkdir(parents=True, exist_ok=True)

        chunk_names = set()
        for index, chunk in enumerate(chunks):
            name = f"chunk_{index:06d}.txt"
            (chunk_path / name).write_text(chunk, encoding="utf-8")
            chunk_names.add(name)

        for old_chunk in chunk_path.glob("chunk_*.txt"):
            if old_chunk.stem.removeprefix("chunk_").isdigit() and old_chunk.name not in chunk_names:
                old_chunk.unlink()

        status.source_processed.append(source)
        status.save()

    return {"run_model": run_model, "status": status}
