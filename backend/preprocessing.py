import os
import cv2
import numpy as np
from typing import Optional, Tuple


def read_image(image_path: str) -> np.ndarray:
    img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Unable to read image: {image_path}")
    return img


def save_image(image: np.ndarray, out_path: str) -> str:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    # Use imencode to support Windows paths with non-ASCII
    ext = os.path.splitext(out_path)[1] or '.png'
    ret, buf = cv2.imencode(ext, image)
    if not ret:
        raise RuntimeError("Failed to encode image for saving")
    with open(out_path, 'wb') as f:
        buf.tofile(f)
    return out_path


def to_grayscale(img: np.ndarray) -> np.ndarray:
    if len(img.shape) == 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


def denoise(img_gray: np.ndarray, h: int = 10) -> np.ndarray:
    # Fast Non-Local Means denoising for grayscale
    return cv2.fastNlMeansDenoising(img_gray, h=h)


def enhance_contrast(img_gray: np.ndarray, clip_limit: float = 3.0, tile_grid_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    return clahe.apply(img_gray)


def binarize(img_gray: np.ndarray, method: str = 'adaptive') -> np.ndarray:
    if method == 'adaptive':
        return cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 31, 10)
    elif method == 'otsu':
        _, th = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return th
    else:
        # simple
        _, th = cv2.threshold(img_gray, 150, 255, cv2.THRESH_BINARY)
        return th


def deskew(img_gray: np.ndarray, max_angle: float = 15.0) -> np.ndarray:
    # Invert for text as white
    th = binarize(img_gray, method='otsu')
    th = cv2.bitwise_not(th)

    coords = np.column_stack(np.where(th > 0))
    if coords.size == 0:
        return img_gray

    rect = cv2.minAreaRect(coords)
    angle = rect[-1]
    # Adjust angle as per OpenCV's convention
    if angle < -45:
        angle = 90 + angle
    # Constrain
    angle = np.clip(angle, -max_angle, max_angle)

    (h, w) = img_gray.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img_gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated


def preprocess_image(image_path: str,
                     do_deskew: bool = True,
                     do_denoise: bool = True,
                     use_adaptive: bool = True,
                     contrast: bool = True,
                     output_dir: Optional[str] = None) -> str:
    """
    Full preprocessing pipeline. Returns path to processed image file.
    """
    img = read_image(image_path)
    gray = to_grayscale(img)

    if do_deskew:
        gray = deskew(gray)

    if do_denoise:
        gray = denoise(gray, h=12)

    if contrast:
        gray = enhance_contrast(gray)

    th = binarize(gray, method='adaptive' if use_adaptive else 'otsu')

    # Save to temp/output path
    base = os.path.splitext(os.path.basename(image_path))[0]
    out_dir = output_dir or os.path.join(os.path.dirname(image_path), 'preprocessed')
    out_path = os.path.join(out_dir, f"{base}_preprocessed.png")
    return save_image(th, out_path)
