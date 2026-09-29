const api = globalThis.browser ?? chrome;

const status = document.getElementById("helper-status");
const download = document.getElementById("helper-download");

async function checkHelper() {
  let installed = false;
  try {
    await api.runtime.sendNativeMessage("tab_transfer", { action: "ping" });
    installed = true; // any reply means the helper is installed and runs
  } catch {
    // not installed yet
  }
  status.textContent = installed
    ? "✓ The helper app is installed. You're ready to go."
    : "The helper app isn't installed yet.";
  status.classList.toggle("ok", installed);
  download.hidden = installed;
}

// Re-check when the user comes back to this tab, e.g. after running the installer
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") checkHelper();
});
document.getElementById("recheck").addEventListener("click", checkHelper);

checkHelper();
