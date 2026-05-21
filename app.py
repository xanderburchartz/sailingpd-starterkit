"""SailingPD Configuration Web UI — Flask backend."""
from flask import Flask, render_template, request, jsonify, send_file
import configparser
import io
import os
from pathlib import Path

try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# ─── directory resolution ────────────────────────────────────────────────────
# config-ui/ zit direct in de sailingpd installatiemap, dus parent = installatiemap
BASE_DIR   = Path(__file__).parent
SAILING_DIR = BASE_DIR.parent
BOATSPECIFICS_DIR = SAILING_DIR / "boatspecifics"
SYSTEMFILES_DIR   = SAILING_DIR / "systemfiles"
POLARS_DIR        = SAILING_DIR / "polars"
HEELPOLARS_DIR    = SAILING_DIR / "heelpolars"
DEVIATION_DIR     = SAILING_DIR / "deviation"
STWCORR_DIR       = SAILING_DIR / "stwcorrection"

BOATSPECIFICS_FILE = BOATSPECIFICS_DIR / "boatspecifics.ini"
PROCESSLIST_FILE   = SYSTEMFILES_DIR   / "processlist.ini"
SENDOVERWIFI_FILE  = SYSTEMFILES_DIR   / "sendoverwifi.ini"

CSV_DIRS = {
    "polars":       POLARS_DIR,
    "heelpolars":   HEELPOLARS_DIR,
    "deviation":    DEVIATION_DIR,
    "stwcorrection": STWCORR_DIR,
}

EXAMPLE_FILES = {
    "boatspecifics": BOATSPECIFICS_DIR / "example boatspecifics heel tables.ini",
    "processlist":   SYSTEMFILES_DIR   / "processlist.ini",
    "sendoverwifi":  SYSTEMFILES_DIR   / "sendoverwifi.ini",
}

# ─── INI helpers ─────────────────────────────────────────────────────────────
def read_ini(filepath):
    cfg = configparser.RawConfigParser()
    cfg.optionxform = str  # preserve original case
    result = {}
    p = Path(filepath)
    if p.exists():
        cfg.read(str(p), encoding="utf-8")
        for sec in cfg.sections():
            result[sec] = {}
            for k, v in cfg.items(sec):
                result[sec][k] = v if v is not None else ""
    return result


def write_ini(filepath, data: dict):
    p = Path(filepath)
    p.parent.mkdir(parents=True, exist_ok=True)
    cfg = configparser.RawConfigParser()
    cfg.optionxform = str
    for sec, vals in data.items():
        cfg.add_section(sec)
        for k, v in vals.items():
            cfg.set(sec, k, "" if v is None else str(v))
    with open(str(p), "w", encoding="utf-8") as f:
        cfg.write(f)


# ─── routes ──────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/config", methods=["GET"])
def get_config():
    boatspecifics = read_ini(BOATSPECIFICS_FILE)
    if not boatspecifics:
        boatspecifics = read_ini(EXAMPLE_FILES["boatspecifics"])

    processlist   = read_ini(PROCESSLIST_FILE)
    if not processlist:
        processlist = read_ini(EXAMPLE_FILES["processlist"])

    sendoverwifi  = read_ini(SENDOVERWIFI_FILE)
    if not sendoverwifi:
        sendoverwifi = read_ini(EXAMPLE_FILES["sendoverwifi"])

    files = {}
    for folder, dirpath in CSV_DIRS.items():
        if dirpath.exists():
            files[folder] = [f.name for f in sorted(dirpath.glob("*.csv"))
                             if not f.name.startswith(".")]
        else:
            files[folder] = []

    headless_file = SYSTEMFILES_DIR / "headless.txt"

    return jsonify({
        "boatspecifics": boatspecifics,
        "processlist":   processlist,
        "sendoverwifi":  sendoverwifi,
        "files":         files,
        "sailing_dir":   str(SAILING_DIR),
        "config_exists": BOATSPECIFICS_FILE.exists(),
        "headless":      headless_file.exists(),
    })


@app.route("/api/config", methods=["POST"])
def save_config():
    data = request.get_json(force=True)
    try:
        if "boatspecifics" in data:
            write_ini(BOATSPECIFICS_FILE, data["boatspecifics"])
        if "processlist" in data:
            write_ini(PROCESSLIST_FILE, data["processlist"])
        if "sendoverwifi" in data:
            write_ini(SENDOVERWIFI_FILE, data["sendoverwifi"])
        # headless.txt aan/uit
        headless_file = SYSTEMFILES_DIR / "headless.txt"
        if "headless" in data:
            if data["headless"]:
                headless_file.write_text("headless\n")
            elif headless_file.exists():
                headless_file.unlink()
        return jsonify({"success": True, "message": "Configuratie opgeslagen!"})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/api/csv/<folder>", methods=["GET"])
def list_csv(folder):
    if folder not in CSV_DIRS:
        return jsonify({"error": "Onbekende map"}), 400
    d = CSV_DIRS[folder]
    files = []
    if d.exists():
        files = [f.name for f in sorted(d.glob("*.csv")) if not f.name.startswith(".")]
    return jsonify({"files": files})


@app.route("/api/csv/<folder>/<path:filename>", methods=["GET"])
def get_csv(folder, filename):
    if folder not in CSV_DIRS:
        return jsonify({"error": "Onbekende map"}), 400
    p = CSV_DIRS[folder] / filename
    if not p.exists():
        return jsonify({"error": "Bestand niet gevonden"}), 404
    return jsonify({"content": p.read_text(encoding="utf-8", errors="replace"),
                    "filename": filename})


@app.route("/api/csv/<folder>/<path:filename>", methods=["POST"])
def save_csv(folder, filename):
    if folder not in CSV_DIRS:
        return jsonify({"error": "Onbekende map"}), 400
    data = request.get_json(force=True)
    content = data.get("content", "")
    p = CSV_DIRS[folder] / filename
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return jsonify({"success": True})


@app.route("/api/csv/<folder>/<path:filename>", methods=["DELETE"])
def delete_csv(folder, filename):
    if folder not in CSV_DIRS:
        return jsonify({"error": "Onbekende map"}), 400
    p = CSV_DIRS[folder] / filename
    if p.exists():
        p.unlink()
    return jsonify({"success": True})


# ─── image routes ─────────────────────────────────────────────────────────────
IMAGE_SPECS = {
    "background": {
        "filename": "background.gif",
        "size": (250, 412),
        "format": "GIF",
        "mime": "image/gif",
    },
    "icon": {
        "filename": "icon.png",
        "size": (256, 256),
        "format": "PNG",
        "mime": "image/png",
    },
}


@app.route("/api/image/<name>", methods=["GET"])
def get_image(name):
    if name not in IMAGE_SPECS:
        return jsonify({"error": "Onbekend afbeeldingstype"}), 400
    spec = IMAGE_SPECS[name]
    p = SYSTEMFILES_DIR / spec["filename"]
    if not p.exists():
        return jsonify({"error": "Bestand niet gevonden"}), 404
    return send_file(str(p), mimetype=spec["mime"])


@app.route("/api/image/<name>", methods=["POST"])
def upload_image(name):
    if name not in IMAGE_SPECS:
        return jsonify({"error": "Onbekend afbeeldingstype"}), 400
    if not HAS_PILLOW:
        return jsonify({"error": "Pillow niet geïnstalleerd. Voer uit: pip3 install Pillow"}), 500

    if "file" not in request.files:
        return jsonify({"error": "Geen bestand ontvangen"}), 400

    spec = IMAGE_SPECS[name]
    file = request.files["file"]
    target = SYSTEMFILES_DIR / spec["filename"]

    try:
        img = Image.open(file.stream).convert("RGBA")

        # Schaal naar doelformaat met behoud van aspectverhouding (letterbox)
        tw, th = spec["size"]
        img.thumbnail((tw, th), Image.LANCZOS)
        canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        offset = ((tw - img.width) // 2, (th - img.height) // 2)
        canvas.paste(img, offset)

        if spec["format"] == "GIF":
            canvas = canvas.convert("P", palette=Image.ADAPTIVE, colors=256)
            canvas.save(str(target), format="GIF")
        else:
            canvas.save(str(target), format="PNG")

        return jsonify({
            "success": True,
            "message": f"Opgeslagen als {spec['filename']} ({tw}×{th} px)",
        })
    except Exception as exc:
        return jsonify({"error": f"Verwerking mislukt: {exc}"}), 500


@app.route("/api/image/<name>/info", methods=["GET"])
def image_info(name):
    if name not in IMAGE_SPECS:
        return jsonify({"error": "Onbekend afbeeldingstype"}), 400
    spec = IMAGE_SPECS[name]
    p = SYSTEMFILES_DIR / spec["filename"]
    if not p.exists():
        return jsonify({"exists": False})
    info = {"exists": True, "filename": spec["filename"], "size_bytes": p.stat().st_size}
    if HAS_PILLOW:
        try:
            img = Image.open(str(p))
            info["width"], info["height"] = img.size
            info["format"] = img.format
        except Exception:
            pass
    return jsonify(info)


@app.route("/api/start", methods=["POST"])
def start_sailingpd():
    import subprocess
    exe = SAILING_DIR / "sailingPD"
    if not exe.exists():
        return jsonify({"success": False, "error": f"sailingPD binary niet gevonden in {SAILING_DIR}"}), 404
    try:
        subprocess.Popen(
            [str(exe)],
            cwd=str(SAILING_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return jsonify({"success": True, "message": "SailingPD wordt gestart…"})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


if __name__ == "__main__":
    print(f"─────────────────────────────────────────────────────────────────")
    print(f"  SailingPD Config Wizard")
    print(f"  Plaats deze map (config-wizard/) in uw SailingPD-installatiemap")
    print(f"  Installatiemap : {SAILING_DIR}")
    print(f"  Open in browser: http://localhost:5001")
    print(f"─────────────────────────────────────────────────────────────────")
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
