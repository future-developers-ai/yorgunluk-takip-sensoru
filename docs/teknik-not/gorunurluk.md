# Görünürlük ve `belirsiz`

Sistem göremediği durumda tahmin uydurmaz, `belirsiz` der.

## Ölçümler (`features/visibility.py`)

| Ölçüm | Tanım |
|---|---|
| `yuz_var` | MediaPipe o karede yüz buldu mu |
| `yuz_kayip_s` | İlk yüzsüz kareden bu yana kesintisiz geçen süre (saniye); yüz görününce sıfırlanır |
| `parlaklik` | Gri görüntünün ortalaması (0–255) |

## Kural (`rules/belirsiz.py`)

Aşağıdakilerden biri sağlanırsa `belirsiz` oyu üretilir. Eşikler `config.toml`
dosyasının `[visibility]` bölümündedir; tablodakiler henüz ayarlanmamış
başlangıç değerleridir.

| Neden | Koşul | Başlangıç değeri |
|---|---|---|
| `yuz_yok` | Yüz eşik süreden uzun kayıp | 1,0 sn |
| `karanlik` | Parlaklık eşiğin altında | 40 |
| `bas_asiri_donuk` | Kalibre yaw açısının mutlak değeri eşiği aşıyor | 60° |

Oy yorgunluk kararını ezmez; öncelik karar modülündedir.

## Video yönü

Telefonla çekilen videoların bir kısmı döndürme bilgisini dosya üstbilgisinde
taşır. OpenCV 4.11 bunu kendiliğinden uygulamaz; çıkarım betiği
`CAP_PROP_ORIENTATION_AUTO` ayarını açar. Fold4'te 36 videonun 16'sında bu
bilgi vardır (`labels/donus.csv`).

## Sınırlar

- Parlaklık tüm karenin ortalamasıdır. Arka plan aydınlık, yüz karanlıksa
  (ters ışık) `karanlik` oyu çıkmayabilir.
- Yaw eşiği, yaw açısını üreten kalibrasyon modülüne bağlıdır.
- Eşikler gerçek veride henüz ayarlanmamıştır; ölçülen bir sonuç yoktur.
