import cv2
import numpy as np

def to_gray(img_bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

def denoise(gray: np.ndarray) -> np.ndarray:
    # leve — suficiente para demo
    return cv2.GaussianBlur(gray, (3, 3), 0)

def binarize(gray: np.ndarray) -> np.ndarray:
    # funciona bem em scans variados
    return cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
        31, 2
    )

def preprocess_bgr(img_bgr: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # contraste local ajuda muito em scans
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # suavização leve
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    # binarização: teste rápido com Otsu (muitas vezes melhor que o adaptive em recibos)
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th
