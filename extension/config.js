(() => {
  const DEFAULT_BACKEND_URL = "https://voice-dictation-extension.onrender.com/api/transcribe";
  const PRODUCTION_BACKEND_ORIGIN = "https://voice-dictation-extension.onrender.com";
  const TRANSCRIPTION_PATH = "/api/transcribe";

  function validateBackendUrl(value) {
    try {
      const url = new URL(value);
      const isLocalHttp = url.protocol === "http:" && ["127.0.0.1", "localhost"].includes(url.hostname);
      const isProductionBackend = url.origin === PRODUCTION_BACKEND_ORIGIN;
      const isXaiHost = url.hostname === "x.ai" || url.hostname.endsWith(".x.ai");

      if (!isLocalHttp && !isProductionBackend) {
        return { ok: false, message: "Use the production backend, or localhost for development." };
      }

      if (isXaiHost) {
        return { ok: false, message: "Use your backend URL, not an xAI URL." };
      }

      if (url.username || url.password || url.search || url.hash) {
        return { ok: false, message: "Backend URL must not include credentials, a query, or a fragment." };
      }

      if (!url.pathname.endsWith(TRANSCRIPTION_PATH)) {
        return { ok: false, message: `Backend URL must end with ${TRANSCRIPTION_PATH}.` };
      }

      return { ok: true, url: url.toString() };
    } catch (_error) {
      return { ok: false, message: "Enter a valid backend URL." };
    }
  }

  function normalizeBackendUrl(value) {
    const result = validateBackendUrl(value || DEFAULT_BACKEND_URL);
    return result.ok ? result.url : DEFAULT_BACKEND_URL;
  }

  function getHealthUrl(value) {
    const url = new URL(normalizeBackendUrl(value));
    url.pathname = url.pathname.slice(0, -TRANSCRIPTION_PATH.length) + "/health";
    return url.toString();
  }

  globalThis.VoiceDictationConfig = Object.freeze({
    DEFAULT_BACKEND_URL,
    getHealthUrl,
    normalizeBackendUrl,
    validateBackendUrl,
  });
})();
