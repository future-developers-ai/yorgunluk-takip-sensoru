# Veri sözleşmesi

Durum: ekip oturumunda onaya sunulacak taslak. Bu belge son görev planındaki
`src/` yapısını ve `hafif_uykulu` durum adını esas alır. README ve etiketleme
kılavuzunda geçen eski `dikkat_dusuk` adı bu sözleşmede kullanılmaz.

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
- Hedef hız `src/ayar.py` içindeki `AYAR.islem_fps` (başlangıçta 15) değeridir.
  Daha düşük hızlı kaynaklarda kare çoğaltılmaz. Zaman kaynak videodan alınır;
  satır sayısından türetilmez. Yüz bulunmasa da işlenen karenin satırı korunur.
- Satır sayısı işlenen kare sayısıdır; yüksek hızlı kaynağın toplam kare sayısı
  olmak zorunda değildir. Videoyu açma/okuma hataları çıkarım raporuna yazılır.
- Ham videolar, gerçek parquet ve kişi bilgileri Git'e eklenmez. Ortak klasörde
  F1, F2, F3 paylaşılır; F4 bu klasöre konmaz.

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

Bir güçlü işaret veya iki farklı zayıf işaret `yorgun`; tek zayıf işaret
`hafif_uykulu` üretir. Görünürlük ve durum geçişleri karar modülünde işlenir.
Bu modül karar hesaplamaz ve eşik içermez; eşikler `src/ayar.py` içindedir.

## JSON satır biçimi

Her kayıt UTF-8 JSON Lines biçiminde tek satırdır. Önerilen ortak çıktı:

```json
{"t_s":12.4,"durum":"yorgun","neden":["uzun_kapanma"],"uyari":"ses"}
```

| Alan | Tip | Anlam |
|---|---|---|
| `t_s` | Sayı | Kaynak başlangıcından geçen saniye |
| `durum` | Metin | `DURUMLAR` listesinden bir değer |
| `neden` | Metin listesi | Etkin gerekçeler; gerekçe yoksa `[]`; görünürlük gerekçeleri de yazılabilir |
| `uyari` | Metin | O kayıtta üretilen uyarı: `yok`, `yazi`, `ses`; `ses`, yazı ve sesi birlikte ifade eder |

Uyarı bekleme süresi nedeniyle yorgun durumundaki her kayıt ses üretmek zorunda
değildir. `dogrula()` yalnızca parquet tablosunu denetler; JSON doğrulamaz.
JSON alanları ve eksik veri kuralları oturumda Sena, Casım ve Behlül ile onaylanır.

## Kabul ve son kontrol

1. Ekip 52 adın MediaPipe çıktısıyla eşleşmesini, matris sırasını, eksik veri,
   örnekleme ve JSON kurallarını oturumda onaylar.
2. Değişiklik ayrı branch ve PR ile gönderilir; main'e doğrudan gönderilmez.
3. Behlül'ün bir gerçek videodan çıkardığı parquet `dogrula()` kontrolünden geçer.
4. Kontrol edilen dosyanın adı, komut ve sonuç PR'a yazılır; veri Git'e eklenmez.

Başarılı doğrulama `None` döndürür ve tabloyu değiştirmez. Uygunsuz veri
`ValueError`, DataFrame dışındaki girdi `TypeError` üretir. Kontroller
`python -O` ile de çalışır. Sentetik testin geçmesi gerçek parquet kontrolü
ve ekip onayı yerine geçmez.
