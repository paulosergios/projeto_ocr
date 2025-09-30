# app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF
import numpy as np
import pytesseract
from pytesseract import Output
from .preprocess import preprocess_bgr

app = FastAPI(title="OCR Mini", version="0.2.0")

@app.get("/health")
def health():
    return {"status": "ok"}

def best_tesseract_result(img_bin: np.ndarray, lang: str = "por+eng"):
    """
    Testa alguns PSMs (layout modes) do Tesseract e retorna o melhor
    por média de confiança. psm 4=coluna, 6=bloco, 11=sparse.
    """
    best = {"text": "", "conf": -1.0, "psm": None}
    for psm in (4, 6, 11):
        cfg = f"--oem 3 --psm {psm}"
        data = pytesseract.image_to_data(img_bin, lang=lang, config=cfg, output_type=Output.DICT)
        confs = []
        for c in data.get("conf", []):
            try:
                v = float(c)
                if v >= 0:
                    confs.append(v)
            except:
                pass
        avg = float(np.mean(confs)) if confs else -1.0
        txt = pytesseract.image_to_string(img_bin, lang=lang, config=cfg)
        if avg > best["conf"]:
            best = {"text": txt, "conf": avg, "psm": psm}
    return best

@app.post("/ocr/pdf")
async def ocr_pdf(file: UploadFile = File(...), lang: str = "por+eng", max_chars: int = 5000):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Envie um arquivo .pdf")

    pdf_bytes = await file.read()
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception:
        raise HTTPException(status_code=400, detail="PDF inválido ou corrompido.")

    pages_out = []
    # ~300 DPI (72 é o baseline do PDF)
    zoom = 500 / 72.0
    mat = fitz.Matrix(zoom, zoom)

    for i, page in enumerate(doc):
        # (opcional) se o PDF tiver texto embutido, usa direto:
        plain = page.get_text("text").strip()
        if plain:
            pages_out.append({
                "page": i + 1,
                "word_count": len(plain.split()),
                "avg_confidence": None,   # não se aplica quando é texto nativo
                "text": plain[:max_chars]
            })
            continue

        # Renderiza a página como imagem e faz OCR
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)

        # Pré-processamento (CLAHE + Otsu, ver preprocess.py atualizado)
        pre = preprocess_bgr(img)

        # Testa PSMs e pega o melhor
        res = best_tesseract_result(pre, lang=lang)
        pages_out.append({
            "page": i + 1,
            "word_count": len(res["text"].split()),
            "avg_confidence": None if res["conf"] < 0 else round(res["conf"], 2),
            "text": res["text"][:max_chars],
            "psm": res["psm"]  # útil para debug; remova se quiser manter a resposta minimalista
        })

    return JSONResponse({"filename": file.filename, "pages": pages_out, "lang": lang})