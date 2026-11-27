# Fold1 veri hazırlığı

Kontrol tarihi: 27 Kasım 2026.

- Yerel veri dizini: `data/uta/Fold1/`.
- Kaynak arşivler: `Fold1_part1.zip` ve `Fold1_part2.zip`.
- Katılımcı sayısı: **12** (01–12).
- Video sayısı: **36**; kişi başına **3** video.
- Sınıflar: `0` (uyanık), `5` (hafif uykulu), `10` (uykulu).
- Fold1 geliştirme ve eşik ayarı için kullanılır.

| Katılımcı | Video sayısı | Sınıflar |
|---|---:|---|
| 01 | 3 | 0, 5, 10 |
| 02 | 3 | 0, 5, 10 |
| 03 | 3 | 0, 5, 10 |
| 04 | 3 | 0, 5, 10 |
| 05 | 3 | 0, 5, 10 |
| 06 | 3 | 0, 5, 10 |
| 07 | 3 | 0, 5, 10 |
| 08 | 3 | 0, 5, 10 |
| 09 | 3 | 0, 5, 10 |
| 10 | 3 | 0, 5, 10 |
| 11 | 3 | 0, 5, 10 |
| 12 | 3 | 0, 5, 10 |

## Kontroller

Hazırlık öncesinde D: sürücüsünde 65,4 GB boş alan vardı; 55 GB koşulu
sağlandı. Çıkarma sonrasında yaklaşık 40,7 GB boş alan kaldı.

Çıkarılan 36 videonun tamamı mevcut ve boş değildir. Dosya boyutları ZIP
kayıtlarıyla tek tek eşleşmektedir. Bu kontrol video çözme/oynatma veya
arşiv CRC doğrulaması değildir; görüntü yönü ve çıkarım kontrolü sonraki
Fold1 işleme görevinde yapılacaktır.

`main` dalında bulunan `.gitignore` içindeki `data/` kuralı bütün 36 videoyu
kapsamaktadır. `git check-ignore --stdin` ile doğrulandı. Video dosyaları
Git tarafından izlenmez; yalnızca bu veri notu repoya gönderilir.
