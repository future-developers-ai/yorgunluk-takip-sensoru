"""Belirsiz kuralı: sistem göremiyorsa tahmin uydurmak yerine `belirsiz` oyu verir.

Yalnızca oy üretir. Yorgunluk kararını ezmez; öncelik karar modülündedir.
Eşikler config.toml dosyasının [visibility] bölümünden okunur.
"""

from dataclasses import dataclass
from pathlib import Path

import tomllib

from contracts import Vote
from features.visibility import Gorunurluk

CONFIG = Path(__file__).resolve().parent.parent / "config.toml"


@dataclass(frozen=True)
class BelirsizAyari:
    yuz_kayip_s: float  # yüz bundan uzun süre kayıpsa, saniye
    parlaklik_esik: float  # parlaklık bunun altındaysa, 0–255
    yaw_esik_derece: float  # |yaw| bunu aşıyorsa, derece


def ayar_oku(yol: Path = CONFIG) -> BelirsizAyari:
    with open(yol, "rb") as dosya:
        return BelirsizAyari(**tomllib.load(dosya)["visibility"])


def belirsiz_oyu(
    gorunurluk: Gorunurluk, yaw_deg: float | None, ayar: BelirsizAyari
) -> Vote | None:
    """yaw_deg kalibre edilmiş açıdır; ölçülemiyorsa None."""
    nedenler = []
    if not gorunurluk.yuz_var and gorunurluk.yuz_kayip_s > ayar.yuz_kayip_s:
        nedenler.append("yuz_yok")
    if gorunurluk.parlaklik < ayar.parlaklik_esik:
        nedenler.append("karanlik")
    if yaw_deg is not None and abs(yaw_deg) > ayar.yaw_esik_derece:
        nedenler.append("bas_asiri_donuk")
    if not nedenler:
        return None
    return Vote(t_s=gorunurluk.t_s, neden=";".join(nedenler))
