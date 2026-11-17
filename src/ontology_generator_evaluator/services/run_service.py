from datetime import datetime

from config import load_config
from ontology_generator_evaluator.models.run_model import RunModel
from ontology_generator_evaluator.services.ai_providers import AI_PROVIDERS
from ontology_generator_evaluator.services.lib_providers import LIB_PROVIDERS

load_config()


def get_dashboard_data(request):
    run_id = request.form.get("run_id", None)
    run_name = request.form.get("run_name", None)
    library = request.form.get("library", "")
    ai_provider = request.form.get("ai_provider", "")
    ai_model = request.form.get("ai_model", "")
    input_sources = request.form.getlist("input_sources")
    processing_prompt = request.form.get("processing_prompt", "")

    run_model = RunModel(
        id=run_id,
        name=run_name,
        library=library,
        ai_provider=ai_provider,
        ai_model=ai_model,
        input_sources=input_sources,
        prompt=processing_prompt,
    )

    errors = {}

    if not run_id:
        run_id = 'run-' + datetime.now().strftime("%Y-%m-%d.%H-%M-%S")

    if not run_name:
        run_name = 'run-' + datetime.now().strftime("%Y-%m-%d.%H-%M-%S")

    # As an expert on content schema and meta data, can you extract the content schema and meta data from the document and return it in TTL format?

    return {
        # select options
        "lib_providers": [{"text": key, "value": key} for key in LIB_PROVIDERS.keys()],
        "ai_providers": [{"text": key, "value": key} for key in AI_PROVIDERS.keys()],
        # model data
        "run_model": run_model,
        "errors": errors
    }
