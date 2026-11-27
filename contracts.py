"""
Ortak Veri Tipleri ve Sözleşmeler (contracts.py)

Tüm modüllerin ortak kullandığı veri sınıfları bu dosyada toplanır.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import numpy as np


@dataclass
class FaceObs:
    """Tek bir video karesindeki yüz gözlem verisi.

    Yüz algılanamadığında (yuz_var=False) tüm skor ve matris alanları None olur.
    """
    timestamp_ms: int = 0
    yuz_var: bool = False

    # 52 Blendshape skor sözlüğü: {"eyeBlinkLeft": 0.05, ...}
    blendshapes: Optional[Dict[str, float]] = None

    # Hızlı ve doğrudan erişim için temel alanlar
    eye_blink_left: Optional[float] = None
    eye_blink_right: Optional[float] = None
    jaw_open: Optional[float] = None

    # 4x4 yüz dönüş matrisi (facial transformation matrix, 16 eleman)
    transformation_matrix: Optional[np.ndarray] = None

    # 478 Yüz işaretçisi (Normalized landmarklar: x, y, z)
    landmarks: Optional[np.ndarray] = None

    # Görüntü parlaklığı (0 - 255)
    parlaklik: Optional[float] = None

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
