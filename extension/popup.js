const INSERT_FAKE_TEXT_MESSAGE = "VOICE_DICTATION_INSERT_FAKE_TEXT";
const FAKE_TRANSCRIPT = "This is fake dictation text.";

const insertButton = document.querySelector("#insertFakeText");
const statusText = document.querySelector("#status");

function setStatus(message) {
  statusText.textContent = message;
}

async function getActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

async function insertFakeText() {
  insertButton.disabled = true;
  setStatus("Checking active field...");

  try {
    const tab = await getActiveTab();

    if (!tab?.id) {
      setStatus("No active tab found.");
      return;
    }

    chrome.tabs.sendMessage(
      tab.id,
      {
        type: INSERT_FAKE_TEXT_MESSAGE,
        text: FAKE_TRANSCRIPT,
      },
      (response) => {
        insertButton.disabled = false;

        if (chrome.runtime.lastError) {
          setStatus("Open or reload a normal web page first.");
          return;
        }

        setStatus(response?.message || "Unable to insert test text.");
      },
    );
  } catch (_error) {
    insertButton.disabled = false;
    setStatus("Unable to reach the active tab.");
  }
}

insertButton.addEventListener("click", insertFakeText);
