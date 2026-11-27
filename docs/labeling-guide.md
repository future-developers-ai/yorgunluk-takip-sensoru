# Etiketleme Kılavuzu

Ekip kare kare elle etiketleme yapmaz. UTA-RLDD'nin video başına tek olan etiketi kullanılır.

| Sınıf | Anlamı |
|---|---|
| 0 | Uyanık |
| 5 | Düşük dikkatli (hafif uykululuk). Projedeki `dikkat_dusuk` durumuyla aynı şey değildir. |
| 10 | Uykulu |

## Etiket dosyası

Her fold için `labels/<fold_adı>.csv` dosyası yazılır. Sütunlar: `katilimci`, `video`, `sinif` (0, 5, 10), `sure_sn`, `fps`.

Yan duran videolar ve döndürme açıları `labels/donus.csv` dosyasına yazılır.

## Kurallar

1. `dikkat_dusuk` ve `belirsiz` için veri etiketi yoktur; bu durumlar sentetik testlerle ve webcam demosuyla doğrulanır.
2. Kalibrasyon aynı katılımcının uyanık (0) videosundan alınır.
3. Bir katılımcı yalnızca bir grupta (ayar, doğrulama, test) yer alır.
4. Video, yüz görüntüsü ve kişi adı repoya girmez.
