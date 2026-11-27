# Yorgunluk ve Dikkat Takip Sensörü: Repo ve Teknik Araştırması

Kaynak: Tavily aramaları (2026-11-23) ve GitHub API'sinden alınan lisans ve tarih bilgisi.
Not: Repoların içine girip kodlarını çalıştırmadım, bu yüzden "çalışıyor" garantisi yok.

## Kullanabileceğimiz repolar

| Repo | Ne işe yarar | Lisans / durum |
|---|---|---|
| **e-candeloro/Driver-State-Detection** | MediaPipe ve OpenCV ile webcam üzerinden EAR, PERCLOS, göz bakışı ve baş pozu. En olgun aday (159 yıldız). | MIT, son güncelleme 2026-08 |
| **google-ai-edge/mediapipe** | Face Landmarker: 478 nokta ve blendshape çıktıları. Temel bileşen. | Apache-2.0, aktif |
| **Mohammad-Umar7/drowsy-driver-detection** | Sıfırdan eğitilmiş göz açık/kapalı CNN ve yüz geometrisi. Model görevi için iskelet olabilir. | MIT, yeni ama 0 yıldız |
| **lyrics00/drowsiness-detection** | MediaPipe FaceMesh ile EAR ve geometrik ipuçları için başlangıç şablonu. | MIT, 1 yıldız |
| **tpatzelt/drowsiness-detection** | Göz takibi sinyallerinden LSTM ile uykululuk tespiti. | MIT, küçük proje |
| **iice257/driver-monitor** | `eyeBlink*` ve `jawOpen` blendshape'lerini EAR'a yedek ve esneme tespiti için kullanıyor. | Lisans kontrol edilmedi |
| **Vicomtech/DMD-Driver-Monitoring-Dataset** | DMD veri seti için araçlar ve etiket dönüştürücüler. | Akademik kullanım |

Yıldız sayıları düşük olduğu için çoğu doğrudan bağımlılık olarak değil, referans olarak uygun. Sağlam taban: MediaPipe ve Driver-State-Detection.

## Teknikler

- **PERCLOS:** Belirli bir pencerede gözlerin çoğunlukla kapalı olduğu sürenin yüzdesi. Pencere ve eşik parametre olarak alınabilir.
- **EAR ve MAR:** Göz ve ağız açıklık oranları. EAR göz kapanmasını, MAR esnemeyi yakalar. Bir arXiv çalışması sabit eşik yerine kişiye göre eşik öneriyor.
- **Blendshape yedeği:** MediaPipe'ın `eyeBlinkLeft/Right` ve `jawOpen` skorları baş pozu değişse de daha dayanıklı. Esneme için kısa süreli konuşmayı ayırt etme mantığı da var.
- **Zaman modeli:** Kare başına özellikleri (EAR, MAR, PERCLOS, baş pozu) CNN-LSTM veya 3D-CNN ile diziye çevirmek. Küçük veride önce eşik ve özellik tabanlı yaklaşım yeterli olabilir.
- **Baş pozu:** `solvePnP` ile pitch, yaw ve roll. Baş düşmesi için ek sinyal.

## Veri setleri

- **DMD:** Erişim için başvuru gerekiyor. 18 yaş üstü, yalnızca akademik ve ticari olmayan kullanım. Başvuru erken başlamalı.
- **DROZY:** İmzalı lisans sözleşmesiyle ORBi üzerinden iniyor. 14 kişilik küçük set, EEG ve yakın kızılötesi video içeriyor.
- **CEW:** 2.423 açık/kapalı göz fotoğrafı. Yorgunluk etiketi yok, yalnızca göz durumu. Göz sınıflandırıcısı için uygun.
- **NTHU-DDD:** Yorgunluk, baş, göz ve ağız durumu etiketleri var. Kaynaklarda en çok kullanılan genel set. Lisansı doğrulanmadı.
- **UL-DD:** Video, IR ve biyometrik sinyaller içeren, Zenodo'da yayımlanmış çok kipli set. KSS etiketli, uzman çapraz kontrolü var.

## Etiketleme ve ayırma notları

- Standart yöntem: eğitim, doğrulama ve test setlerinde kişiler ayrık olmalı (kimlik sızıntısını önler).
- UL-DD, KSS etiketlerini uzmanın videoların %30'unu bağımsız etiketlemesiyle doğrulamış. "Etiketle ve çapraz kontrol et" görevi için örnek.
- Literatürde KSS 1-5 "uyanık", 6-9 "uykulu" sayılmış. Bizim dört sınıfa (uyanık, dikkat düşük, yorgun, belirsiz) eşlemek için başlangıç olabilir.

## Önerilen sonraki adım

1. Driver-State-Detection'ı klonlayıp webcam demosunu ve çıktısını denemek.
2. DMD başvurusunu başlatmak.
3. Seçilen repoyu derinlemesine incelemek.
