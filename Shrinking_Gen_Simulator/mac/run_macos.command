#!/bin/zsh
set -e
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 bulunamadı. Lütfen python.org veya Homebrew üzerinden Python 3 kur."
  read -k 1 -s "?Kapatmak için herhangi bir tuşa bas..."
  exit 1
fi

echo "Shrinking Generator Simulator başlatılıyor..."
python3 ShrinkingGeneratorSimulator.pyw
