from dataclasses import dataclass

@dataclass(frozen=True)
class Ayar:
    islem_fps: int = 15
    # göz
    goz_kapali_esik: float = 0.5        # eyeBlink ortalaması bunun üstündeyse kapalı
    uzun_kapanma_s: float = 1.5
    perclos_pencere_s: float = 60.0
    perclos_esik: float = 0.15
    # ağız
    esneme_jaw_esik: float = 0.5
    esneme_min_s: float = 1.0
    sik_esneme_sayi: int = 2
    sik_esneme_pencere_dk: float = 3.0
    # baş
    bas_dusme_derece: float = 15.0
    bas_dusme_sure_s: float = 1.0
    # belirsiz
    yaw_belirsiz_derece: float = 60.0
    karanlik_esik: float = 40.0
    # kalibrasyon
    kalibrasyon_s: float = 60.0

AYAR = Ayar()
