"""rules/belirsiz.py: görünürlük oyu."""

import pytest

from features.visibility import Gorunurluk
from rules.belirsiz import BelirsizAyari, ayar_oku, belirsiz_oyu

AYAR = BelirsizAyari(yuz_kayip_s=1.0, parlaklik_esik=40.0, yaw_esik_derece=60.0)


def olcum(yuz_var=True, yuz_kayip_s=0.0, parlaklik=120.0):
    return Gorunurluk(t_s=5.0, yuz_var=yuz_var, yuz_kayip_s=yuz_kayip_s, parlaklik=parlaklik)


def test_yuz_yok():
    oy = belirsiz_oyu(olcum(yuz_var=False, yuz_kayip_s=2.0), None, AYAR)
    assert (oy.durum, oy.neden, oy.t_s) == ("belirsiz", "yuz_yok", 5.0)


def test_karanlik():
    assert belirsiz_oyu(olcum(parlaklik=5.0), 0.0, AYAR).neden == "karanlik"


@pytest.mark.parametrize("yaw", [70.0, -70.0])
def test_yaw_70(yaw):
    assert belirsiz_oyu(olcum(), yaw, AYAR).neden == "bas_asiri_donuk"


def test_yaw_30_belirsiz_degil():
    assert belirsiz_oyu(olcum(), 30.0, AYAR) is None


def test_normal_operator():
    assert belirsiz_oyu(olcum(), 0.0, AYAR) is None


def test_kisa_yuz_kaybi_oy_vermez():
    assert belirsiz_oyu(olcum(yuz_var=False, yuz_kayip_s=0.5), None, AYAR) is None


def test_birden_fazla_neden_birlesir():
    oy = belirsiz_oyu(olcum(parlaklik=5.0), 70.0, AYAR)
    assert oy.neden == "karanlik;bas_asiri_donuk"


def test_ayar_dosyadan_okunur(tmp_path):
    yol = tmp_path / "config.toml"
    yol.write_text(
        "[visibility]\nyuz_kayip_s = 2.5\nparlaklik_esik = 30\nyaw_esik_derece = 45\n",
        encoding="utf-8",
    )
    assert ayar_oku(yol) == BelirsizAyari(2.5, 30, 45)
