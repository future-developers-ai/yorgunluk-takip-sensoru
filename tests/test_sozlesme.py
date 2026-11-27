import pandas as pd
import pytest

from src.sozlesme import BLENDSHAPE_ADLARI, MATRIS_SUTUNLARI, SUTUNLAR, dogrula


def ornek():
    df = pd.DataFrame(0.0, index=range(3), columns=SUTUNLAR)
    df["t_s"] = [0.0, 1 / 15, 2 / 15]
    df["yuz_var"] = [True, False, True]
    df["parlaklik"] = 100.0
    df.loc[1, BLENDSHAPE_ADLARI + MATRIS_SUTUNLARI] = float("nan")
    return df


def test_parquet_gidip_gelme(tmp_path):
    df = ornek()
    path = tmp_path / "F1_kisi03_10.parquet"
    df.to_parquet(path, index=False)
    okunan = pd.read_parquet(path)
    once = okunan.copy(deep=True)
    assert dogrula(okunan) is None
    pd.testing.assert_frame_equal(okunan, once)


@pytest.mark.parametrize("durum", [
    "eksik", "fazla", "tekrar_sutun", "bos", "tekrar_zaman", "ters_zaman",
    "negatif_zaman", "sonsuz_zaman", "bos_zaman", "tamsayi_yuz", "bos_yuz",
    "skor_aralik", "skor_bos", "matris_sonsuz", "matris_bos", "yuz_yok_skor",
    "parlaklik_aralik", "parlaklik_bos", "metin_skor",
])
def test_gecersiz_veri(durum):
    df = ornek()
    if durum == "eksik":
        df = df.drop(columns="jawOpen")
    elif durum == "fazla":
        df["fazla"] = 0
    elif durum == "tekrar_sutun":
        df = pd.concat([df, df[["jawOpen"]]], axis=1)
    elif durum == "bos":
        df = df.iloc[:0]
    elif durum == "tekrar_zaman":
        df.loc[1, "t_s"] = 0.0
    elif durum == "ters_zaman":
        df = df.iloc[::-1]
    elif durum == "negatif_zaman":
        df.loc[0, "t_s"] = -1.0
    elif durum == "sonsuz_zaman":
        df.loc[2, "t_s"] = float("inf")
    elif durum == "bos_zaman":
        df.loc[0, "t_s"] = float("nan")
    elif durum == "tamsayi_yuz":
        df["yuz_var"] = [1, 0, 1]
    elif durum == "bos_yuz":
        df["yuz_var"] = pd.Series([True, None, True], dtype="boolean")
    elif durum == "skor_aralik":
        df.loc[0, "jawOpen"] = 1.1
    elif durum == "skor_bos":
        df.loc[0, "jawOpen"] = float("nan")
    elif durum == "matris_sonsuz":
        df.loc[0, "m00"] = float("inf")
    elif durum == "matris_bos":
        df.loc[0, "m00"] = float("nan")
    elif durum == "yuz_yok_skor":
        df.loc[1, "jawOpen"] = 0.0
    elif durum == "parlaklik_aralik":
        df.loc[0, "parlaklik"] = 256.0
    elif durum == "parlaklik_bos":
        df.loc[0, "parlaklik"] = float("nan")
    elif durum == "metin_skor":
        df["jawOpen"] = "0.5"
    with pytest.raises(ValueError):
        dogrula(df)


def test_yuz_olmayan_video():
    df = ornek()
    df["yuz_var"] = False
    df[BLENDSHAPE_ADLARI + MATRIS_SUTUNLARI] = float("nan")
    dogrula(df)


def test_sinirlar_ve_sutun_sirasi():
    df = ornek()
    df.loc[0, BLENDSHAPE_ADLARI] = 1.0
    df.loc[0, "parlaklik"] = 255.0
    df.loc[2, "parlaklik"] = 0.0
    df.loc[0, "m03"] = -10.0
    dogrula(df.loc[:, list(reversed(SUTUNLAR))])
