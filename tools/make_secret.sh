#!/usr/bin/env bash
# Запускать на своём Mac. Результат только в буфер обмена, файлов в репозитории не создаёт.
# Использование: ./tools/make_secret.sh /путь/к/записи.wav   (запись 6-10 с, чистая речь)
set -euo pipefail
IN="${1:?Укажите путь к записи}"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
if command -v ffmpeg >/dev/null 2>&1; then
  ffmpeg -v error -y -i "$IN" -t 10 -ac 1 -ar 24000 -c:a libopus -b:a 24k "$TMP/ref.ogg"; OUT="$TMP/ref.ogg"
else
  afconvert "$IN" "$TMP/ref.m4a" -f m4af -d aac -b 24000 -c 1; OUT="$TMP/ref.m4a"
fi
B64="$(base64 < "$OUT" | tr -d '\n')"
N=${#B64}; echo "Размер секрета: $N символов (лимит GitHub: 48000)"
[ "$N" -le 48000 ] || { echo "Слишком большой. Возьмите запись короче (6-10 с)."; exit 1; }
printf '%s' "$B64" | pbcopy
echo "Скопировано в буфер обмена. Вставьте как секрет REF_AUDIO_B64."
