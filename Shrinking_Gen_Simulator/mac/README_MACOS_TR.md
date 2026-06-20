# macOS Kullanım

## Direkt çalıştırma

Klasördeki `run_macos.command` dosyasına çift tıklayarak uygulamayı Python ile çalıştırabilirsin.

Alternatif olarak terminalden:

```bash
python3 ShrinkingGeneratorSimulator.pyw
```

## macOS `.app` oluşturma

Klasördeki `build_macos_app.command` dosyasına çift tıkla.

Bu dosya otomatik olarak:

1. Python sanal ortamı oluşturur
2. PyInstaller kurar
3. Uygulamayı macOS `.app` haline getirir

Çıktı şu klasörde oluşur:

```text
dist/ShrinkingGeneratorSimulator.app
```

## Not

macOS güvenlik uyarısı verirse uygulamaya sağ tıkla ve **Open / Aç** seçeneğini kullan.
