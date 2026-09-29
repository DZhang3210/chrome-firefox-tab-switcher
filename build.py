"""Build a release from the single VERSION file.

Stamps the version into both extension manifests, builds the helper with PyInstaller,
and compiles the installer. Run from the project root with the venv's Python:

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
    sys.exit(f"VERSION must look like 1.2 or 1.2.3 (browsers require it), got {version!r}")
print(f"== Building Tab Transfer {version}")

# 1. Extension manifests: replace only the top-level "version" value, keeping each file's formatting
for browser in ("chrome", "firefox"):
    path = ROOT / f"extension-{browser}" / "manifest.json"
    text = path.read_text(encoding="utf-8")
    new_text, count = re.subn(r'("version"\s*:\s*")[^"]*(")', rf"\g<1>{version}\g<2>", text, count=1)
    if count != 1:
        sys.exit(f'No "version" field found in {path}')
    path.write_text(new_text, encoding="utf-8")
    print(f"   {path.relative_to(ROOT)} -> {version}")

# 2. Helper: one-folder build, with VERSION bundled next to the code for read_version()
subprocess.run(
    [sys.executable, "-m", "PyInstaller", "--onedir", "--noconfirm",
     "--add-data", f"{ROOT / 'VERSION'}{os.pathsep}.", str(ROOT / "app" / "tab_transfer.py")],
    cwd=ROOT, check=True,
)

# 3. Installer: the .iss reads VERSION itself
iscc = next((p for p in ISCC_CANDIDATES if p.is_file()), None)
if iscc is None:
    sys.exit("ISCC.exe not found - is Inno Setup 6 installed?")
subprocess.run([str(iscc), "/Q", str(ROOT / "installer" / "tab_transfer.iss")], check=True)

print(f"== Done: {ROOT / 'installer' / 'Output' / 'TabTransferSetup.exe'} (version {version})")
print("   Reload both extensions to pick up the new manifest version.")
