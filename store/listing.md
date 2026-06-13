# Chrome Web Store Listing Draft

## Product Details

Name: Voice Dictation Browser Extension

Category: Productivity

Language: English

Short description:

> Dictate text into supported web fields using your microphone and a secure speech-to-text backend.

Detailed description:

> Voice Dictation adds a small microphone control beside supported text fields. Click Mic, speak a short phrase, stop recording, and the returned transcript is inserted into the field you selected.
>
> Recording begins only after an explicit click and can be stopped immediately. The extension ignores password, payment, hidden, disabled, readonly, file, checkbox, and radio fields.
>
> Audio is sent over HTTPS to the Voice Dictation backend and processed by xAI Speech-to-Text. The xAI API key remains on the backend and is never included in the extension.
>
> The MVP has no accounts, payments, advertising, background recording, or real-time streaming.

## Single Purpose

Allow users to dictate short text into supported web input fields by recording audio after an explicit user action, sending it to a speech-to-text backend, and inserting the returned transcript into the selected field.

## Permission Justifications

`storage`:

Stores the backend URL and recording-duration preference locally in Chrome. No account or cloud synchronization is used.

Site access on HTTPS pages:

Required to detect when the user focuses a supported text field, display the Mic control beside that field, and insert the transcript back into that same field. The extension does not collect browsing history, page URLs, existing field contents, or surrounding page content.

Localhost page access:

Supports local manual QA and development using the repository's test page.

Backend host access:

Allows the Manifest V3 service worker to send user-triggered audio to `https://voice-dictation-extension.onrender.com` and to local FastAPI instances during development. The extension never calls an xAI host directly.

`activeTab` is intentionally not requested because declarative content scripts already provide the page access required by the feature.

## Privacy Dashboard Draft

Remote code: No. All JavaScript executed by the extension is packaged in the extension ZIP. Network responses are treated as data, not executable code.

Data handled:

- User-provided audio.
- Returned transcript, which may contain personal communications or other user-generated content.
- Extension settings stored locally.
- Focused field metadata inspected locally for compatibility and safety checks.

Data not collected or transmitted:

- Browsing history or a list of visited URLs.
- Existing webpage field contents.
- Password or payment-field contents.
- Advertising identifiers, analytics, or account information.

Dashboard guidance:

- Do not select a declaration claiming that the extension handles no user data.
- Declare the dashboard categories that cover user-provided audio, transcripts, personal communications, user-generated content, and form data as presented by the current dashboard.
- Certify that data is used only for the extension's disclosed single purpose, is not sold, is not used for advertising or lending, and is transferred only as needed to provide transcription.
- Enter the public HTTPS URL for `PRIVACY.md` in the designated Privacy Policy field.

## Reviewer Test Instructions

1. Install the submitted ZIP.
2. Open an HTTPS webpage containing a normal text input or textarea.
3. Focus the field and confirm that the Mic button appears.
4. Click Mic and allow microphone access.
5. Speak a short phrase and click Stop, or wait for the recording limit.
6. Confirm that the transcription status completes and text appears in the focused field.
7. Open the popup and click Test Backend to verify the production backend health endpoint.

No test account or credentials are required. The production backend must have the submitted extension ID configured in CORS before review.

## Listing Links

Homepage: `https://github.com/fredjkhar/voice-dictation-extension`

Support: `https://github.com/fredjkhar/voice-dictation-extension/issues`

Privacy policy after it is publicly available: `https://github.com/fredjkhar/voice-dictation-extension/blob/main/PRIVACY.md`
