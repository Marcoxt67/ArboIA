"""
ARboIA — Conquistas e medalhas

Calcula as medalhas a partir do progresso salvo na sessão.
Não substitui a pontuação: apenas torna visível a trajetória do grupo.
"""

from __future__ import annotations

from typing import Any

CONQUISTAS: list[dict[str, str]] = [
    {"id": "primeiro", "icone": "🌱", "nome": "Primeiro Passo",
     "descricao": "Concluir a fase 1 da trilha."},
    {"id": "conector", "icone": "🔗", "nome": "Conector de Sistemas",
     "descricao": "Conectar pelo menos dois limites planetários em uma análise."},
    {"id": "sinergista", "icone": "✨", "nome": "Sinergista",
     "descricao": "Ter uma sinergia reconhecida pela IA."},
    {"id": "equilibrista", "icone": "⚖️", "nome": "Equilibrista",
     "descricao": "Identificar um efeito colateral (trade-off)."},
    {"id": "explorador", "icone": "🧭", "nome": "Explorador",
     "descricao": "Concluir cinco fases."},
    {"id": "fotografo", "icone": "📸", "nome": "Olhar Atento",
     "descricao": "Usar a análise por fotografia."},
    {"id": "digital", "icone": "💻", "nome": "Mente Digital",
     "descricao": "Usar a análise digital com fichas na plataforma."},
    {"id": "nota100", "icone": "💯", "nome": "Combinação Perfeita",
     "descricao": "Alcançar 100 pontos em alguma fase."},
    {"id": "guardiao", "icone": "🏆", "nome": "Guardião da Terra",
     "descricao": "Concluir todas as 10 fases."},
]


def calcular_conquistas(progresso: dict[str, Any]) -> list[dict[str, Any]]:
    """Retorna todas as conquistas com o campo `desbloqueada` preenchido."""
    concluidas = progresso.get("concluidas", []) or []
    historico = progresso.get("historico", []) or []
    total_fases = progresso.get("total_fases", 10)

    condicoes = {
        "primeiro": 1 in concluidas,
        "conector": any(item.get("limites", 0) >= 2 for item in historico),
        "sinergista": any(item.get("sinergias", 0) >= 1 for item in historico),
        "equilibrista": any(item.get("tradeoffs", 0) >= 1 for item in historico),
        "explorador": len(concluidas) >= 5,
        "fotografo": bool(progresso.get("usos_foto", 0)),
        "digital": bool(progresso.get("usos_digital", 0)),
        "nota100": any(item.get("pontos", 0) >= 100 for item in historico),
        "guardiao": len(concluidas) >= total_fases,
    }

    # Progresso numérico (atual/meta) das conquistas que se contam em etapas.
    progressos = {
        "primeiro": (1 if 1 in concluidas else 0, 1),
        "conector": (1 if condicoes["conector"] else 0, 1),
        "sinergista": (1 if condicoes["sinergista"] else 0, 1),
        "equilibrista": (1 if condicoes["equilibrista"] else 0, 1),
        "explorador": (min(len(concluidas), 5), 5),
        "fotografo": (min(int(progresso.get("usos_foto", 0) or 0), 1), 1),
        "digital": (min(int(progresso.get("usos_digital", 0) or 0), 1), 1),
        "nota100": (1 if condicoes["nota100"] else 0, 1),
        "guardiao": (min(len(concluidas), total_fases), total_fases),
    }

    resultado = []
    for conquista in CONQUISTAS:
        atual, meta = progressos.get(conquista["id"], (0, 1))
        resultado.append({
            **conquista,
            "desbloqueada": bool(condicoes.get(conquista["id"], False)),
            "atual": atual,
            "meta": meta,
        })
    return resultado


def registrar_metricas(item: dict[str, Any], relatorio: dict[str, Any]) -> dict[str, Any]:
    """Extrai métricas da análise para alimentar as conquistas."""
    fichas = relatorio.get("fichas_reconhecidas", {})
    item["limites"] = len(fichas.get("limites", []) or [])
    item["sinergias"] = len(relatorio.get("sinergias", []) or [])
    item["tradeoffs"] = len(relatorio.get("tradeoffs", []) or [])
    return item
