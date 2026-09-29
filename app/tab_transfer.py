import glob, json, os, struct, subprocess, sys, tempfile, time, traceback, winreg

# Keep in sync with AppVersion in installer/tab_transfer.iss and LATEST_VERSION in popup.js
VERSION = "1.2"

LOG_PATH = os.path.join(tempfile.gettempdir(), "tab_transfer.log")

def log_error(text):
    # Logging must never stop a tab from being sent, so any failure here is ignored.
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {os.getpid()} {text}\n")
    except OSError:
        pass

EXE_NAMES = {"chrome": "chrome.exe", "firefox": "firefox.exe"}

def find_browser(name):
    # Same lookup Windows uses for Win+R: the App Paths key, per-user first, then machine-wide
    key_path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{EXE_NAMES[name]}"
    for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        try:
            with winreg.OpenKey(hive, key_path) as key:
                exe, _ = winreg.QueryValueEx(key, "")
                return exe.strip('"')
        except FileNotFoundError:
            continue
    raise FileNotFoundError(f"{name} is not installed")

def read_message():
    raw_len = sys.stdin.buffer.read(4)               # first 4 bytes = message length
    length = struct.unpack("<I", raw_len)[0]
    return json.loads(sys.stdin.buffer.read(length))

def send_message(obj):
    data = json.dumps(obj).encode("utf-8")
    sys.stdout.buffer.write(struct.pack("<I", len(data)))
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()

def launch_detached(args):
    # Browsers kill the helper's child processes when the helper exits.
    # Breaking away from that job lets the launched program keep running.
    try:
        subprocess.Popen(args, creationflags=subprocess.CREATE_BREAKAWAY_FROM_JOB | subprocess.DETACHED_PROCESS)
    except PermissionError:
        # This job doesn't allow breakaway; launching normally beats not launching at all
        subprocess.Popen(args, creationflags=subprocess.DETACHED_PROCESS)

def handle(msg):
    action = msg.get("action", "open")
    if action == "ping":
        return {"ok": True, "version": VERSION}
    if action == "uninstall":
        # Inno Setup puts its uninstaller next to the helper; it asks the user to confirm
        uninstallers = glob.glob(os.path.join(os.path.dirname(sys.executable), "unins*.exe"))
        if not uninstallers:
            raise FileNotFoundError("Uninstaller not found - was the helper installed with TabTransferSetup.exe?")
        launch_detached([uninstallers[0]])
        return {"ok": True}
    launch_detached([find_browser(msg["target"]), msg["url"]])
    return {"ok": True}

try:
    msg = read_message()
    try:
        send_message(handle(msg))
    except Exception as e:
        log_error(f"launch failed for {msg}:\n{traceback.format_exc()}")
        send_message({"ok": False, "error": str(e)})
except BaseException:
    log_error(f"crashed:\n{traceback.format_exc()}")
    raise
