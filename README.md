# 🧠 Operatör Yorgunluk & Dikkat Takip Sensörü

> Kamera görüntüsünden operatörün dikkat ve yorgunluk durumunu gerçek zamanlı analiz eden bilgisayarlı görü sistemi.

---

## 🎯 Proje Amacı

Fabrika, kontrol odası veya araç gibi kritik ortamlarda görev yapan operatörlerin **yorgunluk ve dikkat düşüklüğünü** kameradan otomatik olarak tespit etmek. Sistem, operatörün yüz ve göz hareketlerini analiz ederek HMI (İnsan-Makine Arayüzü) üzerinden uyarı verir.

---

## 👥 Ekip & Görev Dağılımı

| Kişi | Rol | Sorumluluk |
|------|-----|------------|
| Veri Mühendisi 1 | Veri Bulma | Açık veri setleri araştırma, veri toplama planı |
| Veri Mühendisi 2 | Etiketleme | Görüntü etiketleme, kalite kontrolü |
| Görüntü İşleme Müh. | Kamera & Bellek | Kamera optimizasyonu, gerçek zamanlı pipeline |
| ML Mühendisi | Model Eğitimi | Model geliştirme, değerlendirme, teslim |

> Detaylı görev takibi ClickUp üzerinden yürütülmektedir.

---

## 🗂️ Proje Yapısı

```
hmi-operator-fatigue-detection/
│
├── data/
│   ├── raw/              # Ham veri setleri
│   ├── labeled/          # Etiketlenmiş veriler
│   └── splits/           # Train / val / test ayrımı
│
├── camera/
│   ├── capture.py        # Kamera yakalama modülü
│   ├── preprocess.py     # Görüntü ön işleme
│   └── optimize.py       # Bellek & hız optimizasyonu
│
├── model/
│   ├── train.py          # Model eğitimi
│   ├── evaluate.py       # Değerlendirme
│   └── export.py         # Model dışa aktarma
│
├── hmi/
│   ├── alert.py          # Uyarı mantığı
│   └── output.py         # HMI çıktı sözleşmesi
│
└── docs/
    └── labeling-guide.md # Etiketleme kılavuzu
```

---

## 📊 Tespit Edilecek Durumlar

| Durum | Belirtiler |
|-------|-----------|
| 🟢 Uyanık | Normal göz açıklığı, dik baş pozisyonu |
| 🟡 Dikkat Düşük | Sık göz kırpma, yavaş tepki |
| 🔴 Yorgun | Kısık gözler, baş eğimi, uzun göz kapama |

---

## 🗃️ Veri Kaynakları (Araştırılacak)

- **NTHU-DDD** — Sürücü uyuşukluk veri seti
- **UTA-RLDD** — Gerçek zamanlı yorgunluk tespiti
- **CEW Dataset** — Kapalı/açık göz veri seti
- Özel kayıt — Proje ortamına özgü veriler

---

## ⏱️ Takvim

| Aşama | Tarih |
|-------|-------|
| Veri toplama & etiketleme | — |
| Kamera pipeline | — |
| Model eğitimi | — |
| Kabul & teslim | — |

---

## 🛠️ Teknoloji Yığını

- **Görüntü işleme:** OpenCV
- **Model:** PyTorch / ONNX
- **Etiketleme:** CVAT / LabelImg
- **Takip:** ClickUp

---

## 🚀 Kurulum

```bash
git clone https://github.com/Bhllcoder1/hmi-operator-fatigue-detection.git
cd hmi-operator-fatigue-detection
pip install -r requirements.txt
```
