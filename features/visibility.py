"""Görünürlük ölçümü: yüz var mı, ne kadar süredir kayıp, görüntü ne kadar parlak.

Eşik ve karar içermez; bunlar belirsiz kuralındadır.

Canlıda parlaklik_hesapla(frame.goruntu) ya da FaceObs.parlaklik, veri setinde
.parquet dosyasının parlaklik sütunu GorunurlukOlcer.guncelle'ye verilir.
"""

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class Gorunurluk:
    t_s: float  # saniye
    yuz_var: bool
    yuz_kayip_s: float  # yüzün kesintisiz kayıp olduğu süre, saniye; yüz varken 0
    parlaklik: float  # gri ton ortalaması, 0–255


def parlaklik_hesapla(goruntu: np.ndarray) -> float:
    """BGR ya da gri uint8 görüntünün ortalama parlaklığı (0–255)."""
    if goruntu.ndim == 3:
        goruntu = cv2.cvtColor(goruntu, cv2.COLOR_BGR2GRAY)
    return float(np.mean(goruntu))


class GorunurlukOlcer:
    """Kareleri zaman sırasıyla alır. Her video ya da oturum için yeni nesne kurulur."""

    def __init__(self) -> None:
        self._son_t: float | None = None
        self._kayip_baslangic: float | None = None  # ilk yüzsüz karenin zamanı

    def guncelle(self, t_s: float, yuz_var: bool, parlaklik: float) -> Gorunurluk:
        if self._son_t is not None and t_s < self._son_t:
            raise ValueError(f"Zaman geri gitti: {self._son_t} -> {t_s}")
        self._son_t = t_s
        if yuz_var:
            self._kayip_baslangic = None
            kayip = 0.0
        else:
            if self._kayip_baslangic is None:
                self._kayip_baslangic = t_s
            kayip = t_s - self._kayip_baslangic
        return Gorunurluk(t_s, bool(yuz_var), kayip, float(parlaklik))
