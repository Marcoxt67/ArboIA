"""
Gera jogo/imprimir/fichas.html a partir de ia/limites.json.

Uso:
    python jogo/imprimir/gerar_fichas.py

O HTML gerado é estático (sem dependência de rede) e pronto para Ctrl+P.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
BASE = RAIZ / "ia" / "limites.json"
SAIDA = Path(__file__).resolve().parent / "fichas.html"


def esc(texto: str) -> str:
    return html.escape(str(texto))


def gerar() -> None:
    dados = json.loads(BASE.read_text(encoding="utf-8"))

    cartoes = []
    for limite in dados["limites"]:
        central = " ★" if limite.get("central") else ""
        problematicas = "".join(
            f'<div class="p"><b>{esc(p["codigo"])}</b> {esc(p["texto"])}</div>'
            for p in limite["problematicas"]
        )
        intervencoes = "".join(
            f'<div class="i"><b>{esc(i["codigo"])}</b> {esc(i["texto"])}</div>'
            for i in limite["intervencoes"]
        )

        cartoes.append(f"""
        <div class="sheet limite">
          <div class="topo">
            <span class="codigo">{esc(limite['codigo'])}</span>
            <span class="titulo">🔵 {esc(limite['nome'])}{central}</span>
          </div>
          <div class="meta"><b>Variável:</b> {esc(limite['variavel_controle'])}</div>
          <div class="zonas">
            <div class="segura">Segura: {esc(limite['zona_segura'])}</div>
            <div class="incerteza">Incerteza: {esc(limite['zona_incerteza'])}</div>
            <div class="risco">Risco: {esc(limite['zona_risco'])}</div>
          </div>
          <div class="desc">{esc(limite['descricao'])}</div>
          <div class="secao">PROBLEMÁTICAS</div>
          {problematicas}
          <div class="secao">INTERVENÇÕES</div>
          {intervencoes}
        </div>

        <div class="sheet problema">
          <div class="topo"><span class="codigo">{esc(limite['codigo'])}-P</span>
            <span class="titulo">🟠 {esc(limite['nome'])}</span></div>
          {problematicas}
          <div class="rodape">Cenários-problema para a rodada.</div>
        </div>

        <div class="sheet intervencao">
          <div class="topo"><span class="codigo">{esc(limite['codigo'])}-I</span>
            <span class="titulo">🟢 {esc(limite['nome'])}</span></div>
          {intervencoes}
          <div class="rodape">Propostas de intervenção.</div>
        </div>
        """)

    conteudo = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>ARboIA — Fichas para impressão</title>
<style>
  @page {{ size: A4; margin: 10mm; }}
  body {{ font-family: Arial, sans-serif; font-size: 9pt; color: #222; }}
  h1 {{ font-size: 16pt; margin: 0 0 4mm; }}
  .intro {{ margin-bottom: 6mm; font-size: 9pt; color: #555; }}
  .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 4mm; }}
  .sheet {{ border: 1px dashed #999; border-radius: 3mm; padding: 3mm;
            break-inside: avoid; min-height: 82mm; }}
  .limite {{ border-top: 5px solid #0d6efd; }}
  .problema {{ border-top: 5px solid #fd7e14; }}
  .intervencao {{ border-top: 5px solid #198754; }}
  .topo {{ display:flex; gap:2mm; align-items:baseline; border-bottom:1px solid #ddd;
           padding-bottom:2mm; margin-bottom:2mm; }}
  .codigo {{ font-family: monospace; font-size: 8pt; color:#666; }}
  .titulo {{ font-weight: bold; font-size: 10pt; }}
  .meta {{ font-size: 8pt; margin-bottom: 2mm; }}
  .zonas {{ font-size: 7.5pt; margin-bottom: 2mm; }}
  .segura {{ color:#198754; }} .incerteza {{ color:#b27a00; }} .risco {{ color:#c62828; }}
  .desc {{ font-size: 8pt; color:#444; margin-bottom:2mm; }}
  .secao {{ font-size: 7.5pt; font-weight:bold; color:#666; margin:2mm 0 1mm; }}
  .p {{ background:#fff6ec; border-left:3px solid #fd7e14; padding:1.5mm 2mm;
        margin-bottom:1.5mm; font-size:8pt; }}
  .i {{ background:#edf8f1; border-left:3px solid #198754; padding:1.5mm 2mm;
        margin-bottom:1.5mm; font-size:8pt; }}
  .rodape {{ margin-top:3mm; font-size:7pt; color:#888; }}
  @media print {{ .intro {{ display:none; }} }}
</style>
</head>
<body>
  <h1>🌳 ARboIA — Fichas do jogo</h1>
  <div class="intro">
    Recorte cada ficha pelas bordas tracejadas. 9 fichas azuis (limites),
    9 folhas laranjas com 3 problemáticas cada, 9 folhas verdes com 3 intervenções cada.
    Use Ctrl+P para imprimir. Modelo: {esc(dados['metadados']['versao_modelo'])}.
  </div>
  <div class="grid">
    {''.join(cartoes)}
  </div>
</body>
</html>
"""
    SAIDA.write_text(conteudo, encoding="utf-8")
    print(f"✅ Gerado: {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    gerar()
