"""ArboIA — OCR local robusto, limitado e tolerante a falhas."""
from __future__ import annotations
import os, logging
from pathlib import Path
from typing import Any
import cv2
import numpy as np
try:
    import pytesseract
except ImportError:
    pytesseract = None
logger = logging.getLogger(__name__)
IDIOMAS_PADRAO = "por+eng"
OCR_TIMEOUT_SEGUNDOS = 7
OCR_REGIAO_TIMEOUT_SEGUNDOS = 1.5
MAX_DIMENSAO_IMAGEM = 1200
MAX_REGIOES = 8
MAX_CONTORNOS_ANALISADOS = 250
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
FERRAMENTAS = RAIZ_PROJETO / ".ferramentas"
BINARIO_LOCAL = FERRAMENTAS / "usr/bin/tesseract"
TESSDATA_LOCAL = FERRAMENTAS / "usr/share/tesseract-ocr/5/tessdata"
LIBS_LOCAIS = FERRAMENTAS / "usr/lib/x86_64-linux-gnu"

def configurar_tesseract() -> str | None:
    if pytesseract is None or not BINARIO_LOCAL.is_file(): return None
    pytesseract.pytesseract.tesseract_cmd = str(BINARIO_LOCAL)
    prefixo = os.environ.get("TESSDATA_PREFIX", "")
    if str(TESSDATA_LOCAL) not in prefixo:
        os.environ["TESSDATA_PREFIX"] = f"{TESSDATA_LOCAL}:{prefixo}" if prefixo else str(TESSDATA_LOCAL)
    libs = os.environ.get("LD_LIBRARY_PATH", "")
    if str(LIBS_LOCAIS) not in libs:
        os.environ["LD_LIBRARY_PATH"] = f"{LIBS_LOCAIS}:{libs}" if libs else str(LIBS_LOCAIS)
    return str(BINARIO_LOCAL)
TESSERACT_USADO = configurar_tesseract()

def carregar_imagem(caminho: str | os.PathLike[str]) -> np.ndarray:
    img = cv2.imread(str(caminho), cv2.IMREAD_COLOR)
    if img is None or img.size == 0: raise ValueError(f"Não foi possível abrir imagem: {caminho}")
    return img

def _normalizar(imagem: np.ndarray) -> np.ndarray:
    if not isinstance(imagem, np.ndarray) or imagem.size == 0: raise ValueError("Imagem vazia ou inválida")
    if imagem.dtype != np.uint8: imagem = np.clip(imagem, 0, 255).astype(np.uint8)
    if imagem.ndim == 2: imagem = cv2.cvtColor(imagem, cv2.COLOR_GRAY2BGR)
    elif imagem.ndim == 3 and imagem.shape[2] == 4: imagem = cv2.cvtColor(imagem, cv2.COLOR_BGRA2BGR)
    elif imagem.ndim != 3 or imagem.shape[2] != 3: raise ValueError("Formato de imagem não suportado")
    return imagem

def limitar_imagem(imagem: np.ndarray, escala_max: int = MAX_DIMENSAO_IMAGEM) -> np.ndarray:
    imagem = _normalizar(imagem); h, w = imagem.shape[:2]; maior = max(h, w)
    if maior > escala_max:
        fator = escala_max / maior
        imagem = cv2.resize(imagem, (max(1, int(w*fator)), max(1, int(h*fator))), interpolation=cv2.INTER_AREA)
    return imagem

def preprocessar(imagem: np.ndarray, escala_max: int = MAX_DIMENSAO_IMAGEM) -> np.ndarray:
    img = limitar_imagem(imagem, escala_max); gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    realcada = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(gray)
    thresh = cv2.adaptiveThreshold(realcada, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11)
    return cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, np.ones((2,2), np.uint8))

def _tesseract(img: np.ndarray, lang: str, config: str, timeout: float) -> str:
    if pytesseract is None: raise RuntimeError("pytesseract não instalado")
    return pytesseract.image_to_string(img, lang=lang, config=config, timeout=timeout).strip()

def extrair_texto(caminho: str | os.PathLike[str] | np.ndarray, idiomas: str = IDIOMAS_PADRAO) -> str:
    if pytesseract is None: raise RuntimeError("pytesseract indisponível")
    img = carregar_imagem(caminho) if isinstance(caminho, (str, os.PathLike)) else caminho
    processada = preprocessar(img)
    try: return _tesseract(processada, idiomas, "--psm 11", OCR_TIMEOUT_SEGUNDOS)
    except Exception as exc:
        if "timeout" in str(exc).lower() or "timed out" in str(exc).lower():
            raise RuntimeError(f"OCR excedeu {OCR_TIMEOUT_SEGUNDOS}s; seguir sem OCR") from exc
        if "por" in idiomas:
            try: return _tesseract(processada, "eng", "--psm 11", 3)
            except Exception as fallback: raise RuntimeError(f"OCR português/inglês falhou: {fallback}") from fallback
        raise RuntimeError(f"Tesseract falhou: {exc}") from exc

def detectar_regioes(caminho: str | os.PathLike[str] | np.ndarray, min_area_ratio: float = 0.004) -> list[dict[str, Any]]:
    img = carregar_imagem(caminho) if isinstance(caminho, (str, os.PathLike)) else caminho
    proc = preprocessar(img); h, w = proc.shape[:2]
    contours, _ = cv2.findContours(cv2.bitwise_not(proc), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:MAX_CONTORNOS_ANALISADOS]
    area_min, area_max = h*w*max(.001,min_area_ratio), h*w*.60; candidates=[]
    for c in contours:
        area=cv2.contourArea(c)
        if not area_min <= area <= area_max: continue
        x,y,rw,rh=cv2.boundingRect(c)
        if rw<60 or rh<40 or not .35<=rw/max(rh,1)<=4: continue
        candidates.append({"id":0,"x":int(x),"y":int(y),"largura":int(rw),"altura":int(rh),"area":int(area),"centro":{"x":int(x+rw/2),"y":int(y+rh/2)},"texto":""})
    def overlap(a,b):
        x1,y1=max(a["x"],b["x"]),max(a["y"],b["y"]); x2,y2=min(a["x"]+a["largura"],b["x"]+b["largura"]),min(a["y"]+a["altura"],b["y"]+b["altura"])
        inter=max(0,x2-x1)*max(0,y2-y1); union=a["largura"]*a["altura"]+b["largura"]*b["altura"]-inter
        return inter/union if union else 0
    unique=[]
    for r in sorted(candidates,key=lambda z:z["area"],reverse=True):
        if not any(overlap(r,u)>.75 for u in unique): unique.append(r)
        if len(unique)>=MAX_REGIOES: break
    unique.sort(key=lambda r:(r["centro"]["y"]//40,r["centro"]["x"]))
    for i,r in enumerate(unique,1):
        r["id"]=i
        if pytesseract is not None:
            roi=proc[r["y"]:r["y"]+r["altura"],r["x"]:r["x"]+r["largura"]]
            try: r["texto"]=_tesseract(roi,"eng","--psm 6",OCR_REGIAO_TIMEOUT_SEGUNDOS)
            except Exception: r["texto"]=""
    return unique

def relacoes_espaciais(regioes: list[dict[str,Any]], limiar_proximidade: int=220) -> list[dict[str,Any]]:
    rel=[]
    for i,a in enumerate(regioes):
        for b in regioes[i+1:]:
            dx=b["centro"]["x"]-a["centro"]["x"]; dy=b["centro"]["y"]-a["centro"]["y"]; dist=(dx*dx+dy*dy)**.5
            if dist>limiar_proximidade*2: continue
            if abs(dx)>abs(dy)*1.3: direction="à direita de" if dx>0 else "à esquerda de"
            elif abs(dy)>abs(dx)*1.3: direction="abaixo de" if dy>0 else "acima de"
            else: direction="em diagonal com"
            rel.append({"de":a["id"],"para":b["id"],"relacao":direction,"distancia":int(dist)})
    return rel

def interpretar_imagem(caminho: str) -> dict[str,Any]:
    result={"sucesso":False,"modo":"ocr-local","texto":"","regioes":[],"relacoes":[],"estimativa_fichas":0,"avisos":[]}
    try: img=carregar_imagem(caminho)
    except Exception as exc: result["avisos"].append(f"Imagem inválida: {exc}"); return result
    try: result["texto"]=extrair_texto(img)
    except Exception as exc: logger.warning("OCR falhou, continuando sem texto: %s",exc); result["avisos"].append(f"OCR falhou; análise pode continuar sem texto: {exc}")
    try:
        result["regioes"]=detectar_regioes(img); result["relacoes"]=relacoes_espaciais(result["regioes"]); result["estimativa_fichas"]=len(result["regioes"])
    except Exception as exc: logger.warning("Detecção de regiões falhou: %s",exc); result["avisos"].append(f"Detecção de regiões falhou: {exc}")
    result["sucesso"]=True
    return result
if __name__=="__main__":
    import json,sys
    if len(sys.argv)<2: print("Uso: python ia/ocr.py imagem.jpg"); raise SystemExit(1)
    print(json.dumps(interpretar_imagem(sys.argv[1]),ensure_ascii=False,indent=2))
