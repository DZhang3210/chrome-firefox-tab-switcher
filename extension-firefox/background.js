const api = globalThis.browser ?? chrome;
const IS_FIREFOX = api.runtime.getURL("").startsWith("moz-extension://");
const TARGET = IS_FIREFOX ? "chrome" : "firefox";
const LABEL = `Send to ${IS_FIREFOX ? "Chrome" : "Firefox"}`;
const menus = api.menus ?? api.contextMenus;

// Removing the extension can't remove the helper app, so point people to instructions for it
api.runtime.setUninstallURL("https://github.com/DZhang3210/chrome-firefox-tab-switcher#uninstalling");

// Create the right-click menu items once, on install
api.runtime.onInstalled.addListener(() => {
  menus.create({
    id: "send-page",
    title: LABEL,
    // "tab" = right-click on the tab itself, which only Firefox supports
    contexts: IS_FIREFOX ? ["page", "tab"] : ["page"],
  });
  menus.create({ id: "send-link", title: `Open link in ${TARGET}`, contexts: ["link"] });
});

// Right-click handler
menus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "send-link") send(info.linkUrl);
  else if (info.menuItemId === "send-page") sendTab(tab);
});

async function sendTab(tab) {
  const ok = await send(tab.url);
  if (ok) api.tabs.remove(tab.id); // close it here = "move"; delete this line for "copy"
}

async function send(url) {
  if (!/^https?:/.test(url)) return false; // skip chrome://, about:, etc.
  try {
    const reply = await api.runtime.sendNativeMessage("tab_transfer", { url, target: TARGET });
    return reply?.ok === true;
  } catch (err) {
    console.error("Tab Transfer failed:", err);
    return false;
  }
}