from config import load_config
from ontology_generator_evaluator.services.ai_providers import AI_PROVIDERS
from ontology_generator_evaluator.services.lib_providers import LIB_PROVIDERS

load_config()


def get_dashboard_data(request):
    run_id = request.form.get("run_id", "")
    run_name = request.form.get("run_name", "")
    library = request.form.get("library", "")
    ai_provider = request.form.get("ai_provider", "")
    ai_model = request.form.get("ai_model", "")
    input_sources = request.form.getlist("input_sources")
    processing_prompt = request.form.get("processing_prompt", "")

    errors = {}

    # As an expert on content schema and meta data, can you extract the content schema and meta data from the document and return it in TTL format?

    return {
        # select options
        "lib_providers": [{"text": key, "value": key} for key in LIB_PROVIDERS.keys()],
        "ai_providers": [{"text": key, "value": key} for key in AI_PROVIDERS.keys()],
        # model data
        "run_id": run_id,
        "run_name": run_name,
        "lib_provider": library,
        "ai_provider": ai_provider,
        "ai_model": ai_model,
        "input_sources": input_sources,
        "processing_prompt": processing_prompt,
        "errors": errors
    }
