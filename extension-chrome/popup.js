const api = globalThis.browser ?? chrome;
const HOST = "tab_transfer";
// Oldest helper this extension works with. Bump it only when the extension starts relying on
// something new in the helper - not for extension-only changes (icons, text, popup fixes).
const MIN_HELPER_VERSION = "1.2";

const uninstallFooter = document.getElementById("uninstall-footer");
const uninstallButton = document.getElementById("uninstall");
const manualUninstall = document.getElementById("manual-uninstall");

function show(state) {
  for (const section of document.querySelectorAll("[data-state]")) {
    section.hidden = section.dataset.state !== state;
  }
  // Uninstall is offered on every screen except while checking or once it has started
  uninstallFooter.hidden = state === "checking" || state === "uninstalling";
  manualUninstall.hidden = true;
}

function isOlder(version, than) {
  const a = version.split(".").map(Number);
  const b = than.split(".").map(Number);
  for (let i = 0; i < Math.max(a.length, b.length); i++) {
    const diff = (a[i] ?? 0) - (b[i] ?? 0);
    if (diff !== 0) return diff < 0;
  }
  return false;
}

async function check() {
  show("checking");
  let reply;
  try {
    reply = await api.runtime.sendNativeMessage(HOST, { action: "ping" });
  } catch {
    show("missing"); // helper isn't installed (or can't be started)
    return;
  }
  // Helpers before 1.2 don't understand "ping" and reply without a version
  const version = reply?.version;
  for (const el of document.querySelectorAll(".version")) {
    el.textContent = version ?? "1.1 or earlier";
  }
  show(!version || isOlder(version, MIN_HELPER_VERSION) ? "outdated" : "ready");
}

uninstallButton.addEventListener("click", async () => {
  uninstallButton.disabled = true;
  let started = false;
  try {
    const reply = await api.runtime.sendNativeMessage(HOST, { action: "uninstall" });
    started = reply?.ok === true;
  } catch {
    // No helper responded - fall through to the manual instructions
  }
  uninstallButton.disabled = false;
  // Helpers before 1.2 can't uninstall themselves, and a missing or broken helper can't
  // either, so point to Settings, which can always remove it
  if (started) show("uninstalling");
  else manualUninstall.hidden = false;
});

for (const button of document.querySelectorAll(".recheck")) {
  button.addEventListener("click", check);
}

check();
