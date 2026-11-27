"""eval/olcutler.py: elle hesaplanmış küçük örnek."""

import pytest

from eval.olcutler import VideoSonucu, olcutler


def kayit(t_s, durum, uyari=False):
    return {"t_s": t_s, "durum": durum, "neden": "", "uyari": uyari}


def video(katilimci, sinif, *kayitlar, sure=600.0):
    return VideoSonucu(katilimci, sinif, sure, list(kayitlar))


ORNEK = [
    # kişi 1: 0 < 5 < 10 sırası tutuyor
    video(1, 0, kayit(0, "uyanik"), kayit(100, "yorgun", True), kayit(101, "yorgun"),
          kayit(110, "uyanik")),
    video(1, 5, kayit(0, "uyanik"), kayit(100, "hafif_uykulu"), kayit(200, "uyanik")),
    video(1, 10, kayit(0, "uyanik"), kayit(300, "yorgun", True), kayit(500, "uyanik")),
    # kişi 2: uykulu videosunda hiç yorgun yok
    video(2, 0, kayit(0, "uyanik"), kayit(300, "belirsiz")),
    video(2, 5, kayit(0, "uyanik")),
    video(2, 10, kayit(0, "uyanik")),
]


def test_elle_hesaplanan_degerler():
    s = olcutler(ORNEK)
    # 0 videoları toplam 1200 sn, 1 uyarı -> 10 dakikada 0.5
    assert s["yanlis_alarm_10dk"] == pytest.approx(0.5)
    assert s["uykulu_yakalama"] == pytest.approx(0.5)
    assert s["kisi_ici_ayrim"] == pytest.approx(0.5)
    assert s["kisi_ici_siralama"] == pytest.approx(0.5)
    assert s["belirsiz_orani"] == pytest.approx(300 / 3600)


def test_yanlis_alarm_kare_degil_uyari_sayar():
    cok_kayit = video(1, 0, kayit(0, "yorgun", True),
                      *[kayit(t, "yorgun") for t in range(1, 600)])
    assert olcutler([cok_kayit])["yanlis_alarm_10dk"] == pytest.approx(1.0)


def test_veri_yoksa_none():
    s = olcutler([video(1, 0, kayit(0, "uyanik"))])
    assert s["uykulu_yakalama"] is None and s["kisi_ici_siralama"] is None
