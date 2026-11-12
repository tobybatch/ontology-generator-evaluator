from flask import Blueprint, render_template, request

from flask import request

from ontology_generator_evaluator.services.run_service import get_dashboard_data, AI_PROVIDERS

run_bp = Blueprint("run", __name__)


@run_bp.route("/", methods=["GET", "POST"])
def index():
    data = get_dashboard_data(request)
    return render_template("index.html", **data)


@run_bp.route("/update_ai_models")
def update_ai_models():
    provider_name = request.args["ai_provider"]
    provider = AI_PROVIDERS[provider_name]
    return provider.get_models()
