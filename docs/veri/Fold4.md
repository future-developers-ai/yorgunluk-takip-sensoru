# Fold4 veri notu (final test verisi)

Kontrol tarihi: 27 Kasım 2026.

- Yerel veri dizini: `data/uta/Fold4/` (başka bir diske dizin bağlantısı).
- Kaynak arşivler: `Fold4_part1.zip` ve `Fold4_part2.zip`.
- Katılımcı sayısı: **12** (37–48).
- Video sayısı: **36**; kişi başına **3** video.
- Sınıflar: `0` (uyanık), `5` (hafif uykulu), `10` (uykulu).
- Dosya uzantıları (büyük/küçük harf ayrımsız): `.mp4` 19, `.mov` 15, `.m4v` 2.

## Kontroller

36 videonun tamamı açıldı. Dosya boyutları ZIP kayıtlarıyla tek tek eşleşiyor.
Bu kontrol video çözme ya da arşiv CRC doğrulaması değildir; görüntü yönü ve
çıkarım kontrolü Fold4 işleme görevinde yapılacak.

Video dosyaları `.gitignore` içindeki `data/` kuralıyla Git dışındadır.

## Kural

Fold4 final test verisidir. Videoların ve çıkarım sonuçlarının içine, son gün
testine kadar bakılmaz.

## Yön kontrolü

Çıkarımdan önce video yönü sayısal olarak denetlendi: her videodan birkaç karede
yüzün bulunup bulunmadığı ve başın yatıklık açısı ölçüldü. Görüntüler açılıp
izlenmedi, eşik seçilmedi. 16 videoda döndürme bilgisi uygulanmadığı için yüz
yan ya da ters geliyordu; çıkarım betiği düzeltildikten sonra 36 videonun
tamamı dik.
