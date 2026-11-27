"""scripts/extract.py adlandırma ve satır üretimi testleri (model gerektirmez)."""

import numpy as np
import pandas as pd
import pytest

from contracts import FaceObs
from scripts.extract import cikti_adi, satir
from src.sozlesme import BLENDSHAPE_ADLARI, MATRIS_SUTUNLARI, SUTUNLAR, dogrula


@pytest.mark.parametrize(
    ("yol", "beklenen"),
    [
        ("data/uta/Fold4/37/0.mov", "F4_kisi37_0.parquet"),
        ("veri/Fold1_part1/01/10.MOV", "F1_kisi01_10.parquet"),
    ],
)
def test_cikti_adi(tmp_path, yol, beklenen):
    assert cikti_adi(tmp_path / yol) == beklenen


def test_cikti_adi_bilinmeyen_etiket(tmp_path):
    with pytest.raises(ValueError):
        cikti_adi(tmp_path / "Fold1/01/deneme.mp4")


def test_satirlar_sozlesmeye_uyar():
    matris = np.arange(16, dtype=np.float32).reshape(4, 4)
    yuzlu = FaceObs(
        yuz_var=True,
        blendshapes=dict.fromkeys(BLENDSHAPE_ADLARI, 0.5),
        transformation_matrix=matris,
        parlaklik=100.0,
    )
    yuzsuz = FaceObs(timestamp_ms=33, yuz_var=False, parlaklik=0.0)
    df = pd.DataFrame([satir(yuzlu, 0.0), satir(yuzsuz, 0.033)], columns=SUTUNLAR)
    df = df.astype({"yuz_var": bool})

    dogrula(df)
    assert df.loc[0, "m01"] == 1 and df.loc[0, "m10"] == 4  # satır sırası
    assert df.loc[1, BLENDSHAPE_ADLARI + MATRIS_SUTUNLARI].isna().all()
