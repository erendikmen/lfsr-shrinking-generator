#!/bin/zsh
set -e
cd "$(dirname "$0")"

APP_NAME="ShrinkingGeneratorSimulator"
PY_FILE="ShrinkingGeneratorSimulator.pyw"
VENV_DIR=".venv_mac_build"

echo "=========================================="
echo " Shrinking Generator Simulator - macOS App Builder"
echo "=========================================="

if ! command -v python3 >/dev/null 2>&1; then
  echo "HATA: Python 3 bulunamadı."
  echo "Python 3 kurduktan sonra bu dosyayı tekrar çalıştır."
  read -k 1 -s "?Kapatmak için herhangi bir tuşa bas..."
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "Python sanal ortamı oluşturuluyor..."
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "Gerekli paketler kuruluyor/güncelleniyor..."
python -m pip install --upgrade pip
python -m pip install --upgrade pyinstaller

echo "macOS uygulaması oluşturuluyor..."
pyinstaller --noconfirm --windowed --name "$APP_NAME" "$PY_FILE"

echo ""
echo "Tamamlandı kral!"
echo "Uygulama burada oluştu:"
echo "dist/$APP_NAME.app"
echo ""
echo "Finder'da dist klasörü açılıyor..."
open dist

echo ""
read -k 1 -s "?Kapatmak için herhangi bir tuşa bas..."
