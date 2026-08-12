"""SailingPD Configuration Web UI — Flask backend."""
from flask import Flask, render_template, request, jsonify, send_file
import configparser
import io
import os
import shutil
import sys
from pathlib import Path

try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

# ─── uitvoer veilig maken ────────────────────────────────────────────────────
# Windows gebruikt buiten een echt consolevenster de oude codepagina (cp1252 op
# een Nederlandse installatie). Onze meldingen bevatten accenten en lijntjes, en
# die laten het programma daar met een UnicodeEncodeError crashen nog voor de
# webserver start. UTF-8 afdwingen met errors="replace" maakt uitvoer nooit meer
# fataal.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

# ─── waar draaien we vandaan? ────────────────────────────────────────────────
# Als losse broncode (start.sh / start.bat) staat alles naast app.py. Als
# bevroren .exe (PyInstaller) pakt PyInstaller de templates uit in een tijdelijke
# map (sys._MEIPASS), terwijl de SailingPD-installatie natuurlijk naast de .exe
# staat. Die twee moeten dus uit elkaar worden gehouden.
FROZEN = getattr(sys, "frozen", False)

# Map waar de gebruiker het programma heeft neergezet — bepaalt waar we de
# SailingPD-installatie zoeken.
BASE_DIR = Path(sys.executable).resolve().parent if FROZEN else Path(__file__).resolve().parent

# Map met meegeleverde bronbestanden (templates); bij een .exe de uitpakmap.
RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", BASE_DIR)) if FROZEN else BASE_DIR

app = Flask(__name__, template_folder=str(RESOURCE_DIR / "templates"))
app.config["TEMPLATES_AUTO_RELOAD"] = not FROZEN

SPD_MARKERS = ("web_root", "sailingPD", "sailingPD.exe", "boatspecifics")


def _find_sailing_dir(base: Path) -> Path:
    """Zoek de SailingPD-installatiemap: die met web_root / sailingPD(.exe) / boatspecifics.

    Gekeken wordt naar de map zelf (de .exe kan los in de SailingPD-map staan),
    daarna de bovenliggende map (de gebruikelijke config-wizard/-indeling) en
    ten slotte nog een niveau hoger. Wordt niets gevonden, dan valt hij terug op
    de bovenliggende map, zoals voorheen.
    """
    for candidate in (base, base.parent, base.parent.parent):
        if any((candidate / m).exists() for m in SPD_MARKERS):
            return candidate
    return base.parent

SAILING_DIR       = _find_sailing_dir(BASE_DIR)
BOATSPECIFICS_DIR = SAILING_DIR / "boatspecifics"
SYSTEMFILES_DIR   = SAILING_DIR / "systemfiles"
POLARS_DIR        = SAILING_DIR / "polars"
HEELPOLARS_DIR    = SAILING_DIR / "heelpolars"
DEVIATION_DIR     = SAILING_DIR / "deviation"
STWCORR_DIR       = SAILING_DIR / "stwcorrection"
WEB_ROOT_DIR      = SAILING_DIR / "web_root"

# Meegeleverd dashboard-menu (web-menu/). Bij een .exe zit het in de bundel
# (PyInstaller --add-data), als broncode staat het naast config-wizard/.
MENU_SRC_DIR = (RESOURCE_DIR / "web-menu") if FROZEN else (BASE_DIR.parent / "web-menu")

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

HEADLESS_FILE      = SYSTEMFILES_DIR / "headless.txt"
NOTHEADLESS_FILE   = SYSTEMFILES_DIR / "notheadless.txt"
WEBSERVERSEL_FILE  = SYSTEMFILES_DIR / "webserverselection.txt"
COMPLETESEL_FILE   = SYSTEMFILES_DIR / "completewebserverselection.txt"
NMEATEMPLATES_FILE = SYSTEMFILES_DIR / "NMEAtemplates.txt"

# ─── generic raw text-file editor: fixed allowlist (NO path traversal) ────────
# logical name → (absolute path, read_only)
ALLOWED_TEXT_FILES = {
    "boatspecifics.ini":               (BOATSPECIFICS_FILE, False),
    "systemfiles/processlist.ini":     (PROCESSLIST_FILE,   False),
    "systemfiles/sendoverwifi.ini":    (SENDOVERWIFI_FILE,  False),
    "systemfiles/webserverselection.txt":         (WEBSERVERSEL_FILE,  False),
    "systemfiles/NMEAtemplates.txt":              (NMEATEMPLATES_FILE, False),
    "systemfiles/completewebserverselection.txt": (COMPLETESEL_FILE,   True),
    "systemfiles/headless.txt":        (HEADLESS_FILE,      False),
}


def _display_mode():
    """Return 'screen' | 'web' | 'printer' based on systemfiles/headless.txt."""
    if not HEADLESS_FILE.exists():
        return "screen"
    content = HEADLESS_FILE.read_text(encoding="utf-8", errors="replace").strip().lower()
    return "printer" if content == "printer" else "web"

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


def _strip_placeholders(boatspecifics: dict) -> dict:
    """Maak overduidelijke placeholder-waarden uit SailingPD's voorbeeldbestand leeg.

    Het meegeleverde 'example boatspecifics.ini' vult o.a. de transducer-labels met
    'yourrolltransducer' / 'yourpitchtransducer'. Die als voor-ingevulde waarde tonen
    is verwarrender dan een leeg veld met de detectieknop ernaast.
    """
    inp = boatspecifics.get("Inputcontrol")
    if inp:
        for key in ("XDR_roll", "XDR_pitch"):
            val = inp.get(key, "")
            if val.strip().lower().startswith("your"):
                inp[key] = ""
    return boatspecifics


@app.route("/api/config", methods=["GET"])
def get_config():
    boatspecifics = read_ini(BOATSPECIFICS_FILE)
    if not boatspecifics:
        boatspecifics = read_ini(EXAMPLE_FILES["boatspecifics"])
    boatspecifics = _strip_placeholders(boatspecifics)

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

    return jsonify({
        "boatspecifics": boatspecifics,
        "processlist":   processlist,
        "sendoverwifi":  sendoverwifi,
        "files":         files,
        "sailing_dir":   str(SAILING_DIR),
        "config_exists": BOATSPECIFICS_FILE.exists(),
        "headless":      HEADLESS_FILE.exists(),
        "display_mode":  _display_mode(),
    })


STARTUPFILES_FILE = SYSTEMFILES_DIR / "startupfiles.ini"


def _pick_file(dirpath: Path, prefer_non_example: bool = False) -> str:
    """Kies een bestand uit een map; bij voorkeur niet een 'example ...'-bestand."""
    if not dirpath.exists():
        return ""
    files = sorted(f for f in dirpath.glob("*.csv") if not f.name.startswith("."))
    if not files:
        return ""
    if prefer_non_example:
        eigen = [f for f in files if not f.name.lower().startswith("example")]
        if eigen:
            return str(eigen[0])
    return str(files[0])


def _ensure_startupfiles():
    """Schrijf systemfiles/startupfiles.ini voor de headless (web/printer) modus.

    Zonder scherm kan SailingPD niet interactief om bestanden vragen en stopt hij
    met "Deadly Error. Headless cannot be combined with no for same start files".
    Bestaande keuzes blijven staan zolang het genoemde bestand nog bestaat; alleen
    ontbrekende regels worden ingevuld.
    """
    huidig = read_ini(STARTUPFILES_FILE).get("startupfiles", {})

    defaults = {
        "boatfile":      str(BOATSPECIFICS_FILE),
        "polarfile":     _pick_file(POLARS_DIR, prefer_non_example=True),
        "heelpolarfile": _pick_file(HEELPOLARS_DIR),
        "deviationfile": _pick_file(DEVIATION_DIR),
        "stwcorrfile":   _pick_file(STWCORR_DIR),
    }

    resultaat = {}
    for sleutel, standaard in defaults.items():
        bestaand = huidig.get(sleutel, "").strip()
        resultaat[sleutel] = bestaand if bestaand and Path(bestaand).exists() else standaard

    write_ini(STARTUPFILES_FILE, {"startupfiles": resultaat})
    return resultaat


@app.route("/api/config", methods=["POST"])
def save_config():
    data = request.get_json(force=True)
    try:
        BOATSPECIFICS_DIR.mkdir(parents=True, exist_ok=True)
        SYSTEMFILES_DIR.mkdir(parents=True, exist_ok=True)

        if "boatspecifics" in data:
            write_ini(BOATSPECIFICS_FILE, data["boatspecifics"])
        if "processlist" in data:
            write_ini(PROCESSLIST_FILE, data["processlist"])
        if "sendoverwifi" in data:
            write_ini(SENDOVERWIFI_FILE, data["sendoverwifi"])
        # ── Weergavemodus: systemfiles/headless.txt ──────────────────────────
        # Scherm  → geen headless.txt
        # web     → headless.txt met exact één regel: web
        # printer → headless.txt met exact één regel: printer
        # (routeert info/foutmeldingen; "headless" als inhoud is FOUT)
        if "display_mode" in data:
            mode = str(data["display_mode"]).strip().lower()
            # verwijder verwarrende oude/hernoemde variant
            if NOTHEADLESS_FILE.exists():
                NOTHEADLESS_FILE.unlink()
            if mode in ("web", "printer"):
                HEADLESS_FILE.write_text(mode + "\n", encoding="utf-8")
            else:  # 'screen' of onbekend → geen headless
                if HEADLESS_FILE.exists():
                    HEADLESS_FILE.unlink()
        elif "headless" in data:  # achterwaartse compatibiliteit
            if NOTHEADLESS_FILE.exists():
                NOTHEADLESS_FILE.unlink()
            if data["headless"]:
                HEADLESS_FILE.write_text("web\n", encoding="utf-8")
            elif HEADLESS_FILE.exists():
                HEADLESS_FILE.unlink()

        # In de headless modus moet startupfiles.ini bestaan, anders weigert
        # SailingPD te starten met een "Deadly Error".
        if HEADLESS_FILE.exists():
            _ensure_startupfiles()

        # Het overzichtsmenu wordt standaard de startpagina op poort 9090.
        # Idempotent en niet-fataal: mislukt het, dan blijft de config wél bewaard.
        try:
            _install_webmenu()
        except Exception:
            pass

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
    # [SECURITY OPTIMIZATION]: Strikt beveiligen tegen path traversal via Path(filename).name
    safe_name = Path(filename).name
    p = CSV_DIRS[folder] / safe_name
    if not p.exists():
        return jsonify({"error": "Bestand niet gevonden"}), 404
    return jsonify({"content": p.read_text(encoding="utf-8", errors="replace"),
                    "filename": safe_name})


@app.route("/api/csv/<folder>/<path:filename>", methods=["POST"])
def save_csv(folder, filename):
    if folder not in CSV_DIRS:
        return jsonify({"error": "Onbekende map"}), 400
    data = request.get_json(force=True)
    content = data.get("content", "")
    # [SECURITY OPTIMIZATION]: Strikt beveiligen tegen path traversal via Path(filename).name
    safe_name = Path(filename).name
    p = CSV_DIRS[folder] / safe_name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return jsonify({"success": True})


@app.route("/api/csv/<folder>/<path:filename>", methods=["DELETE"])
def delete_csv(folder, filename):
    if folder not in CSV_DIRS:
        return jsonify({"error": "Onbekende map"}), 400
    # [SECURITY OPTIMIZATION]: Strikt beveiligen tegen path traversal via Path(filename).name
    safe_name = Path(filename).name
    p = CSV_DIRS[folder] / safe_name
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


# ─── dashboard-menu (web-menu) installeren in web_root ───────────────────────
# Het meegeleverde menu (web-menu/index.html + thumbs) wordt de startpagina op
# poort 9090. De originele SPA blijft bereikbaar als dials.html.
MENU_MARKER = "SailingPD — Pagina's"   # <title> van ons menu


def _webmenu_installed() -> bool:
    idx = WEB_ROOT_DIR / "index.html"
    if not idx.exists():
        return False
    try:
        return MENU_MARKER in idx.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


@app.route("/api/webmenu", methods=["GET"])
def webmenu_status():
    return jsonify({
        "installed":      _webmenu_installed(),
        "web_root_exists": WEB_ROOT_DIR.exists(),
        "source_exists":  (MENU_SRC_DIR / "index.html").exists(),
    })


def _install_webmenu():
    """Kopieer het meegeleverde menu naar web_root. Retourneert (ok, bericht).

    Idempotent: bewaart de originele startpagina één keer als index.html.orig-spa
    én als dials.html, en overschrijft die nooit met ons eigen menu.
    """
    src_index = MENU_SRC_DIR / "index.html"
    if not src_index.exists():
        return False, f"Menu-bronbestand niet gevonden ({src_index})"
    if not WEB_ROOT_DIR.exists():
        return False, f"web_root niet gevonden in {SAILING_DIR}"

    dst_index = WEB_ROOT_DIR / "index.html"
    orig_bak  = WEB_ROOT_DIR / "index.html.orig-spa"
    dials     = WEB_ROOT_DIR / "dials.html"

    if dst_index.exists() and not _webmenu_installed():
        if not orig_bak.exists():
            shutil.copy2(dst_index, orig_bak)
        shutil.copy2(dst_index, dials)
    elif orig_bak.exists() and not dials.exists():
        shutil.copy2(orig_bak, dials)

    shutil.copy2(src_index, dst_index)

    src_thumbs = MENU_SRC_DIR / "thumbs"
    if src_thumbs.is_dir():
        dst_thumbs = WEB_ROOT_DIR / "thumbs"
        dst_thumbs.mkdir(parents=True, exist_ok=True)
        for jpg in src_thumbs.glob("*.jpg"):
            shutil.copy2(jpg, dst_thumbs / jpg.name)

    # SPD's eigen logo meekopiëren zodat het menu (geserveerd door SPD op 9090)
    # hetzelfde logo toont als de wizard. Ontbreekt het? Dan valt het menu terug
    # op een anker-embleem.
    spd_icon = SYSTEMFILES_DIR / "icon.png"
    if spd_icon.exists():
        shutil.copy2(spd_icon, WEB_ROOT_DIR / "spd-icon.png")

    # Het configureerbare prestatiepaneel meekopiëren (de standaard-dashboardkeuze).
    panel = MENU_SRC_DIR / "panel.html"
    if panel.exists():
        shutil.copy2(panel, WEB_ROOT_DIR / "panel.html")

    return True, "Dashboard-menu geïnstalleerd als startpagina."


@app.route("/api/webmenu/install", methods=["POST"])
def webmenu_install():
    try:
        ok, msg = _install_webmenu()
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500
    return (jsonify({"success": True, "message": msg}) if ok
            else (jsonify({"success": False, "error": msg}), 404))


# ─── webserver field selection ────────────────────────────────────────────────
def _read_keyword_lines(path):
    """One keyword per line, trailing/leading whitespace stripped, blanks dropped."""
    out = []
    if path.exists():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            kw = line.strip()
            if kw:
                out.append(kw)
    return out


@app.route("/api/webserverfields", methods=["GET"])
def get_webserverfields():
    master = _read_keyword_lines(COMPLETESEL_FILE)
    file_exists = WEBSERVERSEL_FILE.exists()
    if file_exists:
        selected = _read_keyword_lines(WEBSERVERSEL_FILE)
    else:
        # geen bestand => ALLE velden worden geserveerd
        selected = list(master)
    return jsonify({
        "master":      master,
        "selected":    selected,
        "file_exists": file_exists,
    })


@app.route("/api/webserverfields", methods=["POST"])
def save_webserverfields():
    data = request.get_json(force=True)
    selected = data.get("selected", [])
    try:
        SYSTEMFILES_DIR.mkdir(parents=True, exist_ok=True)
        lines = [str(kw).strip() for kw in selected if str(kw).strip()]
        WEBSERVERSEL_FILE.write_text("\n".join(lines) + ("\n" if lines else ""),
                                     encoding="utf-8")
        return jsonify({"success": True, "count": len(lines)})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


# ─── generic raw text-file editor (allowlist only, no path traversal) ──────────
@app.route("/api/rawfile", methods=["GET"])
def list_rawfiles():
    out = []
    for name, (path, readonly) in ALLOWED_TEXT_FILES.items():
        out.append({"name": name, "readonly": readonly, "exists": path.exists()})
    return jsonify({"files": out})


@app.route("/api/rawfile/<path:name>", methods=["GET"])
def get_rawfile(name):
    entry = ALLOWED_TEXT_FILES.get(name)
    if entry is None:
        return jsonify({"error": "Niet-toegestaan bestand"}), 400
    path, readonly = entry
    content = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    return jsonify({"name": name, "content": content,
                    "readonly": readonly, "exists": path.exists()})


@app.route("/api/rawfile/<path:name>", methods=["POST"])
def save_rawfile(name):
    entry = ALLOWED_TEXT_FILES.get(name)
    if entry is None:
        return jsonify({"success": False, "error": "Niet-toegestaan bestand"}), 400
    path, readonly = entry
    if readonly:
        return jsonify({"success": False, "error": "Dit bestand is alleen-lezen"}), 400
    data = request.get_json(force=True)
    content = data.get("content", "")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return jsonify({"success": True})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


# ─── Signal K / Node-RED flow download ────────────────────────────────────────
SIGNALK_FLOW_FILE = SAILING_DIR / "Signal K connection" / "Node Red SPD v311.json"


@app.route("/api/signalk-flow", methods=["GET"])
def signalk_flow():
    if not SIGNALK_FLOW_FILE.exists():
        return jsonify({"error": "Node-RED flow niet gevonden"}), 404
    return send_file(str(SIGNALK_FLOW_FILE), mimetype="application/json",
                     as_attachment=True, download_name="Node Red SPD v311.json")


# ─── live NMEA connection test (listen briefly, report sentence types) ─────────
@app.route("/api/test-nmea", methods=["POST"])
def test_nmea():
    import socket, time
    data = request.get_json(force=True) or {}
    channel = str(data.get("channel", "network")).lower()
    proto   = str(data.get("type", "UDP")).upper()
    ip      = str(data.get("ip", "")).strip()
    try:
        port = int(str(data.get("port", "0")).strip() or "0")
    except (TypeError, ValueError):
        port = 0
    seconds = 4
    lines = []

    def collect(buf):
        for raw in buf.replace(b"\r", b"\n").split(b"\n"):
            s = raw.strip()
            if s[:1] in (b"$", b"!"):
                lines.append(s.decode("ascii", "replace"))

    if channel == "serial":
        return jsonify({"ok": False,
            "error": "Serieel testen wordt (nog) niet ondersteund in de wizard. "
                     "Test de netwerkverbinding, of controleer de seriële poort met een terminalprogramma."})
    if port < 1 or port > 65535:
        return jsonify({"ok": False, "error": "Ongeldige poort."})

    try:
        if proto == "TCP":
            host = ip if ip and ip not in ("0.0.0.0", "255.255.255.255") else "127.0.0.1"
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(seconds)
            sock.connect((host, port))
            # [PERFORMANCE OPTIMIZATION]: Kortere socket timeout (0.2s) voorkomt trage responsiviteit
            sock.settimeout(0.2)
            deadline = time.monotonic() + seconds
            while time.monotonic() < deadline:
                try:
                    buf = sock.recv(4096)
                    if not buf:
                        break
                    collect(buf)
                except socket.timeout:
                    pass
            sock.close()
        else:  # UDP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if hasattr(socket, "SO_REUSEPORT"):
                try:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                except OSError:
                    pass
            sock.bind(("", port))
            # [PERFORMANCE OPTIMIZATION]: Kortere socket timeout (0.2s) voorkomt trage responsiviteit
            sock.settimeout(0.2)
            deadline = time.monotonic() + seconds
            while time.monotonic() < deadline:
                try:
                    buf, _ = sock.recvfrom(4096)
                    collect(buf)
                except socket.timeout:
                    pass
            sock.close()
    except OSError as exc:
        msg = str(exc)
        if getattr(exc, "errno", None) == 98:  # EADDRINUSE
            msg = (f"Poort {port} is al in gebruik — waarschijnlijk draait SailingPD al op deze poort. "
                   f"Stop SailingPD en test opnieuw.")
        return jsonify({"ok": False, "error": msg})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)})

    types, xdr_labels = {}, set()
    for ln in lines:
        body = ln[1:]
        star = body.find("*")
        if star != -1:
            body = body[:star]
        fields = body.split(",")
        head = fields[0] if fields else ""
        sid = head[2:] if len(head) >= 5 else head  # talker(2) + sentence-id(3)
        if sid:
            types[sid] = types.get(sid, 0) + 1
        if sid == "XDR":
            for i in range(1, len(fields), 4):
                grp = fields[i:i + 4]
                if len(grp) == 4 and grp[3].strip():
                    xdr_labels.add(grp[3].strip())
    return jsonify({
        "ok": True,
        "count": len(lines),
        "types": types,
        "xdr_labels": sorted(xdr_labels),
        "sample": lines[:12],
    })


SERVICE_NAME = "sailingpd.service"


def _systemd_service_active():
    """True als SailingPD als systemd-service is ingericht (Linux/Raspberry Pi).

    Draait SailingPD als service, dan moet de startknop die service herstarten;
    een los proces starten zou botsen op poort 5000/9090 met de service.
    """
    import subprocess
    if sys.platform.startswith("win") or not shutil.which("systemctl"):
        return False
    try:
        r = subprocess.run(["systemctl", "is-enabled", SERVICE_NAME],
                           capture_output=True, text=True, timeout=5)
        return r.stdout.strip() in ("enabled", "enabled-runtime", "static", "alias", "indirect")
    except Exception:
        return False


@app.route("/api/start", methods=["POST"])
def start_sailingpd():
    import subprocess
    # Systemd-installatie: herstart de service in plaats van een tweede proces te starten.
    if _systemd_service_active():
        for cmd in (["sudo", "-n", "systemctl", "restart", SERVICE_NAME],
                    ["systemctl", "restart", SERVICE_NAME]):
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            except Exception:
                continue
            if r.returncode == 0:
                return jsonify({"success": True,
                                "message": "SailingPD-service herstart — hij komt op zodra er NMEA-data is."})
        return jsonify({"success": False,
                        "error": f"Kon {SERVICE_NAME} niet herstarten. Probeer: sudo systemctl restart {SERVICE_NAME}"}), 500

    # Windows: sailingPD.exe · Linux/Raspberry Pi: sailingPD
    exe = next((SAILING_DIR / n for n in ("sailingPD", "sailingPD.exe") if (SAILING_DIR / n).exists()), None)
    if exe is None:
        return jsonify({"success": False, "error": f"sailingPD (of sailingPD.exe) niet gevonden in {SAILING_DIR}"}), 404
    try:
        kwargs = {
            "cwd": str(SAILING_DIR),
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
        }
        if sys.platform == "win32":
            # [WINDOWS FIX]: Gebruik DETACHED_PROCESS en CREATE_NEW_PROCESS_GROUP om los te koppelen van console
            DETACHED_PROCESS = 0x00000008
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            kwargs["creationflags"] = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        else:
            kwargs["start_new_session"] = True

        subprocess.Popen([str(exe)], **kwargs)
        return jsonify({"success": True, "message": "SailingPD wordt gestart…"})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


def _found_sailingpd() -> bool:
    return any((SAILING_DIR / m).exists() for m in SPD_MARKERS)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    url = f"http://localhost:{port}"

    print("=" * 65)
    print(f"  SailingPD Config Wizard")
    if _found_sailingpd():
        print(f"  Installatiemap : {SAILING_DIR}")
    else:
        # Beter een duidelijke waarschuwing dan een wizard die stilletjes de
        # verkeerde map bewerkt.
        print(f"  LET OP: geen SailingPD-installatie gevonden bij {SAILING_DIR}")
        print(f"  Zet dit programma IN uw SailingPD-map (die met sailingPD.exe)")
    print(f"  Open in browser: {url}")
    print("=" * 65)

    if FROZEN:
        # Als .exe is er geen start.bat die de browser opent; zelf doen.
        import threading, webbrowser
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()

    # [PERFORMANCE OPTIMIZATION]: Enable threaded=True om gelijktijdige browserverzoeken af te handelen
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
