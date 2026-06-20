# Shrinking Generator Interactive Simulator v2


## Çalıştırma

Bilgisayarında Python varsa:

```text
run_with_python.bat
```

veya doğrudan:

```text
python ShrinkingGeneratorSimulator.pyw
```

## EXE üretme

Windows üzerinde `build_windows_exe.bat` dosyasını çalıştır.

EXE şu klasörde oluşur:

```text
dist/ShrinkingGeneratorSimulator.exe
```

## Not

Sıfır seed verilirse VHDL kodundaki gibi all-zero lock-up durumunu engellemek için seed otomatik olarak all-ones yapılır.

