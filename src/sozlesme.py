"""Ortak parquet sütunları ve veri doğrulaması."""

import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype

BLENDSHAPE_ADLARI = [
    "_neutral", "browDownLeft", "browDownRight", "browInnerUp", "browOuterUpLeft",
    "browOuterUpRight", "cheekPuff", "cheekSquintLeft", "cheekSquintRight",
    "eyeBlinkLeft", "eyeBlinkRight", "eyeLookDownLeft", "eyeLookDownRight",
    "eyeLookInLeft", "eyeLookInRight", "eyeLookOutLeft", "eyeLookOutRight",
    "eyeLookUpLeft", "eyeLookUpRight", "eyeSquintLeft", "eyeSquintRight",
    "eyeWideLeft", "eyeWideRight", "jawForward", "jawLeft", "jawOpen", "jawRight",
    "mouthClose", "mouthDimpleLeft", "mouthDimpleRight", "mouthFrownLeft",
    "mouthFrownRight", "mouthFunnel", "mouthLeft", "mouthLowerDownLeft",
    "mouthLowerDownRight", "mouthPressLeft", "mouthPressRight", "mouthPucker",
    "mouthRight", "mouthRollLower", "mouthRollUpper", "mouthShrugLower",
    "mouthShrugUpper", "mouthSmileLeft", "mouthSmileRight", "mouthStretchLeft",
    "mouthStretchRight", "mouthUpperUpLeft", "mouthUpperUpRight",
    "noseSneerLeft", "noseSneerRight",
]
MATRIS_SUTUNLARI = [f"m{i}{j}" for i in range(4) for j in range(4)]
SUTUNLAR = ["t_s", "yuz_var", *BLENDSHAPE_ADLARI, *MATRIS_SUTUNLARI, "parlaklik"]

DURUMLAR = ["uyanik", "hafif_uykulu", "yorgun", "belirsiz"]
ISARETLER = ["uzun_kapanma", "bas_dusmesi", "perclos_yuksek", "sik_esneme"]
UYARILAR = ["yok", "yazi", "ses"]


def dogrula(df: pd.DataFrame) -> None:
    """Sözleşmeye aykırı tabloda ValueError verir; tabloyu değiştirmez.

    Sütunların giriş sırası serbesttir. Yazarken SUTUNLAR sırası kullanılır.
    yuz_var boolean olmalıdır. Yüz yokken skor ve matrisler boş kalır.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df bir pandas DataFrame olmalı")
    if not df.columns.is_unique:
        raise ValueError("Tekrarlanan sütun adları var")
    eksik = set(SUTUNLAR) - set(df.columns)
    fazla = set(df.columns) - set(SUTUNLAR)
    if eksik:
        raise ValueError(f"Eksik sütun: {sorted(eksik)}")
    if fazla:
        raise ValueError(f"Fazla sütun: {sorted(fazla)}")
    if df.empty:
        raise ValueError("Tablo boş olamaz")
    if not is_bool_dtype(df["yuz_var"]) or df["yuz_var"].isna().any():
        raise ValueError("yuz_var boş olmayan boolean olmalı")
    sayisal = ["t_s", *BLENDSHAPE_ADLARI, *MATRIS_SUTUNLARI, "parlaklik"]
    for ad in sayisal:
        if not is_numeric_dtype(df[ad]) or is_bool_dtype(df[ad]):
            raise ValueError(f"{ad} sayısal olmalı")
    zaman = df["t_s"]
    if (zaman.isna().any() or not zaman.ge(0).all()
            or zaman.isin([float("inf"), float("-inf")]).any()
            or not zaman.is_monotonic_increasing or zaman.duplicated().any()):
        raise ValueError("t_s sonlu, negatif olmayan ve kesin artan olmalı")
    if df["parlaklik"].isna().any() or not df["parlaklik"].between(0, 255).all():
        raise ValueError("parlaklik boş olmayan 0-255 arası sayı olmalı")
    yuz = df["yuz_var"]
    bs = df.loc[yuz, BLENDSHAPE_ADLARI]
    if bs.isna().any().any() or not ((bs >= 0) & (bs <= 1)).all().all():
        raise ValueError("Yüz varken blendshape boş olamaz ve 0-1 aralığında olmalı")
    matris = df.loc[yuz, MATRIS_SUTUNLARI]
    if matris.isna().any().any() or matris.isin([float("inf"), float("-inf")]).any().any():
        raise ValueError("Yüz varken matris değerleri sonlu ve dolu olmalı")
    if df.loc[~yuz, BLENDSHAPE_ADLARI + MATRIS_SUTUNLARI].notna().any().any():
        raise ValueError("Yüz yokken blendshape ve matris değerleri boş olmalı")
