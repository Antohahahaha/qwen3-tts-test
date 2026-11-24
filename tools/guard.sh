#!/usr/bin/env bash
# Защитные проверки: нет аудио в репозитории; нужные секреты заданы (значения не печатаются).
set -e
if git ls-files | grep -Ei '\.(wav|mp3|m4a|ogg|opus|flac|aac|aiff|b64|enc|tar)$'; then echo "Audio/archive tracked in repo - aborting"; exit 1; fi
[ -n "$REF_AUDIO_B64" ] || { echo "Secret REF_AUDIO_B64 is missing"; exit 1; }
[ -n "$ARTIFACT_PASS" ] || { echo "Secret ARTIFACT_PASS is missing (output must be encrypted)"; exit 1; }
if [ "$NEED_REF_TEXT" = "true" ]; then [ -n "$REF_TEXT" ] || { echo "Secret REF_TEXT is missing"; exit 1; }; fi
echo "guards ok"
