# How Tab Transfer works

A walkthrough of each piece of the project and why it's built the way it is.

## What is the manifest.json for?
- We define the `background` script, which runs the extension's event handlers: creating the right-click menu, reacting to menu clicks, and opening the welcome page on first install.
- We define the `icons`, and the toolbar `action` (its icon, tooltip and popup).
- We define `permissions`, so what the extension is allowed to do: `nativeMessaging` to talk to the helper app, `contextMenus` (`menus` in Firefox) for the right-click items, and `tabs` to read and close the tab being sent.
- The Firefox manifest also has `browser_specific_settings.gecko`: our own add-on ID, the minimum Firefox version, and the data collection declaration (`none`) that addons.mozilla.org requires.

## What happens in background.js?
- We define what happens in the right-click menu. The `contexts` define where each item appears. For example, we get different items when we right-click a tab vs. a web page vs. a link. Right-clicking a tab (the `tab` context) only exists in Firefox.
- Then we add a listener, and notice how we can react differently based on the `id` of whichever item got clicked, which we defined above. One quirk is that an extension only receives clicks on menu items it created itself. This means that there's no risk of us accidentally handling the clicks of other menu items.
- The final code defines how we actually move the tab. An extension can do a lot with its permissions, but it can't start another program, like a separate browser. That requires an external program, which is why we use the `tab_transfer` helper app.
- It also sets an uninstall URL: when someone removes the extension, the browser opens the README's Uninstalling section, since removing the extension can't remove the helper app.

## How is Native Messaging hooked up?
- Firstly, before sending anything, we make sure it isn't an internal page. For example, anything starting with `chrome://` or `about:` is a browser-internal page that the other browser couldn't open anyway.
- Next, when we send, we send to `tab_transfer`, which is a little roundabout in how it gets called. In the Windows registry, under `...\NativeMessagingHosts\tab_transfer` (one key for Chrome, one for Firefox), the value is the absolute path to a special JSON file, the host manifest, which defines the program and a couple of other settings.

## What do tab_transfer_(chrome/firefox).json do?
- They define the `path` of the program, which is a Windows executable, and which extensions are allowed to use it. In Firefox, we set our own unique ID for the extension (`allowed_extensions`); in Chrome, the extension ID is assigned for us by Chrome (`allowed_origins`).
- The `app/` versions point at `tab_transfer_win.bat` for running from source during development. The `installer/` versions point at the built `tab_transfer.exe`.

## What does tab_transfer do?
- When reading a message, there are a couple of technicalities. Each message starts with a 4-byte length, which says how long the rest of the message is. We read exactly that many bytes, which are UTF-8 JSON, and `json.loads` turns them into a Python `dict`.
- When sending a reply, the only tricky part is `buffer.flush()`. Writes first collect in a buffer, and flushing actually sends them to the browser. Like a text message: you can type a bunch of text, but it doesn't get sent until you press send, which is exactly how this works.
- Each message says what to do with an `action` field:
  - no `action`: open `url` in the `target` browser. This is the original behavior.
  - `ping`: reply with the helper's version, which the popup uses to show "You're all set" or "Update available".
  - `uninstall`: start the Inno Setup uninstaller that sits next to the helper. It asks the user to confirm first.
- To open the other browser, it looks up the browser's location in the Windows registry (the same `App Paths` entry that Win+R uses), then starts it with `subprocess.Popen`. By default, the new tab goes into any already-running window of that browser rather than a separate one.
- The browser is started with the `CREATE_BREAKAWAY_FROM_JOB` flag. Browsers put their helper app in a Windows "job", which kills everything inside it when the helper exits. Without breaking away, a browser that wasn't already running would open and then immediately close.

## Why is the helper built as a folder, not a single .exe?
- A PyInstaller `--onefile` build unpacks Python into a temporary folder every time it runs. When Firefox launched it, loading Python from that folder failed ("Failed to load Python DLL"), so every send from Firefox failed. A `--onedir` build keeps Python next to `tab_transfer.exe`, so nothing has to be unpacked. It also starts faster.

## Where does the version number come from?
- The `VERSION` file in the project root is the single source. `build.py` copies it into both extension manifests and bundles it into the helper; the installer script reads it directly.
- The popup compares the helper's version (from `ping`) with the extension's own version, to show when the helper needs an update.
