import os
from datetime import datetime

from werkzeug.utils import secure_filename

import config
from config import load_config
from ontology_generator_evaluator.models.run_model import RunModel
from ontology_generator_evaluator.repositories.run_repository import save_run_model
from ontology_generator_evaluator.services.ai_providers import AI_PROVIDERS
from ontology_generator_evaluator.services.lib_providers import LIB_PROVIDERS

load_config()


def get_dashboard_data(request):
    run_id = request.form.get("run_id", None)
    run_name = request.form.get("run_name", None)
    processing_library = request.form.get("processing_library", "")
    ai_provider = request.form.get("ai_provider", "")
    ai_model = request.form.get("ai_model", "")
    input_sources = request.form.getlist("input_sources")
    processing_prompt = request.form.get("processing_prompt", "")

    run_model = RunModel(
        id=run_id,
        name=run_name,
        processing_library=processing_library,
        ai_provider=ai_provider,
        ai_model=ai_model,
        input_sources=input_sources,
        prompt=processing_prompt,
    )

    errors = {}

    if run_id:
        # save the model - it's got data
        print("Saving model")
        save_run_model(run_model)
    else:
        # create an id for a new model
        run_model.id = 'run.' + datetime.now().strftime("%Y-%m-%d.%H-%M-%S")

    if not run_name:
        run_model.name = 'run.' + datetime.now().strftime("%Y-%m-%d.%H-%M-%S")

    input_data = request.files.get("input_data", None)
    files_path = os.path.join(config.STORAGE_PATH, run_id)
    if input_data:
        # TODO add some validation and error handling for input_data

        filename = secure_filename(
            input_data.filename or 'file.' + datetime.now().strftime("%Y-%m-%d.%H-%M-%S")
        )
        os.makedirs(files_path, exist_ok=True)
        destination = os.path.join(files_path, filename)

        input_data.save(destination)

    # As an expert on content schema and meta data, can you extract the content schema and meta data from the document and return it in TTL format?

    return {
        # select options
        "lib_providers": [{"text": key, "value": key} for key in LIB_PROVIDERS.keys()],
        "ai_providers": [{"text": key, "value": key} for key in AI_PROVIDERS.keys()],
        # model data
        "run_model": run_model,
        "errors": errors
    }
