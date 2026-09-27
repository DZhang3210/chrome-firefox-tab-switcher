import json, struct, subprocess, sys, os

EXE_NAMES = {"chrome": "chrome.exe", "firefox": "firefox.exe"}

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
    os.startfile(EXE_NAMES[msg["target"]], arguments=msg["url"])
    send_message({"ok": True})
except Exception as e:
    send_message({"ok": False, "error": str(e)})