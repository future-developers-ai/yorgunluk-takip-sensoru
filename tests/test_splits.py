"""splits.yaml: gruplar çakışmaz."""

from scripts.check_splits import oku, sorunlar


def test_repodaki_gruplar_temiz():
    gruplar = oku()
    assert sorunlar(gruplar) == []
    assert {ad: len(k) for ad, k in gruplar.items()} == {"ayar": 24, "kontrol": 12, "test": 12}


def test_cakisma_yakalanir():
    assert sorunlar({"ayar": [1, 2], "kontrol": [2], "test": [3]}) == [
        "ayar ve kontrol ortak katılımcı: [2]"
    ]
