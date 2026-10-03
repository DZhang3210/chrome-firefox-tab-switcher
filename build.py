"""Build a helper release from the VERSION file.

VERSION is the helper's version only. It's bundled into the helper (reported by "ping") and used
as the installer's version. The extensions keep their own version in their manifest.json, so
extension-only changes don't need a new helper release. Builds the helper with PyInstaller and
compiles the installer. Run from the project root with the venv's Python:

    .venv\\Scripts\\python build.py
"""
import os, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent
ISCC_CANDIDATES = [
    pathlib.Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
    pathlib.Path(os.environ.get("LOCALAPPDATA", ""), r"Programs\Inno Setup 6\ISCC.exe"),
]

version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
if not re.fullmatch(r"\d+(\.\d+){0,3}", version):
    sys.exit(f"VERSION must look like 1.2 or 1.2.3 (Windows version format), got {version!r}")
print(f"== Building Tab Ferry helper {version}")

# 1. Helper: one-folder build, with VERSION bundled next to the code for read_version()
subprocess.run(
    [sys.executable, "-m", "PyInstaller", "--onedir", "--noconfirm",
     "--add-data", f"{ROOT / 'VERSION'}{os.pathsep}.", str(ROOT / "app" / "tab_transfer.py")],
    cwd=ROOT, check=True,
)

# 2. Installer: the .iss reads VERSION itself
iscc = next((p for p in ISCC_CANDIDATES if p.is_file()), None)
if iscc is None:
    sys.exit("ISCC.exe not found - is Inno Setup 6 installed?")
subprocess.run([str(iscc), "/Q", str(ROOT / "installer" / "tab_transfer.iss")], check=True)

print(f"== Done: {ROOT / 'installer' / 'Output' / 'TabFerrySetup.exe'} (version {version})")
