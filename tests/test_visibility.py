"""features/visibility.py: yüz kaybı süresi ve parlaklık."""

import json
from pathlib import Path

import numpy as np
import pytest

from features.visibility import GorunurlukOlcer, parlaklik_hesapla


def kayip_sureleri(dizi):
    olcer = GorunurlukOlcer()
    return [olcer.guncelle(t, yuz, 100.0).yuz_kayip_s for t, yuz in dizi]


def test_yuz_kayip_suresi_birikir_ve_sifirlanir():
    dizi = [(0.0, True), (1.0, False), (1.5, False), (3.0, False), (4.0, True), (5.0, False)]
    assert kayip_sureleri(dizi) == pytest.approx([0.0, 0.0, 0.5, 2.0, 0.0, 0.0])


def test_video_yuzsuz_baslayabilir():
    assert kayip_sureleri([(0.0, False), (2.0, False)]) == pytest.approx([0.0, 2.0])


def test_olcum_girdileri_aynen_tasir():
    olcum = GorunurlukOlcer().guncelle(2.5, True, 73.0)
    assert (olcum.t_s, olcum.yuz_var, olcum.parlaklik) == (2.5, True, 73.0)


def test_geri_giden_zaman_reddedilir():
    olcer = GorunurlukOlcer()
    olcer.guncelle(2.0, True, 100.0)
    with pytest.raises(ValueError):
        olcer.guncelle(1.0, True, 100.0)


def test_karanlik_goruntu_belirgin_dusuk():
    karanlik = np.full((48, 64, 3), 8, dtype=np.uint8)
    aydinlik = np.full((48, 64, 3), 150, dtype=np.uint8)
    assert parlaklik_hesapla(karanlik) == pytest.approx(8, abs=1)
    assert parlaklik_hesapla(aydinlik) == pytest.approx(150, abs=1)


def test_gri_goruntu_de_olculur():
    assert parlaklik_hesapla(np.full((4, 4), 40, dtype=np.uint8)) == 40.0


@pytest.mark.parametrize("ad", ["bas_dusmesi_yuz_kaybi", "karanlik"])
def test_sahte_senaryolar(ad):
    yol = Path(__file__).parent / "fixtures" / f"{ad}.json"
    kayitlar = json.loads(yol.read_text(encoding="utf-8"))["kayitlar"]
    olcer = GorunurlukOlcer()
    ilk_kayip = None
    for kayit in kayitlar:
        obs = kayit["face_obs"]
        t_s = obs["timestamp_ms"] / 1000.0
        olcum = olcer.guncelle(t_s, obs["yuz_var"], obs["parlaklik"])
        if obs["yuz_var"]:
            ilk_kayip = None
        elif ilk_kayip is None:
            ilk_kayip = t_s
        beklenen = 0.0 if ilk_kayip is None else t_s - ilk_kayip
        assert olcum.yuz_kayip_s == pytest.approx(beklenen)
        assert olcum.parlaklik == obs["parlaklik"]
