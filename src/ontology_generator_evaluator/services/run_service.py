from datetime import datetime
from pathlib import Path

from werkzeug.utils import secure_filename

import config
from config import load_config
from ontology_generator_evaluator.models.run_model import RunModel
from ontology_generator_evaluator.repositories.run_repository import (
    list_runs,
    load_run_model,
    save_run_model,
)
from ontology_generator_evaluator.services.ai_providers import AI_PROVIDERS
from ontology_generator_evaluator.services.lib_providers import LIB_PROVIDERS

load_config()


def get_dashboard_data(request):
    errors = {}
    if request.method == "GET":
        run_id = request.args.get("run")
        if run_id:
            run_model = load_run_model(run_id)
        else:
            run_model = RunModel(
                id="run." + datetime.now().strftime("%Y-%m-%d.%H-%M-%S"),
                name="",
                processing_library="",
                ai_provider="",
                ai_model="",
            )
    else:
        run_model = RunModel.from_request(request.form)

        if not run_model.name:
            run_model.name = "run." + datetime.now().strftime("%Y-%m-%d.%H-%M-%S")

        if run_model.id:
            input_docs = request.files.get("input_docs", None)
            files_path = Path(config.STORAGE_PATH) / run_model.id
            if input_docs:
                # TODO add some validation and error handling for input_docs

                filename = secure_filename(
                    input_docs.filename or "file." + datetime.now().strftime("%Y-%m-%d.%H-%M-%S")
                )
                files_path.mkdir(parents=True, exist_ok=True)
                destination = files_path / filename
                input_docs.save(destination)
                if destination not in run_model.input_sources:
                    run_model.input_sources = [str(destination)]
            save_run_model(run_model)

    previous_runs = [
        {
            "value": Path(path).stem,
            "text": Path(path).stem,
        }
        for path in list_runs()
    ]

    input_source_checkbox_values = [
        {
            "value": str(file),
            "text": file,
        }
        for file in run_model.input_sources
    ]

    return {
        # select options
        "lib_providers": [{"text": key, "value": key} for key in LIB_PROVIDERS.keys()],
        "ai_providers": [{"text": key, "value": key} for key in AI_PROVIDERS.keys()],
        "input_source_checkbox_values": input_source_checkbox_values,
        # model data
        "run_model": run_model,
        "previous_runs": previous_runs,
        "errors": errors,
    }
