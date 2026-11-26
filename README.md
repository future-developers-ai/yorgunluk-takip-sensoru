# Operatör Yorgunluk ve Dikkat Analizi — Teknik Prototip

Sistem, webcam görüntüsünden operatörün durumunu dört sınıftan birine ayırır: `uyanik`, `dikkat_dusuk`, `yorgun`, `belirsiz`.

MediaPipe Face Landmarker yüzü bulur ve her kare için 478 yüz noktası, 52 blendshape skoru ve başın 4×4 dönüş matrisini verir. Ekip bu çıktılardan özellik hesaplar ve **kural tabanlı** karar verir. Sistem model eğitmez.

> Görev takibi ClickUp'ta yürütülür. Görevlerin güncel ve tek doğru metni ClickUp'tadır.
> Kod henüz yazılmamıştır. Aşağıdaki yapı ve komutlar hedeflenen durumu anlatır.

## Karar mantığı

Özellik modülleri yorgunluk hakkında karar vermez. Kurallar işaret (`Isaret`) üretir.

| İşaret | Güç | Tanım |
|---|---|---|
| `uzun_kapanma` | Güçlü | Göz eşik süreden uzun kesintisiz kapalı kalır |
| `perclos_yuksek` | Zayıf | Son pencerede PERCLOS eşik değeri aşar |
| `sik_esneme` | Zayıf | Son 60 saniyedeki esneme sayısı eşik değeri aşar |
| `bas_dusmesi` | Güçlü | Baş kısa sürede eşik açı kadar aşağı iner ve kısa sürede geri kalkar |

`yorgun` kararı yalnızca birleştirme modülünde verilir: son pencerede en az bir güçlü işaret ya da en az iki farklı zayıf işaret gerekir.

Karar sırası:

1. Yorgunluk kuralı sağlanıyorsa durum `yorgun` olur.
2. Yüz kaybolmuşsa ve kaybolmadan hemen önce bir yorgunluk işareti ya da baş düşmesi görülmüşse durum `yorgun` olarak kalır.
3. Yüz görünmüyorsa, görüntü karanlıksa ya da baş aşırı dönükse durum `belirsiz` olur.
4. `dikkat_dusuk` koşulu sağlanıyorsa durum `dikkat_dusuk` olur.
5. Hiçbiri sağlanmıyorsa durum `uyanik` olur.

Bütün eşik, süre ve pencere değerleri `config.toml` dosyasında durur.

## Veri

Veri seti [UTA-RLDD](https://sites.google.com/view/utarldd/home)'dir. Etiketler video başınadır: 0 (uyanık), 5 (düşük dikkatli), 10 (uykulu).

| Fold | Kullanım |
|---|---|
| Fold1, Fold2 | Eşik ayarı |
| Fold3 | Doğrulama |
| Fold4 | Test (6. güne kadar sonuçlarına bakılmaz) |
| Fold5 | Yedek |

**Video, yüz görüntüsü, işlenmiş veri ve kişi adı repoya girmez. Repo herkese açıktır.**

## Ölçütler

| Ölçüt | Hedef |
|---|---|
| Uyanık (0) videolarında 10 dakikadaki `yorgun` uyarısı | En fazla 1 |
| En az bir `yorgun` uyarısı çıkan uykulu (10) video oranı | En az %80 |
| Uykulu videosunda uyanık videosundan uzun `yorgun` süresi olan kişi oranı | En az %80 |
| Canlı webcam işlem hızı | En az 15 kare/sn |
| Uyarı gecikmesi (webcam demosu) | En fazla 2 saniye |

Düşük dikkatli (5) videolar ayrı raporlanır. `dikkat_dusuk` ve `belirsiz` için veri etiketi yoktur; bu durumlar sentetik testlerle ve webcam demosuyla doğrulanır.

## Roller

| Rol | Sinyal | Sistem parçası | Görevler |
|---|---|---|---|
| K1 | Göz | Birleştirme ve histerezis | T01–T10 |
| K2 | Ağız | Uyarı ve JSON çıktısı | T11–T20 |
| K3 | Baş | Canlı döngü ve kaynak okuma | T21–T30 |
| K4 | Yüz görünürlüğü | Toplu çalıştırıcı ve ölçüm | T31–T40 |

Review döngüsü: K1 → K2'nin, K2 → K3'ün, K3 → K4'ün, K4 → K1'in PR'larını inceler.

## Takvim (7 gün)

| Gün | İş | Günün sonunda |
|---|---|---|
| G1 | Altyapı ve veri | Sözleşme dondu, MediaPipe modülü çalışıyor, CI kuruldu, veri iniyor |
| G2 | Özellik ve veri işleme | Dört özellik modülü testli, dört fold işlendi, bölme sabit |
| G3 | Kural ve test | İşaret ve oy kuralları testli |
| G4 | Sistem ve test | Webcam'de canlı durum, uyarı ve JSON, tek komutla ölçüm |
| G5 | Eşik ayarı | Eşikler seçildi ve doğrulama grubunda kontrol edildi |
| G6 | Test, demo ve README | Eşikler donduruldu, test grubu bir kez çalıştırıldı, demo yapıldı |
| G7 | Kapanış ve tampon | Teknik not birleştirildi, geciken işler kapandı |

## Hedeflenen yapı

```
contracts.py        ortak veri tipleri
config.toml         bütün eşikler
yorgunluk/          ayar yükleyici
capture/            kare okuma ve MediaPipe
features/           göz, ağız, baş, görünürlük
rules/              işaretler, oylar, birleştirme
app/                canlı döngü, uyarı, JSON
scripts/            model indirme, çıkarım, toplu çalıştırma
eval/               ölçüm
tests/              birim ve uçtan uca testler
labels/             etiket dosyaları
docs/               veri notu, panel arayüzü, teknik not
data/               yerel veri (repoya girmez)
```

## Kurulum (hedef)

Python 3.12 ve webcam gerekir. `pyproject.toml` eklendikten sonra:

```bash
git clone https://github.com/raclab-ai-group/yorgunluk-takip-sensoru.git
cd yorgunluk-takip-sensoru
python -m venv .venv
pip install -e ".[dev]"
```

Branch ve review kuralları: [BRANCH-KURALLARI.txt](BRANCH-KURALLARI.txt)
