"""
ARboIA — Integração opcional com IA multimodal

Suporta:
  - OpenAI padrão (sk-...);
  - provedores compatíveis com a API OpenAI via OPENAI_BASE_URL;
  - Coarena (coa_...), detectada automaticamente em https://coarena.ai/api/v1.

Lê a chave de OPENAI_API_KEY (ou ARBOIA_API_KEY / COARENA_API_KEY) do
ambiente/.env. Se a chave não existir ou a chamada falhar, retorna `None`
e o sistema usa o modo local (OCR + regras) automaticamente.

NUNCA coloque a chave diretamente neste arquivo.
"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
from typing import Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # pragma: no cover
    pass


MODELO_PADRAO = "gpt-4o-mini"
BASE_COARENA = "https://coarena.ai/api/v1"
MODELOS_COARENA_PREFERIDOS = [
    "gemini-3-8-flash",
    "gpt-6-2-astra",
    "gemini-4-argon",
    "gpt-6-luna",
]

PROMPT_SISTEMA = """Você é o ARboIA, um assistente pedagógico brasileiro que apoia
estudantes do ensino médio em um jogo sobre os 9 limites planetários.

Sua função NÃO é dar a resposta correta. Sua função é interpretar uma foto de
fichas dispostas na mesa e devolver uma análise que estimule a reflexão.

As fichas são de três tipos:
- AZUL: limite planetário (ex.: Mudança climática, Biodiversidade funcional,
  Extinção biótica, Ciclo do nitrogênio, Ciclo do fósforo, Uso do solo,
  Água doce, Acidificação dos oceanos, Aerossóis atmosféricos)
- LARANJA: problemática socioambiental
- VERDE: intervenção proposta

Identifique os 9 limites planetários no modelo de Steffen et al. (2015).

Responda EXATAMENTE em JSON válido, sem markdown e sem explicações extras,
com esta estrutura:
{
  "sucesso": true,
  "modo": "multimodal",
  "limites": [
    {"id": "clima", "codigo": "L1", "nome": "Mudança climática",
     "pontuacao": 0.9, "central": true}
  ],
  "problematicas": [
    {"codigo": "P1.1", "texto": "texto lido ou parafraseado",
     "limite_id": "clima", "pontuacao": 0.8}
  ],
  "intervencoes": [
    {"codigo": "I1.1", "texto": "texto lido ou parafraseado",
     "limite_id": "clima", "afeta": ["clima", "fosforo"], "pontuacao": 0.8}
  ],
  "sinergias": [{"texto": "Uma ação ajuda dois limites ao mesmo tempo.", "forca": 2}],
  "tradeoffs": [{"texto": "Efeito colateral identificado.", "forca": 2}],
  "observacoes": "Breve descrição do que você viu na imagem."
}

IDs possíveis: clima, biodiversidade, extincao, nitrogenio, fosforo,
uso_solo, agua, oceanos, aerossois.

Se não conseguir ler nada, responda: {"sucesso": false, "modo": "multimodal",
"observacoes": "motivo"}.
"""


# --------------------------------------------------------------------------- #
# Configuração
# --------------------------------------------------------------------------- #

def obter_configuracao() -> tuple[str | None, str | None, str]:
    """Retorna (chave, base_url, modelo) a partir do ambiente."""
    chave = (
        os.getenv("OPENAI_API_KEY")
        or os.getenv("ARBOIA_API_KEY")
        or os.getenv("COARENA_API_KEY")
        or ""
    ).strip()

    if not chave or chave.upper().startswith("SK-PROJ-COLOQUE") or chave.upper().startswith("COA_COLOQUE"):
        return None, None, MODELO_PADRAO

    base = (
        os.getenv("OPENAI_BASE_URL")
        or os.getenv("ARBOIA_BASE_URL")
        or (BASE_COARENA if chave.startswith("coa_") else None)
    )
    modelo = os.getenv("OPENAI_MODEL") or (
        MODELOS_COARENA_PREFERIDOS[0] if chave.startswith("coa_") else MODELO_PADRAO
    )
    return chave, base, modelo


def chave_disponivel() -> bool:
    """Verifica se há chave configurada e se a biblioteca está instalada."""
    chave, _, _ = obter_configuracao()
    if not chave:
        return False
    try:
        import openai  # noqa: F401
    except ImportError:
        return False
    return True


# --------------------------------------------------------------------------- #
# Imagem e parsing
# --------------------------------------------------------------------------- #

def _codificar_imagem(caminho: str) -> tuple[str, str]:
    """Codifica imagem em base64 e infere o MIME."""
    with open(caminho, "rb") as arquivo:
        dados = arquivo.read()
    mime, _ = mimetypes.guess_type(caminho)
    if not mime or not mime.startswith("image/"):
        mime = "image/jpeg"
    return base64.b64encode(dados).decode("utf-8"), mime


def _extrair_json(conteudo: str) -> dict[str, Any] | None:
    """Extrai JSON de uma resposta que pode vir com markdown ou texto ao redor."""
    conteudo = conteudo.strip()

    bloco = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", conteudo, re.DOTALL)
    candidatos = [bloco.group(1)] if bloco else []

    inicio = conteudo.find("{")
    fim = conteudo.rfind("}")
    if inicio != -1 and fim > inicio:
        candidatos.append(conteudo[inicio:fim + 1])

    for candidato in candidatos:
        try:
            dados = json.loads(candidato)
            if isinstance(dados, dict):
                return dados
        except json.JSONDecodeError:
            continue
    return None


# --------------------------------------------------------------------------- #
# API principal
# --------------------------------------------------------------------------- #

def analisar_imagem(caminho: str, modelo: str | None = None) -> dict[str, Any] | None:
    """
    Tenta analisar a imagem com um modelo multimodal.

    Retorna dict estruturado em caso de sucesso, ou `None` se:
      - não houver chave;
      - biblioteca não instalada;
      - chamada falhar (rede, cota, formato).
    """
    if not chave_disponivel():
        return None

    from openai import OpenAI

    chave, base, modelo_config = obter_configuracao()
    cliente = (OpenAI(base_url=base, api_key=chave) if base
               else OpenAI(api_key=chave))

    modelo = modelo or modelo_config
    imagem_base64, mime = _codificar_imagem(caminho)

    modelos_tentados: list[str] = []
    for tentativa in range(2):
        try:
            resposta = cliente.chat.completions.create(
                model=modelo,
                messages=[
                    {"role": "system", "content": PROMPT_SISTEMA},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Analise esta foto das fichas montadas pelos "
                                    "estudantes e devolva o JSON pedido."
                                ),
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime};base64,{imagem_base64}",
                                    "detail": "high",
                                },
                            },
                        ],
                    },
                ],
                temperature=0.2,
                max_tokens=1400,
            )
            conteudo = resposta.choices[0].message.content or ""
            dados = _extrair_json(conteudo)
            if dados is None:
                print("[ARborIA] Modelo não devolveu JSON válido; usando modo local.")
                return None

            dados.setdefault("sucesso", True)
            dados.setdefault("modo", "multimodal")
            return dados

        except Exception as exc:  # noqa: BLE001 - fallback é intencional
            nome = type(exc).__name__
            modelos_tentados.append(modelo)
            mensagem = str(exc)

            # Modelo inválido no provedor: tenta um preferido uma única vez.
            if (tentativa == 0 and base == BASE_COARENA
                    and ("model" in mensagem.lower() or "not found" in mensagem.lower())):
                modelo = MODELOS_COARENA_PREFERIDOS[0]
                print(f"[ARborIA] Modelo alternado para {modelo} ({nome}).")
                continue

            print(f"[ARborIA] IA multimodal falhou ({nome}): {mensagem[:200]}")
            return None

    return None


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python ia/ia_multimodal.py caminho/da/imagem.jpg")
        raise SystemExit(1)
    resultado = analisar_imagem(sys.argv[1])
    print(json.dumps(resultado, ensure_ascii=False, indent=2)
          if resultado else "Sem resultado multimodal — usar modo local.")
