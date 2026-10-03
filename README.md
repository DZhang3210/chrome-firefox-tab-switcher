# Tab Ferry

Send tabs and links between **Chrome** and **Firefox** with a right-click.

Browsers can't open other browsers on their own, so Tab Ferry has two parts: a browser extension for each browser, and a small helper app for Windows that opens the link in the other browser.

```
Firefox extension ─┐                          ┌─▶ opens the tab in Chrome
                   ├─▶ Tab Ferry helper ───┤
Chrome extension  ─┘    (Windows app)         └─▶ opens the tab in Firefox
```

## Install

1. **Install the extension** in one or both browsers:
   - Firefox: *coming soon to addons.mozilla.org*
   - Chrome: *coming soon to the Chrome Web Store*
2. **Install the helper app**: download [`TabFerrySetup.exe`](https://github.com/DZhang3210/chrome-firefox-tab-switcher/releases/latest/download/TabFerrySetup.exe) from the [latest release](https://github.com/DZhang3210/chrome-firefox-tab-switcher/releases/latest) and run it.
   - Windows 10/11, 64-bit. No admin rights needed.
   - If Windows shows **"Windows protected your PC"**, click **More info → Run anyway**. The installer isn't code-signed yet; everything it installs is built from the source in this repository.

After installing the extension, a welcome page walks you through these steps and shows when the helper is detected.

## Usage

- **Right-click a page** → **Send to Chrome** / **Send to Firefox**. The page opens in the other browser and the tab closes. In Firefox, you can also right-click a tab.
- **Right-click a link** → **Open link in chrome** / **Open link in firefox** to open just that link.
- **Click the Tab Ferry icon** in the toolbar to check the helper's status: *You're all set*, *Update available*, or setup instructions.

Only regular web pages (`http` and `https`) can be sent. Browser-internal pages like `chrome://settings` or `about:config` are skipped.

## Privacy

Tab Ferry collects no data. The only thing the extension sends is the URL of the tab or link you choose, and only to the helper app on your own computer, which passes it straight to the other browser. Nothing is sent over the internet.

If something goes wrong, the helper writes the error to `%TEMP%\tab_transfer.log`. Nothing is logged during normal use.

## Uninstalling
Tab Ferry has three parts, and each one is removed separately:
1. **The helper app**: open the extension's popup and click **Uninstall helper app**, or go to **Settings → Apps → Installed apps → Tab Ferry Helper → Uninstall**. This removes its files and registry keys.
2. **The Chrome extension**: `chrome://extensions` → Tab Ferry → **Remove**.
3. **The Firefox extension**: `about:addons` → Tab Ferry → **⋯ → Remove**.

Removing an extension doesn't remove the helper app, since both extensions share it. If you still use Tab Ferry in the other browser, keep the helper installed.

## Troubleshooting

**The popup says the helper isn't installed, but I installed it.**
Reopen the popup, or click **check again**. If it still isn't detected, run the installer again: it repairs the registry entries the browsers use to find the helper.

**Sending does nothing.**
Open the popup first. If it shows *Update available*, install the latest helper. Also check that the page is a regular website, not a browser-internal page.

**Something else went wrong.**
Check `%TEMP%\tab_transfer.log` (paste that into Win+R to open it) and [open an issue](https://github.com/DZhang3210/chrome-firefox-tab-switcher/issues) with its contents.

## Building from source

Requirements: Windows, Python 3.10+, [Inno Setup 6](https://jrsoftware.org/isinfo.php), and Node.js (for `web-ext`).

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install pyinstaller
```

There are two kinds of versions:
- **The helper app's version** lives in the `VERSION` file. `build.py` builds the helper with PyInstaller and compiles the installer with that version.
- **Each extension's version** lives in its own `manifest.json`, so extension-only changes (icons, text, fixes) can ship without a new helper release. The popup only asks users to update the helper when it's older than `MIN_HELPER_VERSION` in `popup.js`.

To build the helper and installer:

```powershell
.venv\Scripts\python build.py
```

The installer is written to `installer\Output\TabFerrySetup.exe`. To package the extensions for the stores:

```powershell
npx web-ext build --source-dir extension-firefox --artifacts-dir web-ext-artifacts/firefox --overwrite-dest
npx web-ext build --source-dir extension-chrome --artifacts-dir web-ext-artifacts/chrome --overwrite-dest
```

### Project layout

| Path | Contents |
|---|---|
| `extension-chrome/`, `extension-firefox/` | The browser extensions: right-click menu, popup, and welcome page |
| `app/tab_transfer.py` | The helper app (native messaging host) |
| `app/*.json`, `app/tab_transfer_win.bat` | Host manifests and launcher for running the helper from source |
| `installer/` | Inno Setup script and the host manifests used by the installer |
| `build.py`, `VERSION` | Release build script and the single version number |
| `docs/how-it-works.md` | A walkthrough of how each piece works |

## License

[MIT](LICENSE)
