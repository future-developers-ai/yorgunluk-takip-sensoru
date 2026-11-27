"""
MediaPipe modülü ve FaceObs birim testleri (tests/test_tracker.py)
"""

import numpy as np
import pytest
from contracts import FaceObs
from capture.tracker import YuzAnalizci, varsayilan_model_yolu


def test_face_obs_defaults():
    """Yüz algılanmadığında alanların None olduğunu doğrular."""
    obs = FaceObs(timestamp_ms=100, yuz_var=False)
    assert obs.timestamp_ms == 100
    assert obs.yuz_var is False
    assert obs.blendshapes is None
    assert obs.eye_blink_left is None
    assert obs.eye_blink_right is None
    assert obs.jaw_open is None
    assert obs.eyeBlinkLeft is None
    assert obs.eyeBlinkRight is None
    assert obs.jawOpen is None
    assert obs.transformation_matrix is None
    assert obs.landmarks is None


def test_face_obs_with_blendshapes():
    """Blendshape değerlerinin ve camelCase getter'ların çalıştığını doğrular."""
    sample_blendshapes = {
        "eyeBlinkLeft": 0.85,
        "eyeBlinkRight": 0.82,
        "jawOpen": 0.65,
    }
    sample_matrix = np.eye(4, dtype=np.float32)

    obs = FaceObs(
        timestamp_ms=200,
        yuz_var=True,
        blendshapes=sample_blendshapes,
        eye_blink_left=0.85,
        eye_blink_right=0.82,
        jaw_open=0.65,
        transformation_matrix=sample_matrix,
        parlaklik=120.5,
    )

    assert obs.yuz_var is True
    assert obs.eyeBlinkLeft == 0.85
    assert obs.eyeBlinkRight == 0.82
    assert obs.jawOpen == 0.65
    assert obs.transformation_matrix.shape == (4, 4)
    assert obs.parlaklik == 120.5


def test_yuz_analizci_initialization():
    """YuzAnalizci nesnesinin hatasız başlatıldığını doğrular."""
    model_yolu = varsayilan_model_yolu()
    assert model_yolu.exists(), "Model dosyası bulunamadı."

    with YuzAnalizci(model_yolu=model_yolu) as analizci:
        assert analizci._kapandi is False


def test_yuz_analizci_blank_frame():
    """Siyah (boş) bir karede yüz bulunamadığında beklenen FaceObs çıktısını doğrular."""
    with YuzAnalizci() as analizci:
        blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        obs = analizci.analiz_et(blank_frame, timestamp_ms=50)

        assert isinstance(obs, FaceObs)
        assert obs.yuz_var is False
        assert obs.timestamp_ms == 50
        assert obs.blendshapes is None
        assert obs.eyeBlinkLeft is None
        assert obs.eyeBlinkRight is None
        assert obs.jawOpen is None
        assert obs.parlaklik == 0.0
