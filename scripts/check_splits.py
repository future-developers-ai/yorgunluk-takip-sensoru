"""Hiçbir katılımcının iki grupta birden olmadığını denetler.

Kullanım:
    python scripts/check_splits.py
"""

import json
import sys
from itertools import combinations
from pathlib import Path

SPLITS = Path(__file__).resolve().parent.parent / "splits.yaml"
GRUPLAR = ("ayar", "kontrol", "test")


def oku(yol: Path = SPLITS) -> dict[str, list[int]]:
    """splits.yaml'ın tek satırlık `ad: [1, 2]` biçimini okur (ek bağımlılık yok)."""
    gruplar = {}
    for satir in Path(yol).read_text(encoding="utf-8").splitlines():
        satir = satir.strip()
        if satir and not satir.startswith("#"):
            ad, _, liste = satir.partition(":")
            gruplar[ad] = json.loads(liste)
    return gruplar


def sorunlar(gruplar: dict[str, list[int]]) -> list[str]:
    if set(gruplar) != set(GRUPLAR):
        return [f"Gruplar {GRUPLAR} olmalı, bulunan: {sorted(gruplar)}"]
    sonuc = [f"{ad} içinde tekrar var" for ad, k in gruplar.items() if len(k) != len(set(k))]
    for a, b in combinations(GRUPLAR, 2):
        ortak = sorted(set(gruplar[a]) & set(gruplar[b]))
        if ortak:
            sonuc.append(f"{a} ve {b} ortak katılımcı: {ortak}")
    return sonuc


def main() -> int:
    bulunan = sorunlar(oku())
    print("\n".join(bulunan) or "Katılımcı çakışması yok.")
    return 1 if bulunan else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
