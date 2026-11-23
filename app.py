from flask import Flask
from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader, PrefixLoader

from routes.run import run_bp

app = Flask(__name__)

app.jinja_loader = ChoiceLoader(
    [
        FileSystemLoader("src/templates"),
        PrefixLoader({"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}),
    ]
)

app.register_blueprint(run_bp)

if __name__ == "__main__":
    app.run(debug=True)
