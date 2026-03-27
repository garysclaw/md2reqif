"""Flask web interface for md2reqif."""
import io
import os
import tempfile
from pathlib import Path
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename

from md2reqif.md_parser import parse as parse_markdown
from md2reqif.reqif_writer import write as write_reqif
from md2reqif.reqif_reader import read as read_reqif
from md2reqif.md_writer import write as write_markdown

app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"))
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")

ALLOWED_MD = {".md", ".markdown"}
ALLOWED_REQIF = {".reqif", ".xml"}


def allowed_md(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_MD


def allowed_reqif(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_REQIF


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/convert/md-to-reqif", methods=["POST"])
def convert_md_to_reqif():
    if "file" not in request.files:
        flash("No file selected", "error")
        return redirect(url_for("index"))

    file = request.files["file"]
    if not file.filename:
        flash("No file selected", "error")
        return redirect(url_for("index"))

    if not allowed_md(file.filename):
        flash("Please upload a Markdown file (.md or .markdown)", "error")
        return redirect(url_for("index"))

    try:
        content = file.read().decode("utf-8")
        doc = parse_markdown(content)
        xml_str = write_reqif(doc)
        xml_bytes = xml_str.encode("utf-8") if isinstance(xml_str, str) else xml_str

        stem = Path(secure_filename(file.filename)).stem
        output_filename = f"{stem}.reqif"

        return send_file(
            io.BytesIO(xml_bytes),
            mimetype="application/xml",
            as_attachment=True,
            download_name=output_filename,
        )
    except Exception as e:
        flash(f"Conversion failed: {e}", "error")
        return redirect(url_for("index"))


@app.route("/convert/reqif-to-md", methods=["POST"])
def convert_reqif_to_md():
    if "file" not in request.files:
        flash("No file selected", "error")
        return redirect(url_for("index"))

    file = request.files["file"]
    if not file.filename:
        flash("No file selected", "error")
        return redirect(url_for("index"))

    if not allowed_reqif(file.filename):
        flash("Please upload a ReqIF file (.reqif or .xml)", "error")
        return redirect(url_for("index"))

    try:
        content = file.read().decode("utf-8")
        doc = read_reqif(content)
        md_text = write_markdown(doc)

        stem = Path(secure_filename(file.filename)).stem
        output_filename = f"{stem}.md"

        return send_file(
            io.BytesIO(md_text.encode("utf-8")),
            mimetype="text/markdown",
            as_attachment=True,
            download_name=output_filename,
        )
    except Exception as e:
        flash(f"Conversion failed: {e}", "error")
        return redirect(url_for("index"))


def main():
    """Entry point for md2reqif-web command."""
    import argparse
    parser = argparse.ArgumentParser(description="md2reqif web interface")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
