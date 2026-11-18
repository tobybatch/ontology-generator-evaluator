from unittest.mock import Mock

import pytest

import config
from app import app
from ontology_generator_evaluator.models.run_model import RunModel
from routes import run


@pytest.mark.parametrize(
    ("method", "form", "handler"),
    [
        ("GET", None, "get_dashboard_data"),
        ("POST", {}, "get_dashboard_data"),
        ("POST", {"action": "update"}, "get_dashboard_data"),
        ("POST", {"action": "start"}, "start_run"),
    ],
)
def test_index_dispatches_to_selected_handler(monkeypatch, method, form, handler):
    dashboard = Mock(return_value={})
    start = Mock(return_value={})
    monkeypatch.setattr(run, "get_dashboard_data", dashboard)
    monkeypatch.setattr(run, "start_run", start)
    monkeypatch.setattr(run, "render_template", lambda *args, **kwargs: "dashboard")

    response = app.test_client().open("/", method=method, data=form)

    assert response.status_code == 200
    selected, unselected = (start, dashboard) if handler == "start_run" else (dashboard, start)
    selected.assert_called_once()
    unselected.assert_not_called()


@pytest.mark.parametrize("action", ["update", "start"])
def test_form_actions_save_and_render_dashboard(monkeypatch, tmp_path, action):
    monkeypatch.setattr(config, "STORAGE_PATH", str(tmp_path / "storage"))
    monkeypatch.setattr(config, "RUN_MODEL_STORAGE_PATH", str(tmp_path / "runs"))

    response = app.test_client().post(
        "/",
        data={"action": action, "run_id": "run-actions", "run_name": "Saved changes"},
    )

    assert response.status_code == 200
    assert RunModel.load("run-actions").name == "Saved changes"
    html = response.get_data(as_text=True)
    assert 'value="update" name="action"' in html
    assert 'value="start" name="action"' in html
    assert ">Go<" not in html
    assert ("Run execution is not implemented yet." in html) == (action == "start")
