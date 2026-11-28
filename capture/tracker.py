"""
MediaPipe Face Landmarker Takip Modülü (capture/tracker.py)

Sorumlu: Casım Tugay (k3-baş)
Birlikte çalışılan: Behlül Anik (k4-görünürlük)

Video akışından her kare için yüz tespiti, 52 blendshape skoru ve
4x4 baş dönüş matrisini (transformation matrix) çıkaran MediaPipe sarmalayıcısı.
"""

import os
import urllib.request
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# contracts.py üzerinden FaceObs tanımı
try:
    from contracts import FaceObs
except ImportError:
    from ..contracts import FaceObs

DEFAULT_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/1/face_landmarker.task"
)


def varsayilan_model_yolu() -> Path:
    """Proje kökündeki models/face_landmarker.task yolunu döndürür."""
    repo_root = Path(__file__).resolve().parent.parent
    return repo_root / "models" / "face_landmarker.task"


def model_kontrol_ve_indir(model_yolu: Optional[Path] = None) -> Path:
    """Model dosyası mevcut değilse otomatik olarak indirir."""
    if model_yolu is None:
        model_yolu = varsayilan_model_yolu()

    model_yolu = Path(model_yolu)
    if not model_yolu.exists():
        model_yolu.parent.mkdir(parents=True, exist_ok=True)
        print(f"MediaPipe Face Landmarker modeli indiriliyor -> {model_yolu} ...")
        urllib.request.urlretrieve(DEFAULT_MODEL_URL, str(model_yolu))
        print("Model başarıyla indirildi.")

    return model_yolu


class YuzAnalizci:
    """MediaPipe Face Landmarker video modunda çalışan ortak yüz analiz sınıfı.

    Özellikler:
    - RunningMode.VIDEO modunda kare kare zaman damgasıyla çalışır.
    - 52 blendshape skorunu ve 4x4 yüz dönüş matrisini çıkarır.
    - Yüz bulunamadığında alanları None olan FaceObs döndürür.
    """

    def __init__(
        self,
        model_yolu: Optional[str | Path] = None,
        num_faces: int = 1,
        min_face_detection_confidence: float = 0.5,
        min_face_presence_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        model_path_obj = model_kontrol_ve_indir(Path(model_yolu) if model_yolu else None)

        base_options = python.BaseOptions(model_asset_path=str(model_path_obj))
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_faces=num_faces,
            min_face_detection_confidence=min_face_detection_confidence,
            min_face_presence_confidence=min_face_presence_confidence,
            min_tracking_confidence=min_tracking_confidence,
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True,
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)
        self._kapandi = False

    def analiz_et(self, frame_bgr: np.ndarray, timestamp_ms: int) -> FaceObs:
        """Bir video karesini analiz eder ve FaceObs nesnesi döndürür.

        Args:
            frame_bgr: OpenCV BGR formatında uint8 görüntü (H, W, 3).
            timestamp_ms: Karenin milisaniye cinsinden artan zaman damgası.

        Returns:
            FaceObs nesnesi. Yüz bulunamazsa alanlar None, yuz_var=False olur.
        """
        if self._kapandi:
            raise RuntimeError("YuzAnalizci kapatıldıktan sonra çağrılamaz.")

        # Parlaklık hesabı (gri ton ortalaması)
        if frame_bgr.ndim == 3:
            gri = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        else:
            gri = frame_bgr
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_GRAY2RGB)

        parlaklik = float(np.mean(gri))

        # MediaPipe Görüntü Nesnesi
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        sonuc = self.detector.detect_for_video(mp_image, int(timestamp_ms))

        # Yüz tespit edilemediyse
        if not sonuc.face_landmarks:
            return FaceObs(
                timestamp_ms=timestamp_ms,
                yuz_var=False,
                parlaklik=parlaklik,
            )

        # 52 Blendshape sözlüğü
        blendshape_dict: Dict[str, float] = {}
        if sonuc.face_blendshapes and len(sonuc.face_blendshapes) > 0:
            for item in sonuc.face_blendshapes[0]:
                blendshape_dict[item.category_name] = float(item.score)

        eye_blink_left = blendshape_dict.get("eyeBlinkLeft")
        eye_blink_right = blendshape_dict.get("eyeBlinkRight")
        jaw_open = blendshape_dict.get("jawOpen")

        # 4x4 Dönüş matrisi (Facial Transformation Matrix)
        transform_mat: Optional[np.ndarray] = None
        if (
            sonuc.facial_transformation_matrixes
            and len(sonuc.facial_transformation_matrixes) > 0
        ):
            transform_mat = np.array(
                sonuc.facial_transformation_matrixes[0], dtype=np.float32
            )

        # 478 Yüz Landmark koordinatları (x, y, z)
        landmarks: Optional[np.ndarray] = None
        if sonuc.face_landmarks and len(sonuc.face_landmarks) > 0:
            landmarks = np.array(
                [[lm.x, lm.y, lm.z] for lm in sonuc.face_landmarks[0]],
                dtype=np.float32,
            )

        return FaceObs(
            timestamp_ms=timestamp_ms,
            yuz_var=True,
            blendshapes=blendshape_dict,
            eye_blink_left=eye_blink_left,
            eye_blink_right=eye_blink_right,
            jaw_open=jaw_open,
            transformation_matrix=transform_mat,
            landmarks=landmarks,
            parlaklik=parlaklik,
        )

    # Kolaylık için alternatif metod isimleri
    process_frame = analiz_et
    detect = analiz_et

    def close(self) -> None:
        """MediaPipe kaynaklarını serbest bırakır."""
        if not self._kapandi:
            self.detector.close()
            self._kapandi = True

    def __enter__(self) -> "YuzAnalizci":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
