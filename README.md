# chrome-firefox-tab-switcher
## What is the manifest.json for?
- We define the `background` which essentially allows us to check and detect keypresses
- We define the `icons`
- We define `permissions`, so what it can primarily do
- It defines a new command called `send_tab`, which we will later attach a resultant action in `background.js`

## What happens in background.js?
- We define what happens in the menu. The context defines in what context they appear. For example, we get different when right click a tab vs when we right click a web page
- Then we add a listener, and notice how we can define different results on different webpages, based on the id of whatever got pressed, which we defined above. One more quirk is that when defining an extension we are only able to  track the resultant clicks of menus we created via the extension. This means that, when we use `else` there's no risk of us accidentally overwriting the affect of other menu items
- Below this, it might seem a bit confusing, since we don't have a menuItem with the id of `send-tab`; however, that makes sense, since its not linked to the menu, but rather the shortcut-id we defined in `manifest.json`
- The final code defines how we actually trigger the tab updates. We can do a lot with permissions of an extension, but in particular, we want to define an update of a seperate external browser, which, of course, requires some sort of external program to do so. Which is why we use `tab_transfer`.

## How are we going to hook up Native Messaging
- Firstly, before just using send on anything, we want to ensure we are not doing it any internal link. For example, anything starting with 'chrome://' since those would represent internal offline sites
- Next, when we send, we send to `tab_transfer`, which is a little convoluted in how it gets called. Inside the windows registry we can define external programs associated with extension, where their key would be `key_transfer` and the link is the absolute path to a special json, which defines the program and a couple other settings

## What does Tab_Transfer_(Chrome/Firefox) do?
- we define the path, which is a windows executable, and then we also define an allowed origin. In firefox, we set our own unique_id for the extension, and in chrome we get the extension id defined, for us, by chrome

## What does tab_transfer do?
- When using tab_transfer, there's a couple additional technicalities which need to be fully ironed out. When we read `utf-8`. It starts with an intial 4 byte length, which defines the length of the buffer. This has to be done, so that we can then subsequently we can load is a JSON. The operation of `json.loads` is automatically able to detect if something is a `dict` and shape it accordingly
- When sending a message the only sort of tricky thing is that we use `buffer.flush`. This essentially just confirms what we wrote and actually sends it to the program. For example, when you write something in a text message, you can compile a bunch of text, but it doesn't get sent until you specifically write send, which is exactly how this works.
- Then it creates a subprocess, to open the equivelant tab in chrome, which by default adds the tab into any preexisiting chrome instance rather than creating a seperate one.

## Uninstalling
Tab Transfer has three parts, and each one is removed separately:
1. **The helper app**: open the extension's popup and click **Uninstall helper app**, or go to **Settings → Apps → Installed apps → Tab Transfer Helper → Uninstall**. This removes its files and registry keys.
2. **The Chrome extension**: `chrome://extensions` → Tab Transfer → **Remove**.
3. **The Firefox extension**: `about:addons` → Tab Transfer → **⋯ → Remove**.

Removing an extension doesn't remove the helper app, since both extensions share it. If you still use Tab Transfer in the other browser, keep the helper installed.

## Additional Addendums
- Added the additional functionality to be able to automatically detect if the tab_switcher native app is downloads by having it send a `ping`
- Added 