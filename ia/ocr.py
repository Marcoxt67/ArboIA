"""
ARboIA — Módulo de leitura de imagem (OCR local)

Pipeline:
    imagem -> pré-processamento (OpenCV) -> extração de texto (Tesseract)
           -> detecção de regiões retangulares (fichas) -> relações espaciais

Funciona offline. Se Tesseract não estiver instalado, retorna erro amigável.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import cv2
import numpy as np

try:
    import pytesseract
    from PIL import Image
except ImportError:  # pragma: no cover
    pytesseract = None
    Image = None


IDIOMAS_PADRAO = "por+eng"

# --------------------------------------------------------------------------- #
# Tesseract local (instalado sem sudo em .ferramentas/)
# --------------------------------------------------------------------------- #

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
FERRAMENTAS = RAIZ_PROJETO / ".ferramentas"
BINARIO_LOCAL = FERRAMENTAS / "usr/bin/tesseract"
TESSDATA_LOCAL = FERRAMENTAS / "usr/share/tesseract-ocr/5/tessdata"
LIBS_LOCAIS = FERRAMENTAS / "usr/lib/x86_64-linux-gnu"


def configurar_tesseract() -> str | None:
    """
    Detecta o Tesseract baixado localmente e configura pytesseract,
    TESSDATA_PREFIX e LD_LIBRARY_PATH antes de qualquer chamada.

    Retorna o caminho do binário usado, ou None se usar o binário do sistema.
    """
    if pytesseract is None or not BINARIO_LOCAL.exists():
        return None

    pytesseract.pytesseract.tesseract_cmd = str(BINARIO_LOCAL)

    prefixo = os.environ.get("TESSDATA_PREFIX", "")
    if str(TESSDATA_LOCAL) not in prefixo:
        os.environ["TESSDATA_PREFIX"] = (
            f"{TESSDATA_LOCAL}:{prefixo}" if prefixo else str(TESSDATA_LOCAL)
        )

    bibliotecas = os.environ.get("LD_LIBRARY_PATH", "")
    if str(LIBS_LOCAIS) not in bibliotecas:
        os.environ["LD_LIBRARY_PATH"] = (
            f"{LIBS_LOCAIS}:{bibliotecas}" if bibliotecas else str(LIBS_LOCAIS)
        )

    return str(BINARIO_LOCAL)


TESSERACT_USADO = configurar_tesseract()


# --------------------------------------------------------------------------- #
# Pré-processamento
# --------------------------------------------------------------------------- #

def carregar_imagem(caminho: str) -> np.ndarray:
    """Carrega imagem de arquivo. Levanta ValueError se inválida."""
    imagem = cv2.imread(caminho)
    if imagem is None:
        raise ValueError(f"Não foi possível abrir a imagem: {caminho}")
    return imagem


def preprocessar(imagem: np.ndarray, escala_max: int = 1600) -> np.ndarray:
    """
    Melhora a legibilidade para OCR:
      1. redimensiona mantendo proporção;
      2. escala de cinza;
      3. equalização de histograma (CLAHE);
      4. limiarização adaptativa;
      5. fechamento morfológico leve.
    """
    altura, largura = imagem.shape[:2]
    if max(altura, largura) > escala_max:
        fator = escala_max / max(altura, largura)
        imagem = cv2.resize(imagem, None, fx=fator, fy=fator,
                            interpolation=cv2.INTER_AREA)

    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    realcada = clahe.apply(cinza)
    limiar = cv2.adaptiveThreshold(
        realcada, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 11
    )
    kernel = np.ones((2, 2), np.uint8)
    return cv2.morphologyEx(limiar, cv2.MORPH_CLOSE, kernel)


# --------------------------------------------------------------------------- #
# Extração de texto
# --------------------------------------------------------------------------- #

def extrair_texto(caminho: str | np.ndarray,
                  idiomas: str = IDIOMAS_PADRAO) -> str:
    """Extrai texto da imagem com Tesseract."""
    if pytesseract is None:
        raise RuntimeError(
            "pytesseract ou Pillow não instalados. "
            "Execute: pip install pytesseract pillow"
        )

    imagem = (carregar_imagem(caminho) if isinstance(caminho, str)
              else caminho)
    processada = preprocessar(imagem)

    try:
        texto = pytesseract.image_to_string(processada, lang=idiomas,
                                            config="--psm 11")
    except pytesseract.TesseractError as exc:
        if "por" in idiomas:
            # Fallback: alguns sistemas não têm o pacote de português.
            texto = pytesseract.image_to_string(processada, lang="eng",
                                                config="--psm 11")
        else:
            raise RuntimeError(
                f"Tesseract falhou: {exc}. "
                "Instale os idiomas: apt install tesseract-ocr-por"
            ) from exc

    return texto.strip()


# --------------------------------------------------------------------------- #
# Detecção de fichas e relações espaciais
# --------------------------------------------------------------------------- #

def detectar_regioes(caminho: str | np.ndarray,
                     min_area_ratio: float = 0.004) -> list[dict[str, Any]]:
    """
    Detecta retângulos prováveis (fichas) na imagem.

    Retorna lista de dicts com: id, x, y, largura, altura, area, centro,
    texto_regiao.
    """
    imagem = (carregar_imagem(caminho) if isinstance(caminho, str)
              else caminho)
    processada = preprocessar(imagem)
    altura, largura = processada.shape[:2]

    # O limiar adaptativo deixa o fundo escuro e as bordas claras;
    # invertemos para que as fichas virem regiões claras sobre fundo escuro.
    invertida = cv2.bitwise_not(processada)
    contornos, _ = cv2.findContours(invertida, cv2.RETR_LIST,
                                    cv2.CHAIN_APPROX_SIMPLE)

    area_min = altura * largura * min_area_ratio
    area_max = altura * largura * 0.60
    regioes: list[dict[str, Any]] = []

    for contorno in contornos:
        area = cv2.contourArea(contorno)
        if not (area_min <= area <= area_max):
            continue

        x, y, w, h = cv2.boundingRect(contorno)
        if w < 60 or h < 40:
            continue

        razao = w / h
        if not (0.35 <= razao <= 4.0):
            continue

        regiao = processada[y:y + h, x:x + w]
        texto = ""
        if pytesseract is not None:
            try:
                texto = pytesseract.image_to_string(
                    regiao, lang=IDIOMAS_PADRAO, config="--psm 6"
                ).strip()
            except Exception:
                texto = ""

        regioes.append({
            "id": len(regioes) + 1,
            "x": int(x), "y": int(y),
            "largura": int(w), "altura": int(h),
            "area": int(area),
            "centro": {"x": int(x + w / 2), "y": int(y + h / 2)},
            "texto": texto,
        })

    # Remove duplicados (contorno interno e externo da mesma borda).
    def sobreposicao(a: dict[str, Any], b: dict[str, Any]) -> float:
        x1 = max(a["x"], b["x"])
        y1 = max(a["y"], b["y"])
        x2 = min(a["x"] + a["largura"], b["x"] + b["largura"])
        y2 = min(a["y"] + a["altura"], b["y"] + b["altura"])
        intersecao = max(0, x2 - x1) * max(0, y2 - y1)
        uniao = (a["largura"] * a["altura"]
                 + b["largura"] * b["altura"] - intersecao)
        return intersecao / uniao if uniao else 0.0

    unicas: list[dict[str, Any]] = []
    for regiao in sorted(regioes, key=lambda r: r["area"], reverse=True):
        if any(sobreposicao(regiao, u) > 0.75 for u in unicas):
            continue
        unicas.append(regiao)

    # Ordena da esquerda para a direita, depois de cima para baixo.
    unicas.sort(key=lambda r: (r["centro"]["y"] // 40, r["centro"]["x"]))
    for indice, regiao in enumerate(unicas, start=1):
        regiao["id"] = indice
    return unicas


def relacoes_espaciais(regioes: list[dict[str, Any]],
                       limiar_proximidade: int = 220) -> list[dict[str, str]]:
    """Infere relações espaciais simples entre fichas vizinhas."""
    relacoes: list[dict[str, str]] = []
    for i, a in enumerate(regioes):
        for b in regioes[i + 1:]:
            dx = b["centro"]["x"] - a["centro"]["x"]
            dy = b["centro"]["y"] - a["centro"]["y"]
            distancia = (dx ** 2 + dy ** 2) ** 0.5
            if distancia > limiar_proximidade * 2:
                continue

            if abs(dx) > abs(dy) * 1.3:
                direcao = "à direita de" if dx > 0 else "à esquerda de"
            elif abs(dy) > abs(dx) * 1.3:
                direcao = "abaixo de" if dy > 0 else "acima de"
            else:
                direcao = "em diagonal com"

            relacoes.append({
                "de": a["id"], "para": b["id"],
                "relacao": direcao,
                "distancia": int(distancia),
            })
    return relacoes


# --------------------------------------------------------------------------- #
# API principal
# --------------------------------------------------------------------------- #

def interpretar_imagem(caminho: str) -> dict[str, Any]:
    """
    Interpreta uma imagem de fichas e retorna dados estruturados.

    Saída:
        {
          "sucesso": bool,
          "modo": "ocr-local",
          "texto": str,
          "regioes": [...],
          "relacoes": [...],
          "estimativa_fichas": int,
          "avisos": [...]
        }
    """
    resultado: dict[str, Any] = {
        "sucesso": False,
        "modo": "ocr-local",
        "texto": "",
        "regioes": [],
        "relacoes": [],
        "estimativa_fichas": 0,
        "avisos": [],
    }

    try:
        imagem = carregar_imagem(caminho)
    except ValueError as exc:
        resultado["avisos"].append(str(exc))
        return resultado

    try:
        resultado["texto"] = extrair_texto(imagem)
    except (RuntimeError, Exception) as exc:  # noqa: BLE001
        resultado["avisos"].append(f"OCR indisponível: {exc}")

    try:
        resultado["regioes"] = detectar_regioes(imagem)
        resultado["relacoes"] = relacoes_espaciais(resultado["regioes"])
        resultado["estimativa_fichas"] = len(resultado["regioes"])
    except Exception as exc:  # noqa: BLE001
        resultado["avisos"].append(f"Detecção de regiões falhou: {exc}")

    resultado["sucesso"] = bool(
        resultado["texto"].strip() or resultado["estimativa_fichas"] > 0
    )
    return resultado


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Uso: python ia/ocr.py caminho/da/imagem.jpg")
        raise SystemExit(1)
    print(json.dumps(interpretar_imagem(sys.argv[1]),
                     ensure_ascii=False, indent=2))
