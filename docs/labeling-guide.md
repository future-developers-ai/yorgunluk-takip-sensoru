# Etiketleme Kılavuzu

## PERCLOS Standardı
PERCLOS = Gözlerin %80+ kapalı olduğu sürenin toplam süreye oranı.

## Etiket Kategorileri
| Etiket | Kriter |
|--------|--------|
| awake | PERCLOS < %20, dik baş, normal bakış |
| drowsy | PERCLOS %20–%50, yavaş göz kırpma, hafif baş eğimi |
| fatigue | PERCLOS > %50, uzun göz kapama, belirgin baş düşmesi |
| uncertain | Görüntü kalitesi yetersiz, yüz kısmen kapalı |

## Araçlar
- CVAT: https://cvat.ai
- LabelImg alternatif

## Kurallar
1. Her kare yalnızca bir etiket alır
2. Şüpheli durumlarda uncertain kullan
3. 10 kareden fazla yüz görünmüyorsa o bölümü atla