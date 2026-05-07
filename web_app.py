from __future__ import annotations

import os
from pathlib import Path
import secrets

from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from database import clear_calculations, delete_calculation, fetch_calculations, init_db, save_calculation
from microscope_core import MICROSCOPE_TYPES, UNIT_LABELS, calculate_specimen_size


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("MICROSCOPE_DATA_DIR", BASE_DIR))
UPLOAD_FOLDER = DATA_DIR / "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp"}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-this")
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
init_db()


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error_message = None
    form_data = {
        "username": "",
        "measured_size_mm": "",
        "microscope_type": list(MICROSCOPE_TYPES)[0],
        "output_unit": "um",
    }

    if request.method == "POST":
        form_data = {
            "username": request.form.get("username", ""),
            "measured_size_mm": request.form.get("measured_size_mm", ""),
            "microscope_type": request.form.get("microscope_type", list(MICROSCOPE_TYPES)[0]),
            "output_unit": request.form.get("output_unit", "um"),
        }
        try:
            image = request.files.get("specimen_image")

            if image is None or image.filename == "":
                raise ValueError("Please upload a specimen image.")
            if not allowed_file(image.filename):
                raise ValueError("Please upload a valid image file.")

            safe_name = secure_filename(image.filename)
            filename = f"{secrets.token_hex(8)}_{safe_name}"
            stored_path = UPLOAD_FOLDER / filename
            image.save(stored_path)

            result = calculate_specimen_size(
                username=form_data["username"],
                image_path=str(stored_path.relative_to(BASE_DIR)),
                measured_size_mm=form_data["measured_size_mm"],
                microscope_type=form_data["microscope_type"],
                output_unit=form_data["output_unit"],
            )
            save_calculation(result)
            flash("Calculation saved successfully.", "success")
        except Exception as exc:
            error_message = str(exc)

    rows = fetch_calculations()
    return render_template(
        "index.html",
        microscope_types=list(MICROSCOPE_TYPES),
        units=UNIT_LABELS,
        result=result,
        error_message=error_message,
        rows=rows,
        form_data=form_data,
    )


@app.get("/uploads/<path:filename>")
def uploaded_file(filename: str):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.post("/delete/<int:record_id>")
def delete_record(record_id: int):
    delete_calculation(record_id)
    flash("Record deleted.", "success")
    return redirect(url_for("index"))


@app.post("/clear")
def clear_records():
    clear_calculations()
    flash("All records deleted.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "").lower() in {"1", "true", "yes", "on"}
    app.run(debug=debug)
