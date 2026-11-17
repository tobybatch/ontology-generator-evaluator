import os
from datetime import datetime

from werkzeug.utils import secure_filename

import config
from config import load_config
from ontology_generator_evaluator.models.run_model import RunModel
from ontology_generator_evaluator.repositories.run_repository import save_run_model, list_runs
from ontology_generator_evaluator.services.ai_providers import AI_PROVIDERS
from ontology_generator_evaluator.services.lib_providers import LIB_PROVIDERS

from pathlib import Path

load_config()


def get_dashboard_data(request):
    run_id = request.form.get("run_id", None)
    run_name = request.form.get("run_name", None)
    processing_library = request.form.get("processing_library", "")
    ai_provider = request.form.get("ai_provider", "")
    ai_model = request.form.get("ai_model", "")
    processing_prompt = request.form.get("processing_prompt", "")

    run_model = RunModel(
        id=run_id,
        name=run_name,
        processing_library=processing_library,
        ai_provider=ai_provider,
        ai_model=ai_model,
        prompt=processing_prompt,
    )

    errors = {}

    if not run_name:
        run_model.name = 'run.' + datetime.now().strftime("%Y-%m-%d.%H-%M-%S")

    input_source_checkbox_values = []

    if run_id:
        input_docs = request.files.get("input_docs", None)
        files_path = Path(config.STORAGE_PATH) / run_model.id
        if input_docs:
            # TODO add some validation and error handling for input_docs

            filename = secure_filename(
                input_docs.filename or 'file.' + datetime.now().strftime("%Y-%m-%d.%H-%M-%S")
            )
            files_path.mkdir(parents=True, exist_ok=True)
            destination = files_path / filename

            input_docs.save(destination)

        files_path = Path(files_path)
        if files_path.exists():
            run_model.input_sources = [str(file) for file in files_path.iterdir() if file.is_file()]

        input_source_checkbox_values = [
            {
                "value": str(file),
                "text": file,
            }
            for file in run_model.input_sources
        ]
        # save the model - it's got data
        save_run_model(run_model)
    else:
        # create an id for a new model
        run_model.id = 'run.' + datetime.now().strftime("%Y-%m-%d.%H-%M-%S")

    previous_runs = [
        {
            "value": path,
            "text": Path(path).stem,
        }
        for path in list_runs()
    ]


    return {
        # select options
        "lib_providers": [{"text": key, "value": key} for key in LIB_PROVIDERS.keys()],
        "ai_providers": [{"text": key, "value": key} for key in AI_PROVIDERS.keys()],
        "input_source_checkbox_values": input_source_checkbox_values,
        # model data
        "run_model": run_model,
        "previous_runs": previous_runs,
        "errors": errors
    }

    # As an expert on content schema and meta data, can you extract the content schema and meta data from the document and return it in TTL format?
