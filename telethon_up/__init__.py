import os
import zipfile
import urllib.request
import sys
import subprocess
import tempfile
import shutil
import re
import importlib
import ssl


# ==========================
#   SAFE SSL DOWNLOAD
# ==========================
def safe_download(url, path):
    try:
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla"})
        with urllib.request.urlopen(req, context=ctx) as resp, open(path, "wb") as f:
            shutil.copyfileobj(resp, f)
        return True
    except Exception as e:
        print(f"[telethon_up]: SSL error → {e}")
        return False


# ==========================
#   READ LAYER FROM api.tl
# ==========================
def get_layer_from_api_tl(api_tl_path):
    try:
        with open(api_tl_path, 'r', encoding='utf-8') as f:
            txt = f.read()
        m = re.search(r'// LAYER (\d+)', txt)
        return int(m.group(1)) if m else None
    except Exception as e:
        print("[telethon_up]: error reading api.tl:", e)
        return None


# ==========================
#   DOWNLOAD api.tl
# ==========================
def download_api_tl(temp_dir):
    url = ("https://raw.githubusercontent.com/telegramdesktop/tdesktop/dev/"
           "Telegram/SourceFiles/mtproto/scheme/api.tl")

    out = os.path.join(temp_dir, "api.tl")

    if safe_download(url, out):
        return out

    print("[telethon_up]: failed to download api.tl")
    return None


# ==========================
#   INSTALL TELETHON IF NEEDED
# ==========================
def ensure_telethon_installed():
    try:
        import telethon
        return True
    except ImportError:
        pass

    print("[telethon_up] installing Telethon...")
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "telethon", "--user"],
        text=True, capture_output=True
    )

    if r.returncode == 0:
        print("[telethon_up]: Telethon installed.")
        return True

    print("[telethon_up]: failed:", r.stderr)
    return False


# ==========================
#   FORCE RELOAD MODULE
# ==========================
def force_reload_telethon():
    for name in list(sys.modules.keys()):
        if name.startswith("telethon"):
            sys.modules.pop(name, None)
    import telethon
    return telethon


# ==========================
#   DOWNLOAD + UPDATE TELETHON
# ==========================
def download_and_update_telethon(api_tl_path, latest_layer):
    url = "https://github.com/LonamiWebs/Telethon/archive/v1.zip"

    tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip").name

    if not safe_download(url, tmp_zip):
        print("[telethon_up]: failed downloading Telethon ZIP")
        return False

    extract_dir = os.path.join(os.path.dirname(__file__), "Telethon_temp")

    try:
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)

        with zipfile.ZipFile(tmp_zip, "r") as z:
            z.extractall(extract_dir)

        telethon_folder = None
        for f in os.listdir(extract_dir):
            if f.startswith("Telethon"):
                telethon_folder = os.path.join(extract_dir, f)
                break

        if telethon_folder is None:
            print("[telethon_up]: folder not found")
            return False

        target_api = os.path.join(
            telethon_folder, "telethon_generator", "data", "api.tl"
        )
        os.makedirs(os.path.dirname(target_api), exist_ok=True)
        shutil.copy(api_tl_path, target_api)

        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", ".", "--user", "--force-reinstall"],
            cwd=telethon_folder, text=True, capture_output=True
        )

        if r.returncode != 0:
            print(r.stderr)
            return False

        telethon = force_reload_telethon()
        print("[telethon_up]: updated layer →", telethon.tl.alltlobjects.LAYER)
        return True

    finally:
        try:
            os.unlink(tmp_zip)
        except:
            pass
        shutil.rmtree(extract_dir, ignore_errors=True)


# ==========================
#   MAIN CHECK FUNCTION
# ==========================
def chack():
    if not ensure_telethon_installed():
        print("[telethon_up]: can't continue")
        return

    with tempfile.TemporaryDirectory() as d:
        api_tl = download_api_tl(d)
        if not api_tl:
            return

        latest = get_layer_from_api_tl(api_tl)
        if not latest:
            print("[telethon_up]: cannot detect layer")
            return

        try:
            from telethon.tl import alltlobjects
            current = alltlobjects.LAYER

            if current < latest:
                print(f"[telethon_up]: updating {current} → {latest}")
                download_and_update_telethon(api_tl, latest)
            else:
                print("[telethon_up]: Telethon is up-to-date")

        except ImportError:
            print("[telethon_up]: telethon import failed")
