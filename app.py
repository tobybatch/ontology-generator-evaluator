from flask import Flask, render_template
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader, FileSystemLoader

app = Flask(__name__) 

app.jinja_loader = ChoiceLoader([
    FileSystemLoader("templates"),
    PrefixLoader({
        "govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")
    }),
])

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)