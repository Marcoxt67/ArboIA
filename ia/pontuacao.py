"""
ARboIA — Cálculo de pontuação da gamificação

Converte o relatório pedagógico em uma nota de 0 a 100.

Critérios (bruto máximo = 110, limitado a 100):
    Completude das fichas ............ até 30 (10 por tipo: limite, problema, intervenção)
    Bônus combinação completa ........ +10 (os três tipos presentes)
    Diversidade de limites ........... até 30 (10 por limite, máx. 3)
    Sinergias ........................ até 20 (10 por sinergia, máx. 2)
    Trade-offs identificados ......... até 10 (5 por efeito colateral, máx. 2)
    Limite central incluído .......... +10

A nota NÃO mede "acertar a resposta": mede a qualidade da conexão sistêmica.
"""

from __future__ import annotations

from typing import Any

LIMITES_CENTRAIS = {"clima", "biodiversidade"}


def classificar(pontos: int) -> str:
    """Faixa de classificação simbólica para o feedback."""
    if pontos >= 90:
        return "Guardião da Terra 🏆"
    if pontos >= 80:
        return "Pensador Sistêmico 🌟"
    if pontos >= 70:
        return "Explorador Avançado 🚀"
    if pontos >= 60:
        return "Explorador em Formação 🌱"
    return "Explorando 🔍"


def calcular_pontuacao(relatorio: dict[str, Any], meta: int = 0) -> dict[str, Any]:
    """Calcula pontos, detalha as rubricas e compara com a meta da fase."""
    fichas = relatorio.get("fichas_reconhecidas", {})
    limites = fichas.get("limites", []) or []
    problematicas = fichas.get("problematicas", []) or []
    intervencoes = fichas.get("intervencoes", []) or []
    sinergias = relatorio.get("sinergias", []) or []
    tradeoffs = relatorio.get("tradeoffs", []) or []

    detalhes: list[dict[str, Any]] = []

    def adicionar(item: str, pontos: int, observacao: str = "") -> None:
        detalhes.append({"item": item, "pontos": pontos, "observacao": observacao})

    # 1. Completude (até 30)
    for nome, colecao, rotulo in [
        ("Limite planetário", limites, "ficha azul"),
        ("Problemática", problematicas, "ficha laranja"),
        ("Intervenção", intervencoes, "ficha verde"),
    ]:
        pontos = 10 if colecao else 0
        adicionar(
            nome,
            pontos,
            f"{len(colecao)} {rotulo}(s) reconhecida(s)" if colecao else f"Faltou {rotulo}",
        )

    combinacao_completa = bool(limites and problematicas and intervencoes)
    adicionar(
        "Combinação completa",
        10 if combinacao_completa else 0,
        "Limite + problemática + intervenção" if combinacao_completa
        else "Inclua os três tipos de ficha",
    )

    # 2. Diversidade de limites (até 30)
    qtd_limites = min(len(limites), 3)
    adicionar(
        "Conexão entre limites",
        qtd_limites * 10,
        f"{len(limites)} limite(s) identificado(s) — máximo 3 contam pontos",
    )

    # 3. Sinergias (até 20)
    qtd_sinergias = min(len(sinergias), 2)
    adicionar(
        "Sinergias",
        qtd_sinergias * 10,
        f"{len(sinergias)} sinergia(s) detectada(s)",
    )

    # 4. Trade-offs (até 10)
    qtd_tradeoffs = min(len(tradeoffs), 2)
    adicionar(
        "Efeitos colaterais",
        qtd_tradeoffs * 5,
        f"{len(tradeoffs)} trade-off(s) identificado(s)",
    )

    # 5. Limite central (10)
    tem_central = any(
        (l.get("id") in LIMITES_CENTRAIS) or l.get("central")
        for l in limites
    )
    adicionar(
        "Limite central",
        10 if tem_central else 0,
        "Clima ou biodiversidade funcional" if tem_central else "Inclua um limite central",
    )

    total = min(sum(d["pontos"] for d in detalhes), 100)

    return {
        "pontos": total,
        "pontuacao": total,
        "meta": meta,
        "atingiu": total >= meta if meta else total >= 60,
        "pontos_faltantes": max(0, meta - total),
        "classificacao": classificar(total),
        "detalhes": detalhes,
        "resumo_rubrica": (
            f"{len(limites)} limite(s) · {len(problematicas)} problemática(s) · "
            f"{len(intervencoes)} intervenção(ões) · {len(sinergias)} sinergia(s) · "
            f"{len(tradeoffs)} trade-off(s)"
        ),
    }
