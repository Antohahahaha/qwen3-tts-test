# qwen3-tts-test
Клон голоса Qwen3-TTS Base на CPU GitHub Actions. Репозиторий публичный: **аудио и референсы сюда не загружаются**.
Референс (`REF_AUDIO_B64`), его точный текст (`REF_TEXT`) и пароль шифрования результата (`ARTIFACT_PASS`) хранятся только в Settings → Secrets → Actions.
Результат в артефакте зашифрован: `openssl enc -d -aes-256-cbc -pbkdf2 -md sha256 -in test.wav.enc -out test.wav -pass pass:ВАШ_ПАРОЛЬ`
