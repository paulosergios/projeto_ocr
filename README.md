# OCR Mini (PDF → Texto) · FastAPI + OpenCV + Tesseract

Pequeno serviço de OCR: recebe **PDF**, renderiza as páginas, faz **pré-processamento** com OpenCV e roda **Tesseract**. Exposto via **FastAPI**.

---

## Funcionalidades

- **Endpoint** `POST /ocr/pdf`: upload de PDF e retorno de texto por página (+ contagem de palavras, confiança média).
- **Pré-processamento**: conversão para tons de cinza, CLAHE para contraste, blur leve e **binarização Otsu** (bom ponto de partida para scans). :contentReference[oaicite:0]{index=0}
- **Tesseract** com varredura de **PSM** (4, 6, 11) e escolha do melhor por confiança média. **Fallback** para texto nativo do PDF quando existente (qualidade superior). Renderização em **alta resolução** (≈500 DPI). :contentReference[oaicite:1]{index=1}
- **Endpoint** `GET /health` para verificação simples.
- **Swagger/OpenAPI** em `/docs`.

---

## Estrutura

ocr_mini/
├─ app/
│ ├─ main.py # FastAPI + OCR por página
│ └─ preprocess.py # pipeline de pré-processamento
├─ requirements.txt
├─ Dockerfile
├─ README.md
└─ tests/
    ├─ sample1.pdf # baixa resolução
    └─ sample2.pdf # boa resolução

## OBS:. Por se apenas um pequeno projeto sem os devidos aperfeiçoamentos, a acurácia do primiero exemplo é baixa (algo próximo dos 15-20%), já o segundo exemplo, de melhor resolução, apresenta acurácia acima de 80%

yaml
Copiar código

---

## 🐳 Rodando com Docker (recomendado)

> Requisitos: Docker instalado e em execução.

### Build
```bash
docker build -t ocr_mini .
```

### Run

## Windows PowerShell

```bash
docker run --rm -p 8000:8000 -v "${PWD}\tests:/tests" ocr_mini
```

## Windows CMD

```bash
docker run --rm -p 8000:8000 -v %CD%\tests:/tests ocr_mini
```
## Git Bash / WSL / Linux / macOS

```bash
docker run --rm -p 8000:8000 -v "$PWD/tests:/tests" ocr_mini
```