from flask import Blueprint, render_template
from services.run_service import get_dashboard_data

run_bp = Blueprint("run", __name__)


@run_bp.route("/")
def index():
    data = get_dashboard_data()
    return render_template("index.html", **data)