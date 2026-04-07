import io
import numpy as np
from PIL import Image
import cv2

_hog = cv2.HOGDescriptor()
_hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
_face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
_profile_face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_profileface.xml"
)
_upperbody_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_upperbody.xml"
)


def _detect_primary_person_bbox(rgb_array: np.ndarray):
    bgr = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
    rects, _ = _hog.detectMultiScale(
        bgr,
        winStride=(8, 8),
        padding=(8, 8),
        scale=1.05,
    )

    if len(rects) == 0:
        return None

    return max(rects, key=lambda r: r[2] * r[3])


def _classify_from_person_bbox(rgb_array: np.ndarray, person_bbox) -> str | None:
    bgr = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    x, y, w, h = person_bbox
    if w <= 0 or h <= 0:
        return None

    h_img, w_img = rgb_array.shape[:2]
    area_ratio = (w * h) / float(max(1, w_img * h_img))
    aspect_ratio = w / float(h)
    body_region = gray[max(0, y):min(h_img, y + h), max(0, x):min(w_img, x + w)]
    if body_region.size == 0:
        return None

    # 상반신(약 45%)에서 얼굴을 찾고, 얼굴 대비 몸통 폭을 체형 지표로 사용
    upper_h = max(1, int(body_region.shape[0] * 0.45))
    upper_region = body_region[:upper_h, :]
    faces = _face_cascade.detectMultiScale(
        upper_region,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(20, 20),
    )

    head_ratio = None
    if len(faces) > 0:
        fx, fy, fw, fh = max(faces, key=lambda r: r[2] * r[3])
        if fw > 0:
            head_ratio = fw / float(w)

    # 얼굴 대비 몸통 폭 + 인물 박스 비율 기반 규칙
    # 마른 체형은 오탐이 매우 잦아서 조건을 훨씬 엄격하게 둡니다.
    if head_ratio is not None:
        if head_ratio <= 0.27 and aspect_ratio >= 0.42:
            return "근육질 (Muscular)"
        if head_ratio <= 0.24 and area_ratio >= 0.16:
            return "건장한 체형 (Endomorph)"
        if (
            head_ratio >= 0.40
            and aspect_ratio <= 0.33
            and 0.08 <= area_ratio <= 0.22
        ):
            return "마른 체형 (Ectomorph)"

    if aspect_ratio >= 0.56 and area_ratio >= 0.20:
        return "건장한 체형 (Endomorph)"
    if aspect_ratio >= 0.46 and area_ratio >= 0.12:
        return "근육질 (Muscular)"
    # 얼굴 검출이 안 된 경우에는 마른 체형으로 단정하지 않음
    if aspect_ratio <= 0.32 and area_ratio >= 0.10:
        return "표준 체형 (Mesomorph)"
    return "표준 체형 (Mesomorph)"


def _has_face_presence(rgb_array: np.ndarray) -> bool:
    bgr = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    # 1) 정면 얼굴
    faces = _face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.05,
        minNeighbors=3,
        minSize=(22, 22),
    )
    if len(faces) > 0:
        return True

    # 2) 측면 얼굴 (정면이 안 잡히는 경우 보완)
    prof = _profile_face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.05,
        minNeighbors=3,
        minSize=(22, 22),
    )
    if len(prof) > 0:
        return True

    # 3) 상반신 (앉은 사진/전신 미포함 케이스 보완)
    upper = _upperbody_cascade.detectMultiScale(
        gray,
        scaleFactor=1.05,
        minNeighbors=3,
        minSize=(60, 60),
    )
    return len(upper) > 0


def _fallback_classify(rgb_array: np.ndarray) -> str:
    # 인물 검출 실패 시 사용할 보조 휴리스틱(마른 체형 편향 완화)
    gray = np.mean(rgb_array, axis=2)
    mean_val = float(np.mean(gray))
    std_val = float(np.std(gray))
    contrast_score = std_val / (mean_val + 1e-5)

    if mean_val < 95 and contrast_score > 0.62:
        return "근육질 (Muscular)"
    # 밝기 기반으로는 마른 체형 판정하지 않아 오탐을 줄임
    if mean_val > 150 and contrast_score >= 0.48:
        return "건장한 체형 (Endomorph)"
    return "표준 체형 (Mesomorph)"

def analyze_body_type(image_bytes: bytes) -> str:
    """
    이미지 바이트를 입력받아 가벼운 모델로 체형을 분석하는 가상의 함수입니다.
    실제 MLOps 파이프라인 구축 시 이 부분을 실제 모델(예: PyTorch/TensorFlow/Mediapipe) 
    추론 코드로 교체하시면 됩니다.
    """
    try:
        # 1. 이미지 로드 및 전처리
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert("RGB")
        image = image.resize((512, 512))
        img_array = np.array(image)

        # 2. 인물 검출
        person_bbox = _detect_primary_person_bbox(img_array)
        if person_bbox is None and not _has_face_presence(img_array):
            raise ValueError("사람이 감지되지 않았습니다. 인물이 더 크고 선명하게 보이는 사진으로 다시 업로드해 주세요.")

        # 3. 인물 검출 박스 기반 체형 분류
        if person_bbox is not None:
            body_type = _classify_from_person_bbox(img_array, person_bbox)
        else:
            body_type = None

        if body_type is not None:
            return body_type

        # 4. 분류 실패 시 보조 휴리스틱 분류
        return _fallback_classify(img_array)
            
    except Exception as e:
        raise ValueError(f"이미지 처리 중 오류 발생: {e}")

def recommend_martial_arts(body_type: str) -> dict:
    """
    체형을 기반으로 격투기를 추천하는 로직입니다.
    """
    recommendations = {
        "근육질 (Muscular)": {
            "martial_art": "레슬링 / 종합격투기(MMA)",
            "reason": "강한 근력과 파워를 살릴 수 있는 그래플링 및 타격이 결합된 종목이 유리합니다."
        },
        "마른 체형 (Ectomorph)": {
            "martial_art": "무에타이 / 태권도",
            "reason": "긴 리치와 가벼운 체중을 활용한 타격 위주의 종목이 적합합니다."
        },
        "표준 체형 (Mesomorph)": {
            "martial_art": "복싱 / 유도",
            "reason": "민첩성과 힘의 밸런스가 좋아 타격기나 메치기에 모두 적합합니다."
        },
        "건장한 체형 (Endomorph)": {
            "martial_art": "주짓수 / 씨름",
            "reason": "체중을 활용하여 상대를 압박하고 방어 및 굳히기에 능한 그래플링 종목에 유리합니다."
        }
    }
    
    return recommendations.get(body_type, {
        "martial_art": "추천 결과를 찾을 수 없음",
        "reason": "체형 데이터가 명확하지 않습니다."
    })
