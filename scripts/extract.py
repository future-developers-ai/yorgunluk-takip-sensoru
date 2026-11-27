"""Videoları kare kare sayı tablosuna (.parquet) çevirir.

Kullanım:
    python scripts/extract.py data/uta/Fold4
    python scripts/extract.py data/uta/Fold1/01/5.mov --cikti data/parquet

Klasör yapısı .../Fold<n>.../<kişi>/<etiket>.<uzantı> olmalıdır. Çıktı adı
docs/sozlesme.md'deki F{fold}_kisi{NN}_{etiket}.parquet biçimindedir.
Her kaynak kare bir satırdır. Görüntü saklanmaz.
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import cv2
import mediapipe  # noqa: F401  Windows: pandas/pyarrow'dan önce yüklenmeli
import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK))

from src.sozlesme import BLENDSHAPE_ADLARI, MATRIS_SUTUNLARI, SUTUNLAR, dogrula

UZANTILAR = {".mov", ".mp4", ".m4v", ".avi"}
ETIKETLER = {"0", "5", "10"}


def cikti_adi(video: Path) -> str:
    """Yoldan fold, kişi ve etiketi okuyup parquet dosya adını döndürür."""
    video = Path(video).resolve()
    # birden fazla eşleşme varsa kişi klasörüne en yakın olan geçerlidir
    foldlar = re.findall(r"fold(\d+)", video.parent.parent.as_posix(), re.IGNORECASE)
    kisi = video.parent.name
    if not foldlar or not kisi.isdigit() or video.stem not in ETIKETLER:
        raise ValueError(f"Yol .../Fold<n>/<kişi>/<0|5|10>.<uzantı> biçiminde değil: {video}")
    return f"F{foldlar[-1]}_kisi{int(kisi):02d}_{video.stem}.parquet"


def satir(obs, t_s: float) -> dict:
    """FaceObs'u sözleşme satırına çevirir. Yüz yoksa skor ve matris NaN kalır."""
    sonuc = dict.fromkeys(SUTUNLAR, np.nan)
    sonuc["t_s"] = t_s
    sonuc["yuz_var"] = bool(obs.yuz_var)
    sonuc["parlaklik"] = float(obs.parlaklik)
    if obs.yuz_var:
        for ad in BLENDSHAPE_ADLARI:
            sonuc[ad] = obs.blendshapes[ad]
        # satır satır: m00, m01, ... m33
        matris = np.asarray(obs.transformation_matrix, dtype=float).reshape(16)
        sonuc.update(zip(MATRIS_SUTUNLARI, matris))
    return sonuc


def _ac(video: Path, gecici: Path) -> cv2.VideoCapture:
    """Videoyu açar; OpenCV açamazsa ffmpeg ile mp4'e çevirip yeniden dener."""
    cap = cv2.VideoCapture(str(video))
    okunuyor = cap.isOpened() and cap.grab()
    cap.release()
    if okunuyor:
        cap = cv2.VideoCapture(str(video))
        # telefon videoları döndürme bilgisini üstbilgide taşır; OpenCV 4.11 kendisi uygulamaz
        cap.set(cv2.CAP_PROP_ORIENTATION_AUTO, 1)
        return cap
    cevrilen = gecici / "cevrilen.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-an",
         "-c:v", "libx264", "-crf", "18", str(cevrilen)],
        check=True,
    )
    cap = cv2.VideoCapture(str(cevrilen))
    if not cap.isOpened():
        raise RuntimeError(f"Video açılamadı: {video}")
    return cap


def isle(video: Path) -> pd.DataFrame:
    """Bir videonun bütün karelerini işler."""
    from capture.tracker import YuzAnalizci

    satirlar = []
    with tempfile.TemporaryDirectory() as gecici:
        cap = _ac(video, Path(gecici))
        try:
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            onceki_t, onceki_ms = -1.0, -1
            # her video için yeni analizci: video modu artan zaman damgası ister
            with YuzAnalizci() as analizci:
                while True:
                    ok, kare = cap.read()
                    if not ok:
                        break
                    t_s = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                    if t_s <= onceki_t or t_s < 0:
                        t_s = max(onceki_t + 1.0 / fps, 0.0)
                    ms = max(round(t_s * 1000), onceki_ms + 1)
                    satirlar.append(satir(analizci.analiz_et(kare, ms), t_s))
                    onceki_t, onceki_ms = t_s, ms
        finally:
            cap.release()
    if not satirlar:
        raise RuntimeError(f"Videoda okunabilen kare yok: {video}")
    return pd.DataFrame(satirlar, columns=SUTUNLAR).astype({"yuz_var": bool})


def videolar(girdi: Path) -> list[Path]:
    if girdi.is_file():
        return [girdi]
    return sorted(p for p in girdi.rglob("*") if p.is_file() and p.suffix.lower() in UZANTILAR)


def main() -> int:
    # Windows'ta çıktı dosyaya yönlendirilince Türkçe harfler çökertmesin
    for akis in (sys.stdout, sys.stderr):
        akis.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("girdi", type=Path, help="video dosyası ya da klasör")
    parser.add_argument("--cikti", type=Path, default=KOK / "data" / "parquet")
    parser.add_argument("--uzerine-yaz", action="store_true", help="var olan çıktıyı yeniden üret")
    args = parser.parse_args()

    liste = videolar(args.girdi)
    if not liste:
        print(f"Video bulunamadı: {args.girdi}")
        return 1
    args.cikti.mkdir(parents=True, exist_ok=True)

    islenen, atlanan, hatali = 0, 0, []
    for video in liste:
        try:
            hedef = args.cikti / cikti_adi(video)
            if hedef.exists() and not args.uzerine_yaz:
                atlanan += 1
                continue
            df = isle(video)
            dogrula(df)
            yarim = hedef.with_suffix(".yarim")
            df.to_parquet(yarim, index=False)
            yarim.replace(hedef)
            islenen += 1
            print(f"{hedef.name}: {len(df)} kare, yüz yok %{100 * (~df['yuz_var']).mean():.1f}",
                  flush=True)
        except Exception as hata:  # noqa: BLE001  bir video bozuksa gece çalışması durmasın
            hatali.append(f"{video}: {hata}")
            print(f"HATA {video}: {hata}", flush=True)

    print(f"\nİşlenen: {islenen}  Atlanan (zaten var): {atlanan}  Hatalı: {len(hatali)}")
    for h in hatali:
        print("  " + h)
    return 1 if hatali else 0


if __name__ == "__main__":
    sys.exit(main())
