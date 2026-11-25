"""
ARboIA — Analisador pedagógico

Recebe o resultado da leitura de imagem (OCR local ou multimodal) e devolve
um relatório estruturado com:
  - fichas reconhecidas (limites, problemáticas, intervenções);
  - sinergias e trade-offs;
  - pontos fortes, lacunas e perguntas reflexivas.

O analisador NUNCA dá a resposta final: ele devolve perguntas e relações.
"""

from __future__ import annotations

import json
import os
import re
import unicodedata
from difflib import SequenceMatcher
from typing import Any

CAMINHO_BASE = os.path.join(os.path.dirname(__file__), "limites.json")


# --------------------------------------------------------------------------- #
# Normalização e casamento
# --------------------------------------------------------------------------- #

def normalizar(texto: str) -> str:
    """Minúsculas, sem acentos, sem pontuação redundante."""
    if not texto:
        return ""
    texto = str(texto).lower()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    texto = re.sub(r"[^\w\s./-]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


STOPWORDS = {
    "de", "do", "da", "dos", "das", "no", "na", "nos", "nas", "um", "uma",
    "uns", "umas", "o", "a", "os", "as", "e", "em", "para", "com", "por",
    "que", "se", "ao", "aos", "sua", "seu", "suas", "seus", "pelos", "pela",
}


def tokenizar(texto: str) -> list[str]:
    """Tokens informativos (sem stopwords e sem palavras curtas)."""
    return [
        token for token in normalizar(texto).split()
        if len(token) > 2 and token not in STOPWORDS
    ]


def similaridade(a: str, b: str) -> float:
    """Similaridade entre duas strings normalizadas."""
    a, b = normalizar(a), normalizar(b)
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def pontuar_texto(texto_alvo: str, termos: list[str], texto_base: str,
                  codigo: str | None = None) -> float:
    """
    Pontua o quanto `texto_base` contém `texto_alvo`.

    Usa cobertura de tokens informativos (evita falsos positivos por
    substring), presença de palavras-chave e código explícito da ficha.
    """
    alvo_norm = normalizar(texto_alvo)
    base_norm = normalizar(texto_base)
    if not alvo_norm or not base_norm:
        return 0.0

    tokens_alvo = tokenizar(texto_alvo)
    tokens_base = set(tokenizar(texto_base))
    cobertura = (
        sum(1 for token in tokens_alvo if token in tokens_base) / len(tokens_alvo)
        if tokens_alvo else 0.0
    )

    palavras_chave = 0.0
    for termo in termos:
        termo_norm = normalizar(termo)
        if len(termo_norm) < 3:
            continue
        partes = termo_norm.split()
        if termo_norm in base_norm or termo_norm in tokens_base:
            palavras_chave += 0.40
        elif all(parte in base_norm for parte in partes):
            palavras_chave += 0.20

    pontos = (
        0.50 * cobertura
        + 0.50 * min(palavras_chave, 1.0)
        + 0.15 * similaridade(alvo_norm, base_norm)
    )

    if codigo:
        codigo_norm = normalizar(codigo)
        variantes = {codigo_norm}
        # O OCR costuma confundir a letra I com o dígito 1 (I1.1 -> 11.1).
        if codigo_norm.startswith("i"):
            variantes.add("1" + codigo_norm[1:])
        if any(variante in base_norm for variante in variantes):
            pontos += 0.60

    return round(pontos, 4)


# --------------------------------------------------------------------------- #
# Analisador
# --------------------------------------------------------------------------- #

class Analisador:
    """Analisa uma combinação de fichas usando a base de conhecimento."""

    def __init__(self, caminho_base: str = CAMINHO_BASE):
        with open(caminho_base, "r", encoding="utf-8") as arquivo:
            self.base = json.load(arquivo)
        self.limites = {item["id"]: item for item in self.base["limites"]}

    # --------------------------- identificação ---------------------------- #

    def identificar_limites(self, texto: str, limiar: float = 0.25) -> list[dict[str, Any]]:
        resultados = []
        for limite in self.base["limites"]:
            pontos = pontuar_texto(
                limite["nome"], limite.get("palavras_chave", []), texto,
                codigo=limite["codigo"],
            )
            if pontos >= limiar:
                resultados.append({
                    "id": limite["id"],
                    "codigo": limite["codigo"],
                    "nome": limite["nome"],
                    "pontuacao": round(min(pontos, 1.0), 4),
                    "central": limite.get("central", False),
                })
        return sorted(resultados, key=lambda r: r["pontuacao"], reverse=True)

    def identificar_cartoes(self, texto: str, tipo: str,
                            limiar: float = 0.28) -> list[dict[str, Any]]:
        """Identifica problemáticas ou intervenções pelo texto/código."""
        resultados = []
        for limite in self.base["limites"]:
            colecao = limite.get(tipo, [])
            for cartao in colecao:
                pontos = pontuar_texto(
                    cartao["texto"], cartao.get("palavras_chave", []), texto,
                    codigo=cartao["codigo"],
                )
                if pontos >= limiar:
                    resultados.append({
                        "codigo": cartao["codigo"],
                        "texto": cartao["texto"],
                        "limite_id": limite["id"],
                        "limite_nome": limite["nome"],
                        "pontuacao": round(min(pontos, 1.0), 4),
                        "afeta": cartao.get("afeta", []),
                    })
        return sorted(resultados, key=lambda r: r["pontuacao"], reverse=True)

    # ------------------------------ relações ------------------------------ #

    def sinergias_entre(self, ids: set[str]) -> list[dict[str, Any]]:
        encontradas = []
        for sinergia in self.base.get("sinergias", []):
            conjunto = set(sinergia["de"]) | set(sinergia["para"])
            if conjunto.issubset(ids) and len(conjunto) >= 2:
                encontradas.append(sinergia.copy())
        return encontradas

    def tradeoffs_entre(self, ids: set[str]) -> list[dict[str, Any]]:
        encontrados = []
        for tradeoff in self.base.get("tradeoffs", []):
            conjunto = set(tradeoff["de"])
            if conjunto.issubset(ids) and len(conjunto) >= 2:
                encontrados.append(tradeoff.copy())
        return encontrados

    def lacunas(self, ids: set[str]) -> list[dict[str, str]]:
        return [
            {"id": l["id"], "nome": l["nome"], "central": l.get("central", False)}
            for l in self.base["limites"] if l["id"] not in ids
        ]

    # ------------------------------ feedback ------------------------------ #

    def gerar_feedback(self, dados: dict[str, Any],
                       multimodal: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Gera o relatório final.

        `dados` deve conter ao menos:
            {"texto": str, "regioes": [...], "relacoes": [...]}
        `multimodal`, quando presente, sobrescreve a identificação local.
        """
        texto = dados.get("texto", "")

        if multimodal and multimodal.get("sucesso"):
            limites = multimodal.get("limites", [])
            problematicas = multimodal.get("problematicas", [])
            intervencoes = multimodal.get("intervencoes", [])
            modo = multimodal.get("modo", "multimodal")
        else:
            limites = self.identificar_limites(texto)
            problematicas = self.identificar_cartoes(texto, "problematicas")
            intervencoes = self.identificar_cartoes(texto, "intervencoes")
            modo = "local"

        ids = {item["id"] for item in limites if "id" in item}
        # Inclui limites afetados pelas intervenções reconhecidas.
        for intervencao in intervencoes:
            for afetado in intervencao.get("afeta", []):
                if afetado in self.limites:
                    ids.add(afetado)

        sinergias = self.sinergias_entre(ids)
        tradeoffs = self.tradeoffs_entre(ids)
        faltantes = self.lacunas(ids)

        # Sinergias e trade-offs nomeados pelo modelo multimodal.
        if multimodal and multimodal.get("sucesso"):
            for item in multimodal.get("sinergias", []):
                if item.get("texto") and item["texto"] not in [s["texto"] for s in sinergias]:
                    sinergias.append(item)
            for item in multimodal.get("tradeoffs", []):
                if item.get("texto") and item["texto"] not in [t["texto"] for t in tradeoffs]:
                    tradeoffs.append(item)

        # ----------------------- pontos fortes --------------------------- #
        pontos_fortes: list[str] = []
        if len(ids) >= 2:
            pontos_fortes.append(
                f"Vocês conectaram {len(ids)} limites planetários — "
                "isso é pensamento sistêmico."
            )
        if any(r.get("central") for r in limites):
            pontos_fortes.append(
                "Pelo menos um limite central (clima ou biodiversidade) foi incluído."
            )
        if problematicas and intervencoes:
            pontos_fortes.append(
                "A combinação liga um problema concreto a uma intervenção possível."
            )
        if sinergias:
            pontos_fortes.append(
                f"{len(sinergias)} sinergia(s) detectada(s): uma ação ajuda mais de um limite."
            )
        if not pontos_fortes:
            pontos_fortes.append(
                "A combinação foi registrada. Vamos olhar o que ainda pode ser conectado."
            )

        # ----------------------- sugestões -------------------------------- #
        sugestoes: list[str] = []
        if not ids:
            sugestoes.append(
                "Tente incluir uma ficha azul (limite planetário) no centro da mesa."
            )
        if not problematicas:
            sugestoes.append(
                "Adicione uma ficha laranja: qual problema concreto vocês querem enfrentar?"
            )
        if not intervencoes:
            sugestoes.append(
                "Adicione uma ficha verde: que ação transformaria essa situação?"
            )
        if faltantes:
            centrais_faltantes = [f for f in faltantes if f.get("central")]
            if centrais_faltantes:
                sugestoes.append(
                    "Um limite central ficou de fora: "
                    + ", ".join(f["nome"] for f in centrais_faltantes)
                    + ". Como ele se relaciona com a sua proposta?"
                )
            if len(faltantes) >= 6:
                sugestoes.append(
                    "Muitos limites ficaram de fora. Que tal ampliar a roda para 3 limites?"
                )
        if tradeoffs:
            sugestoes.append(
                "Há um efeito colateral na mesa. Proponham uma segunda intervenção para mitigá-lo."
            )

        # ----------------------- perguntas -------------------------------- #
        perguntas = list(self.base.get("perguntas_reflexivas", []))[:5]
        if tradeoffs:
            perguntas.insert(0, "Como vocês mitigariam o efeito colateral apontado acima?")
        if faltantes:
            perguntas.insert(0, f"Por que será que {faltantes[0]['nome']} não apareceu na mesa?")

        mensagens = self.base.get("mensagens_feedback", {})
        if not ids and not problematicas and not intervencoes:
            resumo = mensagens.get("sem_fichas", "Nenhuma ficha reconhecida.")
        elif len(ids) + len(problematicas) + len(intervencoes) <= 2:
            resumo = mensagens.get("poucas_fichas", "Poucas fichas reconhecidas.")
        else:
            resumo = mensagens.get("sucesso", "Análise concluída.")

        if modo == "local":
            aviso_modo = mensagens.get("modo_local", "Análise local.")
        else:
            aviso_modo = mensagens.get("modo_multimodal", "Análise com IA multimodal.")

        return {
            "modo": modo,
            "resumo": resumo,
            "aviso_modo": aviso_modo,
            "fichas_reconhecidas": {
                "limites": limites,
                "problematicas": problematicas,
                "intervencoes": intervencoes,
                "total_regioes_imagem": dados.get("estimativa_fichas", 0),
            },
            "relacoes_espaciais": dados.get("relacoes", [])[:20],
            "sinergias": sinergias,
            "tradeoffs": tradeoffs,
            "pontos_fortes": pontos_fortes,
            "sugestoes": sugestoes,
            "lacunas": faltantes,
            "perguntas_reflexivas": perguntas[:6],
            "advertencia": (
                "Este feedback é um insumo para a discussão em sala, não uma nota "
                "nem uma resposta definitiva."
            ),
        }


# --------------------------------------------------------------------------- #
# API de conveniência
# --------------------------------------------------------------------------- #

def analisar(dados: dict[str, Any],
             multimodal: dict[str, Any] | None = None) -> dict[str, Any]:
    """Atalho para criar o analisador e gerar o feedback."""
    return Analisador().gerar_feedback(dados, multimodal)


if __name__ == "__main__":
    import sys

    texto_exemplo = (
        "Mudanca climatica transporte urbano eletrificacao de onibus "
        "energia renovavel fosforo"
    )
    relatorio = analisar({"texto": texto_exemplo, "regioes": [], "relacoes": []})
    print(json.dumps(relatorio, ensure_ascii=False, indent=2))
