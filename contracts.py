"""
Ortak Veri Tipleri ve Sözleşmeler (contracts.py)

Tüm modüllerin ortak kullandığı veri sınıfları bu dosyada toplanır.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Literal
import numpy as np

from src.sozlesme import DURUMLAR, ISARETLER


@dataclass
class Frame:
    """Kaynak görüntü ve videonun/oturumun başlangıcına göre zamanı."""

    t_s: float  # saniye
    goruntu: Optional[np.ndarray] = None  # OpenCV BGR, uint8; sahte veride None


@dataclass
class FaceObs:
    """Tek bir video karesindeki yüz gözlem verisi.

    Yüz algılanamadığında (yuz_var=False) tüm skor ve matris alanları None olur.
    """
    timestamp_ms: int = 0  # milisaniye; MediaPipe arayüzüyle geriye uyumlu
    yuz_var: bool = False

    # 52 Blendshape skor sözlüğü: {"eyeBlinkLeft": 0.05, ...}
    blendshapes: Optional[Dict[str, float]] = None  # her skor 0–1

    # Hızlı ve doğrudan erişim için temel alanlar
    eye_blink_left: Optional[float] = None  # 0 açık, 1 kapalı
    eye_blink_right: Optional[float] = None  # 0 açık, 1 kapalı
    jaw_open: Optional[float] = None  # 0 kapalı, 1 açık

    # 4x4 yüz dönüş matrisi (facial transformation matrix, 16 eleman)
    transformation_matrix: Optional[np.ndarray] = None  # 4×4 dönüş matrisi; açı değil

    # 478 Yüz işaretçisi (Normalized landmarklar: x, y, z)
    landmarks: Optional[np.ndarray] = None  # normalize MediaPipe koordinatları

    # Görüntü parlaklığı (0 - 255)
    parlaklik: Optional[float] = None  # gri ton ortalaması, 0–255

    @property
    def t_s(self) -> float:
        """Kuralların kullandığı saniye cinsinden zaman."""
        return self.timestamp_ms / 1000.0

    @property
    def eyeBlinkLeft(self) -> Optional[float]:
        """Sözleşme uyumluluğu için camelCase getter."""
        return self.eye_blink_left

    @property
    def eyeBlinkRight(self) -> Optional[float]:
        """Sözleşme uyumluluğu için camelCase getter."""
        return self.eye_blink_right

    @property
    def jawOpen(self) -> Optional[float]:
        """Sözleşme uyumluluğu için camelCase getter."""
        return self.jaw_open


@dataclass
class Features:
    """Özellik modüllerinin ortak ölçümleri; ölçülemeyen alan None kalır."""

    t_s: float  # saniye
    yuz_var: bool
    goz_kapali_skor: Optional[float] = None  # 0 açık, 1 kapalı
    perclos: Optional[float] = None  # pencere içindeki kapalı kare oranı, 0–1
    kapali_sure_s: Optional[float] = None  # kesintisiz göz kapanması, saniye
    jaw_open: Optional[float] = None  # ağız açıklığı, 0–1
    esneme_sayisi: Optional[int] = None  # yapılandırılan penceredeki olay sayısı
    pitch_deg: Optional[float] = None  # kalibre nötr başa göre derece; öne eğilme pozitif
    yaw_deg: Optional[float] = None  # kalibre nötr başa göre derece; sağa dönüş pozitif
    parlaklik: Optional[float] = None  # gri ton ortalaması, 0–255


@dataclass
class Isaret:
    """Göz, esneme veya baş modülünün bulgusu; tek başına karar değildir."""

    ad: str  # ISARETLER listesindeki ad
    guc: Literal["guclu", "zayif"]  # birimsiz
    t_s: float  # saniye
    neden: str  # örnek: goz_kapali_1.6s

    def __post_init__(self) -> None:
        if self.ad not in ISARETLER:
            raise ValueError(f"Geçersiz işaret: {self.ad}")
        beklenen = "guclu" if self.ad in ("uzun_kapanma", "bas_dusmesi") else "zayif"
        if self.guc != beklenen:
            raise ValueError(f"{self.ad} işaretinin gücü {beklenen} olmalı")


@dataclass
class Vote:
    """Yalnızca görünürlük/belirsiz kuralının oyu; göz, ağız ve baş Isaret üretir."""

    t_s: float  # saniye
    neden: str  # yuz_yok, karanlik veya bas_asiri_donuk gibi açıklama
    durum: Literal["belirsiz"] = "belirsiz"  # birimsiz

    def __post_init__(self) -> None:
        if self.durum != "belirsiz":
            raise ValueError("Vote yalnızca belirsiz durumu için kullanılır")


@dataclass
class Decision:
    """Karar ve histerezis çıktısı. Uyarı alanını uyarı modülü belirler."""

    t_s: float  # saniye; mevcut kayıt zamanı
    durum: str  # DURUMLAR listesinden
    baslangic_s: float  # saniye; mevcut durumun başladığı zaman
    neden: str = ""  # birden fazla gerekçe varsa ';' ile birleştirilir
    uyari: bool = False  # bu kayıtta yeni uyarı üretildi mi?

    def __post_init__(self) -> None:
        if self.durum not in DURUMLAR:
            raise ValueError(f"Geçersiz durum: {self.durum}")
        if not isinstance(self.uyari, bool):
            raise ValueError("uyari boolean olmalı")
        if not 0 <= self.baslangic_s <= self.t_s:
            raise ValueError("0 <= baslangic_s <= t_s olmalı")

    def json_kaydi(self) -> dict:
        """ClickUp panel biçimi; durum başlangıcı içeride tutulur."""
        return {"t_s": self.t_s, "durum": self.durum,
                "neden": self.neden, "uyari": self.uyari}
