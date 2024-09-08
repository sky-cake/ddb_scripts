import deepdanbooru
from deepdanbooru.commands import evaluate_image
from flask import Flask, request, render_template

PROJECT_PATH = '/media/scripts/deepdanbooru/db_released_project'
MODEL = deepdanbooru.project.load_model_from_project(PROJECT_PATH, compile_model=False)
TAGS = deepdanbooru.project.load_tags_from_project(PROJECT_PATH)


import os
import deepdanbooru
from io import BytesIO
from deepdanbooru.commands import evaluate_image
from flask import Flask, request, render_template

# PROJECT_PATH = os.path.abspath("model")
print("Loading model")
MODEL = deepdanbooru.project.load_model_from_project(
    PROJECT_PATH, compile_model=False
)
print("Loading tags")
TAGS = deepdanbooru.project.load_tags_from_project(PROJECT_PATH)


app = Flask("deepdanbooru", template_folder=os.path.abspath("templates"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "No file uploaded!"

    file = request.files["file"]

    result = evaluate_image(BytesIO(file.stream.read()), MODEL, TAGS, 0.5)
    results = {}
    for tag, score in result:
        results[tag] = float(f"{score:05.3f}")
    return results


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="8080")