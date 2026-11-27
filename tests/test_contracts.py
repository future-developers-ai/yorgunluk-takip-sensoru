"""Altı sahte dizinin ortak tiplere yüklenmesi ve parquet ile uyumu."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from contracts import Frame, FaceObs, Features, Isaret, Vote, Decision
from src.sozlesme import BLENDSHAPE_ADLARI, MATRIS_SUTUNLARI, SUTUNLAR, dogrula


SENARYOLAR = [
    "normal_operator", "uzun_goz_kapanmasi", "iki_esneme", "kitap_okuma",
    "bas_dusmesi_yuz_kaybi", "karanlik",
]


def yukle(ad):
    path = Path(__file__).parent / "fixtures" / f"{ad}.json"
    ham = json.loads(path.read_text(encoding="utf-8"))
    sonuc = []
    for kayit in ham["kayitlar"]:
        obs_veri = kayit["face_obs"].copy()
        if obs_veri["transformation_matrix"] is not None:
            obs_veri["transformation_matrix"] = np.array(obs_veri["transformation_matrix"])
        sonuc.append((Frame(**kayit["frame"]), FaceObs(**obs_veri),
                      Features(**kayit["features"]),
                      [Isaret(**x) for x in kayit["isaretler"]],
                      Vote(**kayit["vote"]) if kayit["vote"] else None,
                      Decision(**kayit["decision"])))
    return sonuc


@pytest.mark.parametrize("ad", SENARYOLAR)
def test_senaryo_tipleri_ve_parquet(ad):
    satirlar = []
    onceki = -1
    for frame, obs, feat, isaretler, vote, karar in yukle(ad):
        assert frame.t_s == obs.t_s == feat.t_s == karar.t_s
        assert frame.t_s > onceki
        onceki = frame.t_s
        assert obs.yuz_var == feat.yuz_var
        assert all(x.t_s == frame.t_s for x in isaretler)
        if vote is not None:
            assert vote.t_s == frame.t_s
        if obs.yuz_var:
            assert set(obs.blendshapes) == set(BLENDSHAPE_ADLARI)
            mat = obs.transformation_matrix.reshape(-1).tolist()
            skor = obs.blendshapes
        else:
            assert obs.blendshapes is None
            mat = [float("nan")] * 16
            skor = dict.fromkeys(BLENDSHAPE_ADLARI, float("nan"))
        satirlar.append({"t_s": obs.t_s, "yuz_var": obs.yuz_var, **skor,
                         **dict(zip(MATRIS_SUTUNLARI, mat)), "parlaklik": obs.parlaklik})
        cikti = json.loads(json.dumps(karar.json_kaydi(), allow_nan=False))
        assert set(cikti) == {"t_s", "durum", "neden", "uyari"}
        assert isinstance(cikti["neden"], str)
        assert isinstance(cikti["uyari"], bool)
    dogrula(pd.DataFrame(satirlar, columns=SUTUNLAR))


def test_senaryolar_zor_durumlari_icerir():
    assert all(not x[3] for x in yukle("normal_operator"))
    kitap = yukle("kitap_okuma")[-1]
    assert kitap[2].pitch_deg > 0 and kitap[2].goz_kapali_skor < 0.1
    assert not kitap[3]
    uzun = yukle("uzun_goz_kapanmasi")[2]
    assert uzun[2].kapali_sure_s == 1.6
    assert uzun[3][0].ad == "uzun_kapanma"
    esneme = yukle("iki_esneme")[-1]
    assert esneme[2].esneme_sayisi == 2 and esneme[3][0].ad == "sik_esneme"
    bas = yukle("bas_dusmesi_yuz_kaybi")
    assert bas[-2][3][0].ad == "bas_dusmesi"
    assert not bas[-1][1].yuz_var and bas[-1][5].durum == "yorgun"
    assert all(not x[3] and x[4].durum == "belirsiz" for x in yukle("karanlik"))


def test_tracker_faceobs_arayuzu_korunur():
    obs = FaceObs(timestamp_ms=200, yuz_var=True, eye_blink_left=0.85,
                  eye_blink_right=0.82, jaw_open=0.65,
                  transformation_matrix=np.eye(4), parlaklik=120.5)
    assert (obs.t_s, obs.eyeBlinkLeft, obs.eyeBlinkRight, obs.jawOpen) == (0.2, .85, .82, .65)
    bos = FaceObs(timestamp_ms=100, yuz_var=False)
    assert bos.blendshapes is None and bos.eyeBlinkLeft is None


@pytest.mark.parametrize("kurucu,alanlar", [
    (Isaret, dict(ad="uzun_kapanma", guc="zayif", t_s=0, neden="")),
    (Vote, dict(t_s=0, neden="", durum="yorgun")),
    (Decision, dict(t_s=0, durum="dikkat_dusuk", baslangic_s=0)),
    (Decision, dict(t_s=0, durum="uyanik", baslangic_s=1)),
    (Decision, dict(t_s=0, durum="uyanik", baslangic_s=0, uyari="ses")),
])
def test_gecersiz_isaret_oy_karar_reddedilir(kurucu, alanlar):
    with pytest.raises(ValueError):
        kurucu(**alanlar)
