from datetime import datetime
from pathlib import Path
from typing import Any

from werkzeug.wrappers import Request
from werkzeug.utils import secure_filename

import config
from ontology_generator_evaluator.models.run_model import RunModel
from ontology_generator_evaluator.services.ai_providers import AI_PROVIDERS
from ontology_generator_evaluator.services.lib_providers import LIB_PROVIDERS

config.load_config()


def _generate_timestamped_name(prefix: str) -> str:
    return f"{prefix}.{datetime.now():%Y-%m-%d.%H-%M-%S}"


def _handle_post_request(request: Request) -> RunModel:
    run_model = RunModel.from_request(request.form)

    if not run_model.name:
        run_model.name = _generate_timestamped_name("run")

    if run_model.id:
        input_docs = request.files.get("input_docs")
        if input_docs:
            # TODO: add validation and error handling for input_docs
            files_path = Path(config.STORAGE_PATH) / run_model.id
            files_path.mkdir(parents=True, exist_ok=True)

            raw_filename = input_docs.filename or _generate_timestamped_name("file")
            destination = files_path / secure_filename(raw_filename)
            input_docs.save(destination)

            destination_str = str(destination)
            if destination_str not in run_model.input_sources:
                run_model.input_sources = [destination_str]

        run_model.save()

    return run_model


def get_dashboard_data(request: Request) -> dict[str, Any]:
    errors: dict[str, str] = {}

    if request.method == "GET":
        run_id = request.args.get("run")
        run_model = (
            RunModel.load(run_id)
            if run_id
            else RunModel(_generate_timestamped_name("run"))
        )
    else:
        run_model = _handle_post_request(request)

    previous_runs = [{"value": path.stem, "text": path.stem} for path in RunModel.list()]
    input_source_checkbox_values = [
        {"value": str(file), "text": str(file)} for file in run_model.input_sources
    ]

    return {
        "lib_providers": [{"text": key, "value": key} for key in LIB_PROVIDERS],
        "ai_providers": [{"text": key, "value": key} for key in AI_PROVIDERS],
        "input_source_checkbox_values": input_source_checkbox_values,
        "run_model": run_model,
        "previous_runs": previous_runs,
        "errors": errors,
    }