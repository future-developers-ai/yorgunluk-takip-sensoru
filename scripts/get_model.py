"""
MediaPipe modelini indirme betiği (scripts/get_model.py)

Kullanım:
    python scripts/get_model.py
"""

from pathlib import Path
import sys

# Proje kökünü sys.path'e ekle
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from capture.tracker import model_kontrol_ve_indir, varsayilan_model_yolu


def main() -> None:
    hedef = varsayilan_model_yolu()
    print(f"Hedef model yolu: {hedef}")
    indirilen = model_kontrol_ve_indir(hedef)
    print(f"Model hazır: {indirilen} (Boyut: {indirilen.stat().st_size:,} bayt)")


if __name__ == "__main__":
    main()
