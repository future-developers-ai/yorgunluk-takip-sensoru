"""
Sistem Genel Ayarları ve Eşik Değerleri (src/ayar.py)

Tüm modüllerin (göz, ağız/esneme, baş açısı, görünürlük, karar ve uyarı)
kullanacağı eşik, süre ve pencere değerleri tek dosyada toplanmıştır.
Herkes kendi sorumluluk alanındaki başlangıç değerlerini buradan düzenler.
"""

from dataclasses import dataclass


# ==============================================================================
# 1. GÖZ AYARLARI (Işıl)
# ==============================================================================
@dataclass(frozen=True)
class GozAyar:
    # MediaPipe blendshape eyeBlink sol/sağ ortalaması bu eşiğin üstündeyse göz kapalı sayılır (0.0 - 1.0)
    GOZ_KAPALI_ESIK: float = 0.50

    # Kesintisiz göz kapalı kalma süresi (saniye) -> Güçlü işaret: 'uzun_kapanma'
    UZUN_KAPANMA_SURESI_SN: float = 1.50

    # PERCLOS hesaplama penceresi (saniye)
    PERCLOS_PENCERE_SN: float = 60.0

    # PERCLOS eşiği: Son penceredeki göz kapalı kalma oranı bu eşiği aşarsa -> Zayıf işaret: 'perclos_yuksek'
    PERCLOS_ESIK: float = 0.20


# ==============================================================================
# 2. AĞIZ VE ESNEME AYARLARI (Sena)
# ==============================================================================
@dataclass(frozen=True)
class AgizAyar:
    # MediaPipe blendshape jawOpen eşiği (0.0 - 1.0): Bu değerin üstü açık ağız sayılır
    ESNEME_JAW_OPEN_ESIK: float = 0.60

    # Esneme sayılabilmesi için ağzın kesintisiz açık kalması gereken minimum süre (sn)
    # Konuşma sırasında ağız kısa sürelerle açılıp kapandığı için konuşmayı esnemeden ayırır
    ESNEME_MIN_SURE_SN: float = 1.50

    # Esnemelerin takip edildiği zaman penceresi (dakika)
    ESNEME_PENCERE_DK: float = 3.0

    # Son N dakikada en az kaç esneme olursa işaret üretilir -> Zayıf işaret: 'sik_esneme'
    SIK_ESNEME_ESIK_ADET: int = 2


# ==============================================================================
# 3. BAŞ HAREKETİ VE AÇI AYARLARI (Casım)
# ==============================================================================
@dataclass(frozen=True)
class BasAyar:
    # Başın pitch (öne eğilme) açısı eşiği (derece)
    BAS_DUSMESI_ACI_ESIK_DERECE: float = 15.0

    # Başın öne düşme hızı eşiği (derece / saniye)
    BAS_DUSMESI_HIZ_ESIK: float = 10.0

    # Baş düşmesi sayılması için aynı anda gözlerin kapalı olması şartı (sn tolerans)
    BAS_GOZ_ESZAMANLI_PENCERE_SN: float = 0.50


# ==============================================================================
# 4. GÖRÜNÜRLÜK VE KALİTE AYARLARI (Behlül)
# ==============================================================================
@dataclass(frozen=True)
class GorunurlukAyar:
    # Yüzün bulunamadığı durumda 'belirsiz'e düşme tolerans süresi (sn)
    YUZ_YOK_TOLERANS_SN: float = 0.50

    # Ortalama parlaklık değeri bu eşiğin altındaysa görüntü karanlık sayılır (0 - 255)
    MIN_PARLAKLIK: float = 40.0

    # Başın aşırı dönük sayılacağı maksimum yaw/roll açısı (derece)
    MAX_YAW_ACI_DERECE: float = 45.0
    MAX_ROLL_ACI_DERECE: float = 45.0


# ==============================================================================
# 5. KARAR VE HİSTEREZİS AYARLARI (Işıl)
# ==============================================================================
@dataclass(frozen=True)
class KararAyar:
    # Bir durumdan diğerine geçerken ani dalgalanmayı önleyen histerezis süresi (sn)
    HISTEREZIS_YORGUN_SN: float = 2.0
    HISTEREZIS_UYANIK_SN: float = 3.0

    # Yüz kaybolduktan sonra önceki yorgun durumunu koruma süresi (sn)
    KAYIP_YUZ_HAFIZA_SURESI_SN: float = 2.0


# ==============================================================================
# 6. UYARI VE ÇIKTI AYARLARI (Sena)
# ==============================================================================
@dataclass(frozen=True)
class UyariAyar:
    # Aynı uyarının tekrar çalması için geçmesi gereken minimum bekleme süresi (cooldown) (sn)
    UYARI_BEKLEME_SURESI_SN: float = 10.0

    # JSON paneline log akıtma periyodu (saniye)
    JSON_LOG_PERIYOD_SN: float = 1.0

    # Uyarı ses dosyası yolu
    UYARI_SES_DOSYASI: str = "assets/alert.wav"


# ==============================================================================
# TEK ÇATI AYAR SINIFI VE ÖRNEĞİ
# ==============================================================================
@dataclass(frozen=True)
class Ayarlar:
    goz: GozAyar = GozAyar()
    agiz: AgizAyar = AgizAyar()
    bas: BasAyar = BasAyar()
    gorunurluk: GorunurlukAyar = GorunurlukAyar()
    karar: KararAyar = KararAyar()
    uyari: UyariAyar = UyariAyar()


# Kolay erişim için hazır nesneler
ayar = Ayarlar()
goz = ayar.goz
agiz = ayar.agiz
bas = ayar.bas
gorunurluk = ayar.gorunurluk
karar = ayar.karar
uyari = ayar.uyari

if __name__ == "__main__":
    print("Sistem ayarları başarıyla yüklendi:")
    print(f"  - Göz Kapalı Eşik: {goz.GOZ_KAPALI_ESIK}")
    print(f"  - Uzun Kapanma Süresi: {goz.UZUN_KAPANMA_SURESI_SN} sn")
    print(f"  - PERCLOS Eşik: {goz.PERCLOS_ESIK}")
    print(f"  - Esneme JawOpen Eşik: {agiz.ESNEME_JAW_OPEN_ESIK}")
    print(f"  - Sık Esneme Eşiği: {agiz.SIK_ESNEME_ESIK_ADET} adet / {agiz.ESNEME_PENCERE_DK} dk")
    print(f"  - Baş Düşmesi Açısı: {bas.BAS_DUSMESI_ACI_ESIK_DERECE}°")
    print(f"  - Uyarı Bekleme Süresi: {uyari.UYARI_BEKLEME_SURESI_SN} sn")
