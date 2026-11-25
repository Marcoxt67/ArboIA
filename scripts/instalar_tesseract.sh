#!/usr/bin/env bash
# Instala Tesseract + idiomas pt/en SEM sudo, dentro de .ferramentas/.
# O ia/ocr.py detecta e configura automaticamente este binário.
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMP="/tmp/opencode/arboia-debs"
DEST="$RAIZ/.ferramentas"

PACOTES=(
  tesseract-ocr
  libtesseract5
  liblept5
  tesseract-ocr-eng
  tesseract-ocr-por
)

echo "🌳 ARboIA — baixando Tesseract local (sem sudo)..."
mkdir -p "$TEMP" "$DEST"
cd "$TEMP"

for pacote in "${PACOTES[@]}"; do
  apt-get download "$pacote"
done

for deb in ./*.deb; do
  dpkg -x "$deb" "$DEST"
done

BINARIO="$DEST/usr/bin/tesseract"
if [[ ! -x "$BINARIO" ]]; then
  echo "❌ Binário não encontrado em $BINARIO" >&2
  exit 1
fi

export LD_LIBRARY_PATH="$DEST/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export TESSDATA_PREFIX="$DEST/usr/share/tesseract-ocr/5/tessdata"

echo "✅ Instalado: $($BINARIO --version 2>&1 | head -1)"
echo "✅ Idiomas:"; ls "$TESSDATA_PREFIX" | sed 's/^/   - /'
echo
echo "O ia/ocr.py já encontra esse binário automaticamente."
echo "Para testar: python3 -c 'from ia.ocr import TESSERACT_USADO; print(TESSERACT_USADO)'"
