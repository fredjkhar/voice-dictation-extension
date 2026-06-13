const INSERT_FAKE_TEXT_MESSAGE = "VOICE_DICTATION_INSERT_FAKE_TEXT";
const TEST_BACKEND_MESSAGE = "VOICE_DICTATION_TEST_BACKEND";
const FAKE_TRANSCRIPT = "This is fake dictation text.";
const DEFAULT_RECORDING_DURATION_SECONDS = 5;
const MIN_RECORDING_DURATION_SECONDS = 1;
const MAX_RECORDING_DURATION_SECONDS = 30;
const { DEFAULT_BACKEND_URL, validateBackendUrl } = globalThis.VoiceDictationConfig;

const insertButton = document.querySelector("#insertFakeText");
const saveSettingsButton = document.querySelector("#saveSettings");
const testBackendButton = document.querySelector("#testBackend");
const backendUrlInput = document.querySelector("#backendUrl");
const recordingDurationInput = document.querySelector("#recordingDurationSeconds");
const statusText = document.querySelector("#status");

function setStatus(message) {
  statusText.textContent = message;
}

async function getActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

function normalizeRecordingDurationSeconds(value) {
  const duration = Number(value);

  if (!Number.isFinite(duration)) {
    return DEFAULT_RECORDING_DURATION_SECONDS;
  }

  return Math.min(
    MAX_RECORDING_DURATION_SECONDS,
    Math.max(MIN_RECORDING_DURATION_SECONDS, Math.round(duration)),
  );
}

async function loadSettings() {
  const settings = await chrome.storage.local.get({
    backendUrl: DEFAULT_BACKEND_URL,
    recordingDurationMs: DEFAULT_RECORDING_DURATION_SECONDS * 1000,
  });

  const backendUrl = validateBackendUrl(settings.backendUrl);

  backendUrlInput.value = backendUrl.ok ? backendUrl.url : DEFAULT_BACKEND_URL;
  recordingDurationInput.value = String(normalizeRecordingDurationSeconds(settings.recordingDurationMs / 1000));
}

async function saveSettings() {
  const backendUrl = validateBackendUrl(backendUrlInput.value.trim());

  if (!backendUrl.ok) {
    setStatus(backendUrl.message);
    backendUrlInput.focus();
    return;
  }

  const recordingDurationSeconds = normalizeRecordingDurationSeconds(recordingDurationInput.value);

  await chrome.storage.local.set({
    backendUrl: backendUrl.url,
    recordingDurationMs: recordingDurationSeconds * 1000,
  });

  backendUrlInput.value = backendUrl.url;
  recordingDurationInput.value = String(recordingDurationSeconds);
  setStatus("Settings saved.");
}

async function testBackend() {
  const backendUrl = validateBackendUrl(backendUrlInput.value.trim());

  if (!backendUrl.ok) {
    setStatus(backendUrl.message);
    backendUrlInput.focus();
    return;
  }

  testBackendButton.disabled = true;
  setStatus("Checking backend...");

  try {
    const response = await chrome.runtime.sendMessage({
      type: TEST_BACKEND_MESSAGE,
      backendUrl: backendUrl.url,
    });

    setStatus(response?.message || "Backend check failed.");
  } catch (_error) {
    setStatus("Unable to check the backend.");
  } finally {
    testBackendButton.disabled = false;
  }
}

async function insertFakeText() {
  insertButton.disabled = true;
  setStatus("Checking active field...");

  try {
    const tab = await getActiveTab();

    if (!tab?.id) {
      setStatus("No active tab found.");
      insertButton.disabled = false;
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
saveSettingsButton.addEventListener("click", saveSettings);
testBackendButton.addEventListener("click", testBackend);
loadSettings();
