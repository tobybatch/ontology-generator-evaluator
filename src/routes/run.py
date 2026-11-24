import json
from pathlib import Path

from flask import Blueprint, abort, redirect, render_template, request, send_from_directory, url_for

from ontology_generator_evaluator.models.run_model import RunModel
from ontology_generator_evaluator.services import job_queue
from ontology_generator_evaluator.services.ai_providers import EMBEDDING_MODELS
from ontology_generator_evaluator.services.run_service import (
    AI_PROVIDERS,
    create_snapshot,
    enqueue_run,
    get_dashboard_data,
)

run_bp = Blueprint("run", __name__)


@run_bp.route("/", methods=["GET", "POST"])
def index():
    try:
        data = get_dashboard_data(request)
    except ValueError as exc:
        abort(400, description=str(exc))
    if request.method == "POST" and request.form.get("action") == "start":
        try:
            enqueue_run(data["run_model"])
        except (ValueError, OSError, UnicodeError) as exc:
            data["errors"]["run"] = str(exc)
            return render_template("index.html", **data), 400
        return redirect(url_for("run.start", run_id=data["run_model"].id))
    else:
        return render_template("index.html", **data)


@run_bp.route("/start")
def start():
    run_id = request.args.get("run_id")
    if run_id is None:
        raise Exception("No run id was passed to the start route.")
    try:
        run_model = RunModel.load(run_id)
    except FileNotFoundError:
        abort(404)
    except ValueError:
        abort(400)
    job = job_queue.latest(run_id)
    current = False
    if job and job["state"] == "completed":
        try:
            current = json.loads(job["snapshot"]) == create_snapshot(run_model)
        except (ValueError, OSError, UnicodeError):
            current = False
    return render_template("start_run.html", run_model=run_model, job=job, current=current)


@run_bp.route("/download/<run_id>/<filename>")
def download(run_id: str, filename: str):
    if filename not in {"ontology.ttl", "graph.json"}:
        abort(404)
    job = job_queue.latest(run_id)
    if not job or job["state"] != "completed":
        abort(404)
    try:
        run_model = RunModel.load(run_id)
        if json.loads(job["snapshot"]) != create_snapshot(run_model):
            abort(404)
    except (ValueError, OSError, UnicodeError):
        abort(404)
    return send_from_directory(Path(job["result_dir"]).resolve(), filename, as_attachment=True)


@run_bp.route("/update_ai_models")
def update_ai_models():
    provider_name = request.args["ai_provider"]
    provider = AI_PROVIDERS[provider_name]
    return provider.get_models()


@run_bp.route("/update_embedding_models")
def update_embedding_models():
    provider_name = request.args["ai_provider"]
    models = EMBEDDING_MODELS[provider_name]
    return models
