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
import site
import inspect

# ==========================
#   SMART PIP INSTALLER
# ==========================
def run_pip_install(*args, cwd=None):
    base_cmd = [sys.executable, "-m", "pip", "install", "--no-cache-dir"]
    cmd = base_cmd + list(args)

    try:
        process = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if process.returncode == 0:
            return True

        cmd_user = cmd + ["--user"]
        process_user = subprocess.run(cmd_user, cwd=cwd, capture_output=True, text=True)
        
        if process_user.returncode == 0:
            user_site = site.getusersitepackages()
            if user_site not in sys.path:
                sys.path.insert(0, user_site)
            return True
        
        return False
    except:
        return False

# ==========================
#   DEEP RELOAD & INJECTION
# ==========================
def force_reload():
    importlib.invalidate_caches()
    
    for name in list(sys.modules.keys()):
        if name.startswith("telethon"):
            del sys.modules[name]
    
    import telethon
    importlib.reload(telethon)
    sys.modules["telethon"] = telethon

    frame = inspect.currentframe()
    try:
        while frame:
            if "telethon" in frame.f_globals:
                frame.f_globals["telethon"] = telethon
            frame = frame.f_back
    finally:
        del frame
    return telethon

# ==========================
#   UTILITIES
# ==========================
def safe_download(url, path):
    try:
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla"})
        with urllib.request.urlopen(req, context=ctx) as resp, open(path, "wb") as f:
            shutil.copyfileobj(resp, f)
        return True
    except: return False

def get_layer_from_api_tl(api_tl_path):
    try:
        with open(api_tl_path, 'r', encoding='utf-8') as f:
            txt = f.read()
        m = re.search(r'// LAYER (\d+)', txt)
        return int(m.group(1)) if m else None
    except: return None

# ==========================
#   MAIN CHECK FUNCTION
# ==========================
def check():
    try:
        import telethon
    except ImportError:
        print("[telethon_up]: Telethon not found, installing...")
        if not run_pip_install("telethon"): return

    with tempfile.TemporaryDirectory() as d:
        url_api = "https://raw.githubusercontent.com/telegramdesktop/tdesktop/dev/Telegram/SourceFiles/mtproto/scheme/api.tl"
        api_tl = os.path.join(d, "api.tl")
        
        if not safe_download(url_api, api_tl): return
        latest = get_layer_from_api_tl(api_tl)
        
        telethon = force_reload()
        current = telethon.tl.alltlobjects.LAYER

        if current < latest:
            print(f"[telethon_up]: Updating Layer {current} → {latest}...")
            
            zip_urls = [
                "https://codeberg.org/Lonami/Telethon/archive/v1.zip",
                "https://github.com/amirwolf512k/telethon/archive/v1.zip",
                "https://github.com/LonamiWebs/Telethon/archive/v1.zip"
            ]
            tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip").name
            download_success = False
            for url in zip_urls:
                if safe_download(url, tmp_zip):
                    download_success = True
                    continue
            if download_success:
                extract_dir = os.path.join(os.path.dirname(__file__), "Telethon_temp")
                try:
                    if os.path.exists(extract_dir): shutil.rmtree(extract_dir)
                    with zipfile.ZipFile(tmp_zip, "r") as z:
                        z.extractall(extract_dir)
                    
                    folder = next((os.path.join(extract_dir, f) for f in os.listdir(extract_dir) if f.startswith("Telethon")), None)
                    
                    if folder:
                        target_api = os.path.join(folder, "telethon_generator", "data", "api.tl")
                        os.makedirs(os.path.dirname(target_api), exist_ok=True)
                        shutil.copy(api_tl, target_api)
                        if run_pip_install(".", "--force-reinstall", cwd=folder):
                            force_reload()
                            print(f"[telethon_up]: Successfully updated to Layer {latest}")
                finally:
                    if os.path.exists(tmp_zip): os.unlink(tmp_zip)
                    shutil.rmtree(extract_dir, ignore_errors=True)
        else:
            print(f"[telethon_up]: Telethon is up-to-date (Layer {current})")