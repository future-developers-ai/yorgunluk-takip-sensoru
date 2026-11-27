# Veri sözleşmesi

Durum: ClickUp G1 “Sözleşme ve sahte veri (Sena ile)” görevine göre güncellenmiş,
ekip oturumunda onaya sunulacak taslak. En az iki kişinin onayı ve gerçek
parquet kontrolü henüz tamamlanmış sayılmaz. README ve etiketleme kılavuzunda
geçen eski `dikkat_dusuk` adı yerine `hafif_uykulu` kullanılır.

Görev: https://app.clickup.com/t/z8rzdgcbae

## Tek kaynak

Sütun ve durum adları elle tekrar yazılmaz; `src.sozlesme` modülünden alınır:

```python
import pandas as pd
from src.sozlesme import SUTUNLAR, dogrula

df = pd.read_parquet("F1_kisi03_10.parquet")
dogrula(df)
df.loc[:, SUTUNLAR].to_parquet("F1_kisi03_10.parquet", index=False)
```

## Dosyalar ve satırlar

- Ad biçimi: `F{fold}_kisi{katilimci:02d}_{sinif}.parquet`.
- Örnek: `F1_kisi03_10.parquet`, Fold1 / katılımcı 03 / sınıf 10 videosudur.
- `0`: uyanık; `5`: hafif uykulu; `10`: uykulu. Bunlar video etiketleridir;
  sistemin kare başına verdiği kararla aynı bilgi değildir.
- Bir satır, çıkarımda işlenen bir kaynak kareye aittir. Görüntü saklanmaz.
- ClickUp çıkarım görevinin kabul ölçütü: her kaynak kare için bir satır.
  Zaman kaynak videodan alınır; satır sayısından türetilmez. Yüz bulunmasa da
  işlenen karenin satırı korunur. Daha önce paylaşılan 15 kare/sn örnekleme
  planı bu ölçütten farklıdır; ekip açıkça değiştirmedikçe kare atlanmaz.
  Videoyu açma/okuma hataları çıkarım raporuna yazılır.
- Ham videolar, gerçek parquet ve kişi bilgileri Git'e eklenmez. Ortak klasörde
  Fold1–4 paylaşımı ClickUp veri rehberine göre yapılır. Fold3 kontrol, Fold4
  yalnızca final ölçümü içindir; geliştirme veya ayar için incelenmez.

## Parquet sütunları

Toplam 71 sütun vardır. Yazım sırası `SUTUNLAR` sabitidir; doğrulama girişte
sütun sırasına değil adlarına bakar. Fazla, eksik ve tekrarlanan sütun reddedilir.
DataFrame indeksi parquet'e yazılmaz.

| Sütun | Tip | Birim / kural |
|---|---|---|
| `t_s` | Sayısal | Videonun başlangıcından saniye; sonlu, ≥ 0, kesin artan; boş olamaz |
| `yuz_var` | Boolean | `True` / `False`; boş olamaz; tamsayı 0/1 kabul edilmez |
| `BLENDSHAPE_ADLARI` içindeki 52 ad | Sayısal | MediaPipe adları aynen korunur; yüz varken dolu ve 0–1 arasında |
| `m00` … `m33` | Sayısal | 4×4 dönüş matrisi satır sırasıyla: m00, m01, …, m33; yüz varken sonlu ve dolu |
| `parlaklik` | Sayısal | Gri görüntünün ortalama parlaklığı; 0–255; boş olamaz |

52 adın eksiksiz listesi `src/sozlesme.py` içindeki `BLENDSHAPE_ADLARI` sabitidir.
Matris değerlerine 0–1 sınırı uygulanmaz. Sayısal alanlarda boolean kabul edilmez.
Yüz bulunmayan satırda 52 skorun ve 16 matris değerinin tamamı `NaN`/null olur;
sıfırla doldurulmaz. Zaman ve parlaklık yine kaydedilir. Boş tablo reddedilir.

## Durumlar, işaretler ve uyarılar

| Sabit | Değerler |
|---|---|
| `DURUMLAR` | `uyanik`, `hafif_uykulu`, `yorgun`, `belirsiz` |
| `ISARETLER` | `uzun_kapanma`, `bas_dusmesi`, `perclos_yuksek`, `sik_esneme` |
| `UYARILAR` | `yok`, `yazi`, `ses` |

`UYARILAR` iç uyarı seviyeleridir; panel JSON'undaki `uyari` alanı boolean'dır.

Bir güçlü işaret veya iki farklı zayıf işaret `yorgun`; tek zayıf işaret
`hafif_uykulu` üretir. Görünürlük ve durum geçişleri karar modülünde işlenir.
Bu modül karar hesaplamaz ve eşik içermez. ClickUp'a göre eşikler
`config.toml` içinde, okuyucu `yorgunluk/config.py` içindedir (Sena'nın görevi).
Repodaki mevcut `src/ayar.py` eski/geçiş yapısıdır; bu sözleşme değişikliği
Sena'nın ayar geçişini gerçekleştirmez. Yeni eşik dosyası burada oluşturulmaz.

## Modüller arası veri tipleri

Tiplerin tek kaynağı kökteki `contracts.py` dosyasıdır. Sütun adlarının tek
kaynağı `src/sozlesme.py` olarak kalır; iki dosya birbirinin alternatifi değildir.

| Tip | Üreten → kullanan | Alanlar / birimler |
|---|---|---|
| `Frame` | kaynak → yüz modülü | `t_s` saniye; `goruntu` OpenCV BGR uint8 (sahte veride None) |
| `FaceObs` | yüz modülü → özellikler | `timestamp_ms` milisaniye; `t_s` saniyeye dönüşen özellik; yüz varlığı, 0–1 skorlar, 4×4 matris, 0–255 parlaklık |
| `Features` | özellikler → kurallar | `t_s`; `yuz_var`; göz skoru/PERCLOS 0–1; kapanma saniye; ağız skoru 0–1; esneme adedi; pitch/yaw derece; parlaklık 0–255 |
| `Isaret` | göz, esneme, baş → karar | `ad`, `guc` (`guclu`/`zayif`), `t_s` saniye, `neden` metin |
| `Vote` | yalnızca belirsiz kuralı → karar | `t_s` saniye, `neden` metin, `durum=belirsiz` |
| `Decision` | karar → uyarı/panel | `t_s`, `durum`, `baslangic_s` saniye, `neden` metin, `uyari` boolean |

`Vote` ve `Decision` taslakları Sena ile birlikte gözden geçirilir; eklenmeleri
Sena'nın onay verdiği anlamına gelmez. Bütün alanların birimleri kodda yorumdur.
Pitch öne eğilirken pozitif, yaw sağa dönerken pozitiftir; matristen açı üreten
modül bu işaret yönlerine dönüşümü yapmalıdır. Ölçülemeyen özellik `None` kalır.

Mevcut `capture/tracker.py` uyumluluğu için `FaceObs.timestamp_ms` ve camelCase
erişimleri korunur. Parquet'e yazarken zaman `obs.t_s`, skorlar
`obs.blendshapes`, matris satır sırasıyla `m00…m33` olur. Yüz yokken skor ve
matris `None` değerleri parquet satırında sayısal null'a dönüştürülür.

## Altı sahte dizi

`tests/fixtures/` içinde gerçek kişi veya görüntü içermeyen altı JSON vardır:

1. `normal_operator.json`: açık göz, nötr baş, işaret yok.
2. `uzun_goz_kapanmasi.json`: kapanma ve tekrar açılma.
3. `iki_esneme.json`: üç dakika içinde iki ayrı esneme.
4. `kitap_okuma.json`: baş eğik, göz açık; baş düşmesi işareti yok.
5. `bas_dusmesi_yuz_kaybi.json`: göz kapanmasıyla baş düşmesi, ardından yüz kaybı.
6. `karanlik.json`: düşük parlaklık, göz/baş işareti yerine belirsiz oyu.

Her dizi zaman sıralı `frame`, `face_obs`, `features`, `isaretler`, `vote` ve
`decision` kayıtları içerir. Test bunları ilgili dataclass'lara yükler. İşaret,
ölçüm ve kararlar elle hazırlanmış beklenen örneklerdir; henüz yazılmayan kural
modüllerinin çalıştırılması veya eşik ayarı sonucu değildir. Gerçek testler
sonradan bu girdileri modüllere verip beklenen sonuçlarla karşılaştırmalıdır.

## JSON satır biçimi

Her kayıt UTF-8 JSON Lines biçiminde tek satırdır. Önerilen ortak çıktı:

```json
{"t_s":12.4,"durum":"yorgun","neden":"goz_kapali_1.6s","uyari":true}
```

| Alan | Tip | Anlam |
|---|---|---|
| `t_s` | Sayı | Kaynak başlangıcından geçen saniye |
| `durum` | Metin | `DURUMLAR` listesinden bir değer |
| `neden` | Metin | Etkin gerekçe; yoksa boş metin; birden fazlaysa `;` ile birleştirilir |
| `uyari` | Boolean | O kayıtta yeni uyarı üretildi mi? `true` / `false` |

Uyarı bekleme süresi nedeniyle yorgun durumundaki her kayıt ses üretmek zorunda
değildir. `dogrula()` yalnızca parquet tablosunu denetler; JSON doğrulamaz.
Kayıt her durum değişiminde ve saniyede bir kez yazılır (Sena'nın çıktı görevi).
`hafif_uykulu` yazı; `yorgun` yazı ve ses üretir. `Decision.json_kaydi()` yalnızca
kayıt alanlarını verir; uyarıyı tetiklemez veya kayıt sıklığını uygulamaz.
JSON alanları ve eksik veri kuralları oturumda Sena, Casım ve Behlül ile onaylanır.

## Kabul ve son kontrol

1. Ekip 52 adın MediaPipe çıktısıyla eşleşmesini, matris sırasını, eksik veri,
   örnekleme ve JSON kurallarını oturumda onaylar.
2. Değişiklik ayrı branch ve PR ile gönderilir; en az iki kişinin onayı alınır.
   main'e doğrudan gönderilmez. Altı sahte dizi tiplerine hatasız yüklenmelidir.
3. Behlül'ün bir gerçek videodan çıkardığı parquet `dogrula()` kontrolünden geçer.
4. Kontrol edilen dosyanın adı, komut ve sonuç PR'a yazılır; veri Git'e eklenmez.

Başarılı doğrulama `None` döndürür ve tabloyu değiştirmez. Uygunsuz veri
`ValueError`, DataFrame dışındaki girdi `TypeError` üretir. Kontroller
`python -O` ile de çalışır. Sentetik testin geçmesi gerçek parquet kontrolü
ve ekip onayı yerine geçmez.
