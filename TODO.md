# Task: Make real audio → real translation

- [ ] Fix/verify real STT + translation is enabled by env: MOCK_VAD=false, MOCK_TRANSCRIPTION=false, MOCK_DIARIZATION=false, MOCK_TRANSLATION=false
- [ ] Fix audio encoding mismatch: frontend sends Float32 PCM but backend/AI expects float32 raw bytes; ensure sample format/rate and base64 payload alignment
- [ ] Implement chunk boundary / endpointing so FE can dispatch only when a sentence/segment ends (use VAD timestamps + buffer on FE or BE)
- [ ] Add explicit API contract for websocket chunk: send duration/samplerate and/or use a VAD-based “finalize segment” message
- [ ] Add BE logic to return incremental segments without duplicating transcript entries
- [ ] Add manual test scripts (curl/websocket client) to validate:
  - [ ] real STT from audio
  - [ ] real translation from text
  - [ ] segmentation behavior with partial audio
- [ ] Run system tests / smoke tests after changes

