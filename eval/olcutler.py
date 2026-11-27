"""Veri rehberindeki başarı hedeflerinin hesabı.

Girdi, her video için uyarı çıktısının JSON kayıtlarıdır (docs/sozlesme.md):
kayıtlar her durum değişiminde ve saniyede bir yazılır; bir durum sonraki
kayda kadar sürer. Kalibrasyonda kullanılan süre çağıran tarafından hem
kayıtlardan hem video süresinden çıkarılmış olmalıdır.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class VideoSonucu:
    katilimci: int
    sinif: int  # 0, 5, 10
    sure_s: float  # ölçüme katılan süre
    kayitlar: list[dict]  # t_s sırasıyla; t_s videonun sonunu aşmaz


def sure(video: VideoSonucu, *durumlar: str) -> float:
    """Videoda verilen durumlarda geçen toplam saniye."""
    if not video.kayitlar:
        return 0.0
    son = video.kayitlar[0]["t_s"] + video.sure_s
    zamanlar = [k["t_s"] for k in video.kayitlar[1:]] + [son]
    return sum(
        max(sonraki - k["t_s"], 0.0)
        for k, sonraki in zip(video.kayitlar, zamanlar)
        if k["durum"] in durumlar
    )


def yorgun_uyari_sayisi(video: VideoSonucu) -> int:
    return sum(1 for k in video.kayitlar if k["uyari"] and k["durum"] == "yorgun")


def _oran(pay: float, payda: float) -> float | None:
    return pay / payda if payda else None


def olcutler(videolar: list[VideoSonucu]) -> dict[str, float | None]:
    """Hesaplanamayan ölçüt None olur."""
    uyanik = [v for v in videolar if v.sinif == 0]
    uykulu = [v for v in videolar if v.sinif == 10]
    kisiler: dict[int, dict[int, VideoSonucu]] = {}
    for v in videolar:
        kisiler.setdefault(v.katilimci, {})[v.sinif] = v

    ayrim = [k for k in kisiler.values() if {0, 10} <= k.keys()]
    siralama = [k for k in kisiler.values() if {0, 5, 10} <= k.keys()]

    def uykulu_sure(v: VideoSonucu) -> float:
        return sure(v, "hafif_uykulu", "yorgun")

    alarm = _oran(sum(map(yorgun_uyari_sayisi, uyanik)), sum(v.sure_s for v in uyanik))
    return {
        "yanlis_alarm_10dk": None if alarm is None else alarm * 600,
        "uykulu_yakalama": _oran(sum(yorgun_uyari_sayisi(v) > 0 for v in uykulu), len(uykulu)),
        "kisi_ici_ayrim": _oran(
            sum(sure(k[10], "yorgun") > sure(k[0], "yorgun") for k in ayrim), len(ayrim)
        ),
        "kisi_ici_siralama": _oran(
            sum(uykulu_sure(k[0]) < uykulu_sure(k[5]) < uykulu_sure(k[10]) for k in siralama),
            len(siralama),
        ),
        "belirsiz_orani": _oran(
            sum(sure(v, "belirsiz") for v in videolar), sum(v.sure_s for v in videolar)
        ),
    }
