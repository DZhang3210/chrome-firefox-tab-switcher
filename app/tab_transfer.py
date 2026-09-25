import json, struct, subprocess, sys

BROWSERS = {
    "chrome":  
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox": 
    r"C:\Program Files\Mozilla Firefox\firefox.exe",
}

def read_message():
    raw_len = sys.stdin.buffer.read(4)               # first 4 bytes = message length
    length = struct.unpack("<I", raw_len)[0]
    return json.loads(sys.stdin.buffer.read(length))

def send_message(obj):
    data = json.dumps(obj).encode("utf-8")
    sys.stdout.buffer.write(struct.pack("<I", len(data)))
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()

msg = read_message()
try:
    subprocess.Popen(
        [BROWSERS[msg["target"]], msg["url"]],
        # Browsers kill the helper's child processes when the helper exits.
        # These flags let the launched browser keep running.
        creationflags=subprocess.CREATE_BREAKAWAY_FROM_JOB | subprocess.DETACHED_PROCESS,
    )
    send_message({"ok": True})
except Exception as e:
    send_message({"ok": False, "error": str(e)})