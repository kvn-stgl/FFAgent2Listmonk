from flask import Flask, render_template, request, Response
from converter import convert_ff_to_listmonk

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return render_template("index.html", error="Keine Datei ausgewählt.")

    file = request.files["file"]
    if file.filename == "":
        return render_template("index.html", error="Keine Datei ausgewählt.")

    if not file.filename.lower().endswith(".csv"):
        return render_template("index.html", error="Bitte nur CSV-Dateien hochladen.")

    raw = file.read()
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        content = raw.decode("latin-1")

    csv_output, count = convert_ff_to_listmonk(content)

    return Response(
        csv_output,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=listmonk_import.csv",
            "X-Row-Count": str(count),
        },
    )


if __name__ == "__main__":
    app.run(debug=True)
