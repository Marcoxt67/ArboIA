"""
ARboIA — Aplicação web

Fluxo:
    upload da foto -> (IA multimodal opcional) -> OCR local -> analisador
                   -> feedback pedagógico na tela

Rotas:
    GET  /                dashboard (apresentação + acesso ao jogo)
    GET  /jogar           área principal com fichas digitais
    POST /analisar_digital   avalia a combinação montada na plataforma
    GET  /limites         os 9 limites planetários (cartões interativos)
    GET  /ia              assistente virtual (foto ou análise digital)
    POST /analisar        processa foto e renderiza resultado livre
    POST /api/analisar    mesmo fluxo, resposta JSON
    GET  /jogo            painel da trilha de 10 fases (desafios)
    GET  /fase/<n>        desafio da fase n
    POST /analisar_fase   pontua e avança (ou pede outra tentativa)
    POST /reiniciar       zera o progresso
    GET  /progresso       pontuações, medalhas e histórico
    GET  /fichas          fichas na interface (impressão)
    GET  /sobre           sobre o projeto
    GET  /perfil          perfil, nível e jornada do jogador
    POST /perfil/nome     altera o nome exibido no perfil
    GET  /conquistas      medalhas e progresso de cada conquista
    GET  /foto            captura/envio de foto das fichas (análise por foto)
    GET  /configuracoes   preferências da interface
"""

from __future__ import annotations

import json
import logging
import os
import sys
import uuid
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)

# Permite executar tanto `python app/app.py` quanto `flask --app app.app run`.
DIRETORIO_RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DIRETORIO_RAIZ))

from ia.analise import Analisador  # noqa: E402
from ia.conquistas import calcular_conquistas, registrar_metricas  # noqa: E402
from ia.ia_multimodal import analisar_imagem as analisar_multimodal  # noqa: E402
from ia.ocr import interpretar_imagem  # noqa: E402
from ia.pontuacao import calcular_pontuacao  # noqa: E402

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

EXTENSOES_PERMITIDAS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
TAMANHO_MAXIMO = 16 * 1024 * 1024  # 16 MB

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "arboia-dev-secret-alterar-em-producao")
app.config["MAX_CONTENT_LENGTH"] = TAMANHO_MAXIMO
app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)

analisador = Analisador()

with open(DIRETORIO_RAIZ / "ia" / "limites.json", "r", encoding="utf-8") as _f:
    base_conhecimento = json.load(_f)

with open(DIRETORIO_RAIZ / "jogo" / "fases.json", "r", encoding="utf-8") as _f:
    dados_fases = json.load(_f)

FASES = dados_fases["fases"]
TOTAL_FASES = len(FASES)

# Ícones/cores por limite — usados nos cartões interativos.
ESTILO_LIMITES = {
    "clima": ("🌡️", "#0ea5e9"),
    "biodiversidade": ("🦋", "#7cc43f"),
    "extincao": ("🦜", "#fd7e14"),
    "nitrogenio": ("🌾", "#6f42c1"),
    "fosforo": ("💎", "#6610f2"),
    "uso_solo": ("🌱", "#2e7d4f"),
    "agua": ("💧", "#0284c7"),
    "oceanos": ("🪸", "#22d3ee"),
    "aerossois": ("🌬️", "#6c757d"),
}

# Nomes curtos (para os cartões da interface) e ícones de cada ficha.
NOMES_CURTOS = {
    "L1": "Mudança Climática", "L2": "Biodiversidade Funcional", "L3": "Extinção Biótica",
    "L4": "Ciclo do Nitrogênio", "L5": "Ciclo do Fósforo", "L6": "Uso do Solo",
    "L7": "Água Doce", "L8": "Acidificação dos Oceanos", "L9": "Aerossóis",
    "P1.1": "Emissões do transporte", "P1.2": "Ondas de calor", "P1.3": "Degelo acelerado",
    "I1.1": "Ônibus elétricos", "I1.2": "Manguezais urbanos", "I1.3": "Agroecologia",
    "P2.1": "Polinizadores em risco", "P2.2": "Habitat fragmentado", "P2.3": "Espécies invasoras",
    "I2.1": "Corredores ecológicos", "I2.2": "Agrofloresta", "I2.3": "Controle biológico",
    "P3.1": "Tráfico de animais", "P3.2": "Endêmicas perdidas", "P3.3": "Pesca predatória",
    "I3.1": "Unidades de conservação", "I3.2": "Reintrodução", "I3.3": "DNA ambiental",
    "P4.1": "Algas tóxicas", "P4.2": "Solo acidificado", "P4.3": "Dejetos suínos",
    "I4.1": "Adubação de precisão", "I4.2": "Rotação de culturas", "I4.3": "Zonas úmidas",
    "P5.1": "Mineração de fosfato", "P5.2": "Esgoto em lagoas", "P5.3": "Dependência externa",
    "I5.1": "Struvita", "I5.2": "Compostagem", "I5.3": "Saneamento básico",
    "P6.1": "Desmatamento", "P6.2": "Pastagem degradada", "P6.3": "Loteamento irregular",
    "I6.1": "Pastagem sustentável", "I6.2": "Restauração de APPs", "I6.3": "Zoneamento",
    "P7.1": "Irrigação ineficiente", "P7.2": "Captação irregular", "P7.3": "Rios contaminados",
    "I7.1": "Gotejamento", "I7.2": "Água da chuva", "I7.3": "Reúso de água",
    "P8.1": "Corais branqueados", "P8.2": "Pesca artesanal", "P8.3": "Erosão costeira",
    "I8.1": "Menos CO₂", "I8.2": "Recifes resistentes", "I8.3": "Proteção de mangues",
    "P9.1": "Queimadas", "P9.2": "Material particulado", "P9.3": "Poeira transportada",
    "I9.1": "Filtros e controle", "I9.2": "Manejo do fogo", "I9.3": "Monitoramento",
}

ICONES_FICHA = {
    "P1.1": "🚗", "P1.2": "☀️", "P1.3": "🧊", "I1.1": "🚌", "I1.2": "🌳", "I1.3": "🌾",
    "P2.1": "🐝", "P2.2": "🧩", "P2.3": "🌿", "I2.1": "🦌", "I2.2": "🌴", "I2.3": "🐞",
    "P3.1": "🦜", "P3.2": "🧬", "P3.3": "🎣", "I3.1": "🏞️", "I3.2": "🐢", "I3.3": "🧪",
    "P4.1": "🌊", "P4.2": "🫘", "P4.3": "🐖", "I4.1": "📡", "I4.2": "🔄", "I4.3": "🪷",
    "P5.1": "⛏️", "P5.2": "🧼", "P5.3": "🚢", "I5.1": "♻️", "I5.2": "🍂", "I5.3": "🚰",
    "P6.1": "🪓", "P6.2": "🐄", "P6.3": "🏚️", "I6.1": "📈", "I6.2": "🌱", "I6.3": "🗺️",
    "P7.1": "💦", "P7.2": "🕳️", "P7.3": "🚱", "I7.1": "💧", "I7.2": "🌧️", "I7.3": "🚿",
    "P8.1": "🪸", "P8.2": "🦀", "P8.3": "🌊", "I8.1": "📉", "I8.2": "🐠", "I8.3": "🥥",
    "P9.1": "🔥", "P9.2": "🏭", "P9.3": "🌫️", "I9.1": "🛡️", "I9.2": "🧑‍🚒", "I9.3": "🛰️",
}

LIMITES = []
for _limite in base_conhecimento["limites"]:
    _icone, _cor = ESTILO_LIMITES.get(_limite["id"], ("🌍", "#2e7d4f"))
    LIMITES.append({
        **_limite, "icone": _icone, "cor": _cor,
        "curto": NOMES_CURTOS.get(_limite["codigo"], _limite["nome"]),
    })

# Fichas digitais agrupadas por categoria (para /jogar e /ia).
FICHAS_DIGITAIS = []
for _limite in LIMITES:
    FICHAS_DIGITAIS.append({
        "codigo": _limite["codigo"],
        "texto": _limite["nome"],
        "curto": _limite["curto"],
        "categoria": "limite",
        "icone": _limite["icone"],
        "cor": _limite["cor"],
        "detalhe": _limite.get("descricao", ""),
    })
    for _problema in _limite.get("problematicas", []):
        FICHAS_DIGITAIS.append({
            "codigo": _problema["codigo"],
            "texto": _problema["texto"],
            "curto": NOMES_CURTOS.get(_problema["codigo"], _problema["texto"]),
            "categoria": "problema",
            "icone": ICONES_FICHA.get(_problema["codigo"], "⚠️"),
            "cor": "#fd7e14",
            "detalhe": _limite["nome"],
        })
    for _intervencao in _limite.get("intervencoes", []):
        FICHAS_DIGITAIS.append({
            "codigo": _intervencao["codigo"],
            "texto": _intervencao["texto"],
            "curto": NOMES_CURTOS.get(_intervencao["codigo"], _intervencao["texto"]),
            "categoria": "solucao",
            "icone": ICONES_FICHA.get(_intervencao["codigo"], "💡"),
            "cor": "#2e7d4f",
            "detalhe": _limite["nome"],
        })


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def extensao_permitida(nome_arquivo: str) -> bool:
    return Path(nome_arquivo).suffix.lower() in EXTENSOES_PERMITIDAS


def salvar_upload(arquivo) -> Path | None:
    """Salva o arquivo enviado com nome único."""
    if not arquivo or not arquivo.filename or not extensao_permitida(arquivo.filename):
        return None
    sufixo = Path(arquivo.filename).suffix.lower()
    nome = f"{uuid.uuid4().hex}{sufixo}"
    destino = UPLOAD_DIR / nome
    arquivo.save(str(destino))
    return destino


PONTOS_POR_NIVEL = 100  # a cada 100 pontos acumulados o jogador sobe de nível
NOME_PADRAO = "Jogador(a)"


def calcular_nivel(pontos: int) -> dict[str, int]:
    """Nível do jogador a partir dos pontos acumulados na trilha."""
    pontos = max(0, int(pontos))
    nivel = pontos // PONTOS_POR_NIVEL + 1
    percentual = round((pontos % PONTOS_POR_NIVEL) / PONTOS_POR_NIVEL * 100)
    return {"nivel": nivel, "proximo": nivel + 1, "percentual": percentual}


def registrar_atividade(texto: str) -> None:
    """Guarda um marco da jornada (uma vez por dia por tipo de atividade)."""
    hoje = date.today().isoformat()
    atividades = list(session.get("atividades", []))
    if any(a.get("data") == hoje and a.get("texto") == texto for a in atividades):
        return
    atividades.append({"data": hoje, "texto": texto})
    session["atividades"] = atividades[-12:]
    session.modified = True


def rotulo_data(iso: str) -> str:
    """'Hoje', 'Ontem' ou dd/mm."""
    try:
        dia = date.fromisoformat(iso)
    except (TypeError, ValueError):
        return ""
    hoje = date.today()
    if dia == hoje:
        return "Hoje"
    if dia == hoje - timedelta(days=1):
        return "Ontem"
    return dia.strftime("%d/%m")


def jornada_recente(limite: int = 3) -> list[dict[str, str]]:
    atividades = list(session.get("atividades", []))
    # mais recentes primeiro (a ordenação é estável: no mesmo dia vale a ordem de registro)
    recentes = sorted(reversed(atividades), key=lambda a: a.get("data", ""), reverse=True)[:limite]
    return [{"quando": rotulo_data(a.get("data", "")), "texto": a.get("texto", "")} for a in recentes]


@app.template_filter("nota10")
def filtro_nota10(pontos) -> str:
    """Converte 0-100 em nota 0-10 com vírgula (ex.: 95 -> '9,5')."""
    try:
        valor = round(float(pontos) / 10, 1)
    except (TypeError, ValueError):
        valor = 0.0
    texto = f"{valor:.1f}".replace(".", ",")
    return texto[:-2] if texto.endswith(",0") else texto


@app.template_filter("rotulo_nota")
def filtro_rotulo_nota(pontos) -> str:
    pontos = int(pontos or 0)
    if pontos >= 90:
        return "Excelente proposta!"
    if pontos >= 70:
        return "Ótima proposta!"
    if pontos >= 50:
        return "Boa proposta!"
    if pontos >= 30:
        return "Proposta em construção"
    return "Vamos tentar de novo!"


def fase_por_numero(numero: int) -> dict | None:
    """Busca uma fase pelo número (1 a TOTAL_FASES)."""
    return next((f for f in FASES if f["numero"] == numero), None)


def obter_progresso() -> dict[str, Any]:
    """Progresso persistido na sessão do navegador."""
    progresso = {
        "fase_atual": int(session.get("fase_atual", 1)),
        "concluidas": list(session.get("concluidas", [])),
        "pontuacao_total": int(session.get("pontuacao_total", 0)),
        "historico": list(session.get("historico", [])),
        "total_fases": TOTAL_FASES,
        "usos_foto": int(session.get("usos_foto", 0)),
        "usos_digital": int(session.get("usos_digital", 0)),
        "partidas": len(session.get("historico", [])),
        "conquistas": calcular_conquistas({
            "concluidas": session.get("concluidas", []),
            "historico": session.get("historico", []),
            "total_fases": TOTAL_FASES,
            "usos_foto": session.get("usos_foto", 0),
            "usos_digital": session.get("usos_digital", 0),
        }),
    }
    session["fase_atual"] = progresso["fase_atual"]
    session["concluidas"] = progresso["concluidas"]
    session["pontuacao_total"] = progresso["pontuacao_total"]
    session["historico"] = progresso["historico"]
    session["usos_foto"] = progresso["usos_foto"]
    session["usos_digital"] = progresso["usos_digital"]
    return progresso


def registrar_tentativa(numero: int, pontos: int, meta: int,
                        atingiu: bool, imagem: str,
                        relatorio: dict | None = None) -> None:
    """Atualiza histórico, pontuação e desbloqueio da próxima fase."""
    progresso = obter_progresso()
    item = {
        "fase": numero,
        "pontos": pontos,
        "meta": meta,
        "atingiu": atingiu,
        "imagem": imagem,
        "origem": "foto",
        "data": date.today().isoformat(),
    }
    if relatorio:
        registrar_metricas(item, relatorio)
    progresso["historico"].append(item)
    registrar_atividade("Praticou o jogo!")
    if atingiu:
        registrar_atividade(f"Concluiu a fase {numero:02d}")

    if atingiu:
        if numero not in progresso["concluidas"]:
            progresso["concluidas"].append(numero)
            progresso["pontuacao_total"] += pontos
        if numero < TOTAL_FASES:
            progresso["fase_atual"] = numero + 1

    session["fase_atual"] = progresso["fase_atual"]
    session["concluidas"] = progresso["concluidas"]
    session["pontuacao_total"] = progresso["pontuacao_total"]
    session["historico"] = progresso["historico"]
    session.modified = True


def processar(caminho: Path, texto_manual: str = "") -> dict:
    """Executa o pipeline completo de análise."""
    multimodal = None
    usa_multimodal = (
        os.getenv("USE_IA_MULTIMODAL", "true").lower() in {"1", "true", "sim", "yes"}
    )

    if usa_multimodal:
        multimodal = analisar_multimodal(str(caminho))

    leitura = interpretar_imagem(str(caminho))

    # Modo manual: permite analisar mesmo sem Tesseract instalado ou com foto ruim.
    if texto_manual and texto_manual.strip():
        leitura["texto"] = (leitura.get("texto", "") + "\n" + texto_manual).strip()
        leitura["avisos"].append(
            "Texto digitado manualmente foi incluído na análise."
        )
        if not leitura.get("estimativa_fichas"):
            leitura["estimativa_fichas"] = 0

    relatorio = analisador.gerar_feedback(leitura, multimodal)
    relatorio["imagem"] = f"/uploads/{caminho.name}"
    relatorio["leitura_bruta"] = {
        "texto": leitura.get("texto", "")[:1200],
        "estimativa_fichas": leitura.get("estimativa_fichas", 0),
        "avisos": leitura.get("avisos", []),
    }
    relatorio["pontuacao"] = calcular_pontuacao(relatorio)
    return relatorio


def processar_texto(texto: str) -> dict:
    """Avalia uma combinação montada digitalmente, sem imagem."""
    leitura = {
        "texto": texto.strip(),
        "estimativa_fichas": 0,
        "avisos": ["Combinação montada digitalmente na plataforma."],
        "regioes": [],
        "relacoes": [],
    }
    relatorio = analisador.gerar_feedback(leitura, None)
    relatorio["imagem"] = None
    relatorio["leitura_bruta"] = {
        "texto": leitura["texto"][:1200],
        "estimativa_fichas": 0,
        "avisos": leitura["avisos"],
    }
    relatorio["pontuacao"] = calcular_pontuacao(relatorio)
    return relatorio


def registrar_analise_livre(relatorio: dict, origem: str) -> None:
    """Registra uma análise fora da trilha para histórico e conquistas."""
    progresso = obter_progresso()
    item = {
        "fase": 0,
        "pontos": relatorio.get("pontuacao", {}).get("pontos", 0),
        "meta": 0,
        "atingiu": True,
        "imagem": relatorio.get("imagem"),
        "origem": origem,
        "resumo": relatorio.get("resumo", ""),
        "data": date.today().isoformat(),
    }
    registrar_metricas(item, relatorio)
    registrar_atividade("Praticou o jogo!")
    registrar_atividade("Concluiu uma análise com IA")
    progresso["historico"].append(item)
    if origem == "foto":
        progresso["usos_foto"] += 1
    else:
        progresso["usos_digital"] += 1
    for chave in ("historico", "usos_foto", "usos_digital"):
        session[chave] = progresso[chave]
    session.modified = True


@app.context_processor
def injetar_progresso():
    """Disponibiliza o resumo do progresso em todos os templates."""
    progresso = obter_progresso()
    nivel = calcular_nivel(progresso["pontuacao_total"])

    # Sobe de nível: a tela de parabéns aparece uma única vez por nível.
    visto = int(session.get("nivel_visto", 1))
    subiu_nivel = None
    if nivel["nivel"] > visto:
        subiu_nivel = nivel["nivel"]
    if nivel["nivel"] != visto:
        session["nivel_visto"] = nivel["nivel"]

    return {
        "progresso_resumo": {
            "pontos": progresso["pontuacao_total"],
            "concluidas": len(progresso["concluidas"]),
            "total": TOTAL_FASES,
        },
        "nivel_info": nivel,
        "nome_jogador": session.get("nome", NOME_PADRAO),
        "subiu_nivel": subiu_nivel,
    }


# --------------------------------------------------------------------------- #
# Rotas
# --------------------------------------------------------------------------- #

@app.route("/")
def index():
    return render_template(
        "index.html",
        limites=LIMITES,
        total_limites=len(LIMITES),
        total_fichas=len(FICHAS_DIGITAIS),
        progresso=obter_progresso(),
    )


@app.route("/jogar")
def jogar():
    """Redireciona o alias antigo para a trilha de desafios."""
    return redirect(url_for("jogo"))


@app.route("/limites")
def limites():
    registrar_atividade("Explorou os 9 Limites")
    return render_template(
        "limites.html",
        limites=LIMITES,
        total_limites=len(LIMITES),
        icones_ficha=ICONES_FICHA,
        progresso=obter_progresso(),
    )


@app.route("/ia")
def area_ia():
    return render_template(
        "ia.html",
        fichas=FICHAS_DIGITAIS,
        progresso=obter_progresso(),
    )


@app.route("/analisar_digital", methods=["POST"])
def analisar_digital():
    codigos = request.form.get("fichas_selecionadas", "").split("|")
    codigos = [c.strip() for c in codigos if c.strip()]
    if not codigos:
        return render_template(
            "ia.html", fichas=FICHAS_DIGITAIS, relatorio=None,
            erro="Selecione ao menos uma ficha antes de pedir a análise.",
        ), 400

    # O analisador reconhece os códigos (L1, P1.1, I1.1...) direto no texto.
    relatorio = processar_texto(" ".join(codigos))
    registrar_analise_livre(relatorio, "digital")
    return render_template(
        "ia.html", fichas=FICHAS_DIGITAIS, relatorio=relatorio, erro=None,
        selecionados=codigos,
    )


@app.route("/progresso")
def progresso():
    return render_template(
        "progresso.html",
        fases=FASES,
        progresso=obter_progresso(),
    )


@app.route("/analisar", methods=["POST"])
def analisar():
    arquivo = request.files.get("imagem")
    if not arquivo or not arquivo.filename:
        return render_template(
            "resultado.html",
            erro="Nenhuma imagem foi enviada. Escolha uma foto das fichas.",
            relatorio=None,
        ), 400

    if not extensao_permitida(arquivo.filename):
        return render_template(
            "resultado.html",
            erro="Formato não aceito. Use PNG, JPG, JPEG ou WEBP.",
            relatorio=None,
        ), 400

    caminho = salvar_upload(arquivo)
    if caminho is None:
        return render_template(
            "resultado.html", erro="Falha ao salvar a imagem.", relatorio=None
        ), 500

    try:
        relatorio = processar(caminho, request.form.get("texto_manual", ""))
    except Exception as exc:  # noqa: BLE001
        logging.exception("Falha no pipeline de análise de imagem (/analisar)")
        return render_template(
            "resultado.html",
            erro=f"Não foi possível analisar a imagem. Consulte os logs do servidor. ({type(exc).__name__})",
            relatorio=None,
        ), 500

    registrar_analise_livre(relatorio, "foto")
    return render_template(
        "resultado.html", relatorio=relatorio, erro=None, progresso=obter_progresso()
    )


# --------------------------------------------------------------------------- #
# Gamificação — trilha de 10 fases
# --------------------------------------------------------------------------- #

@app.route("/jogo")
def jogo():
    return render_template(
        "jogo.html",
        fases=FASES,
        progresso=obter_progresso(),
        titulo=dados_fases["titulo"],
        descricao=dados_fases["descricao"],
        nota=dados_fases["nota"],
    )


@app.route("/fase/<int:numero>")
def fase(numero: int):
    fase_atual = fase_por_numero(numero)
    if fase_atual is None:
        return redirect(url_for("jogo"))
    progresso = obter_progresso()
    if numero > progresso["fase_atual"]:
        return redirect(url_for("jogo"))
    return render_template("fase.html", fase=fase_atual, progresso=progresso)


@app.route("/analisar_fase", methods=["POST"])
def analisar_fase():
    try:
        numero = int(request.form.get("fase", 1))
    except (TypeError, ValueError):
        numero = 1

    fase_atual = fase_por_numero(numero)
    if fase_atual is None:
        return redirect(url_for("jogo"))

    progresso = obter_progresso()
    arquivo = request.files.get("imagem")
    if not arquivo or not arquivo.filename or not extensao_permitida(arquivo.filename):
        return render_template(
            "resultado_fase.html", erro="Envie uma foto PNG, JPG ou WEBP da combinação.",
            fase=fase_atual, progresso=progresso, pontuacao=None, relatorio=None,
        ), 400

    caminho = salvar_upload(arquivo)
    if caminho is None:
        return render_template(
            "resultado_fase.html", erro="Falha ao salvar a imagem.",
            fase=fase_atual, progresso=progresso, pontuacao=None, relatorio=None,
        ), 500

    try:
        relatorio = processar(caminho, request.form.get("texto_manual", ""))
    except Exception as exc:  # noqa: BLE001
        logging.exception("Falha no pipeline de análise de fase (/analisar_fase)")
        return render_template(
            "resultado_fase.html", erro=f"Não foi possível analisar. Consulte os logs do servidor. ({type(exc).__name__})",
            fase=fase_atual, progresso=progresso, pontuacao=None, relatorio=None,
        ), 500

    meta = int(fase_atual["meta"])
    pontuacao = calcular_pontuacao(relatorio, meta)
    registrar_tentativa(
        numero, pontuacao["pontos"], meta,
        pontuacao["atingiu"], relatorio["imagem"], relatorio,
    )

    return render_template(
        "resultado_fase.html",
        erro=None,
        fase=fase_atual,
        progresso=obter_progresso(),
        pontuacao=pontuacao,
        relatorio=relatorio,
    )


@app.route("/perfil")
def perfil():
    progresso = obter_progresso()
    desbloqueadas = [c for c in progresso["conquistas"] if c["desbloqueada"]]
    return render_template(
        "perfil.html",
        progresso=progresso,
        jornada=jornada_recente(3),
        total_conquistas=len(desbloqueadas),
    )


@app.route("/perfil/nome", methods=["POST"])
def perfil_nome():
    nome = " ".join(request.form.get("nome", "").split())[:30]
    if nome:
        session["nome"] = nome
    else:
        session.pop("nome", None)
    session.modified = True
    return redirect(request.referrer or url_for("perfil"))


@app.route("/conquistas")
def conquistas():
    return render_template("conquistas.html", progresso=obter_progresso())


@app.route("/foto")
def foto():
    return render_template("foto.html")


@app.route("/configuracoes")
def configuracoes():
    return render_template("configuracoes.html")


@app.route("/reiniciar", methods=["POST"])
def reiniciar():
    for chave in ("fase_atual", "concluidas", "pontuacao_total", "historico",
                  "usos_foto", "usos_digital", "atividades", "nivel_visto"):
        session.pop(chave, None)
    destino = request.form.get("voltar", "")
    if destino.startswith("/") and not destino.startswith("//"):
        return redirect(destino)
    return redirect(url_for("jogo"))


@app.route("/api/analisar", methods=["POST"])
def api_analisar():
    arquivo = request.files.get("imagem")
    if not arquivo or not arquivo.filename or not extensao_permitida(arquivo.filename):
        return jsonify({"erro": "Envie uma imagem PNG/JPG/JPEG/WEBP no campo 'imagem'."}), 400

    caminho = salvar_upload(arquivo)
    if caminho is None:
        return jsonify({"erro": "Falha ao salvar a imagem."}), 500

    try:
        relatorio = processar(caminho, request.form.get("texto_manual", ""))
    except Exception as exc:  # noqa: BLE001
        return jsonify({"erro": str(exc)}), 500
    registrar_analise_livre(relatorio, "foto")
    return jsonify(relatorio)


@app.route("/fichas")
def fichas():
    return render_template("fichas.html", limites=base_conhecimento["limites"])


@app.route("/sobre")
def sobre():
    return render_template("sobre.html", metadados=base_conhecimento["metadados"])


@app.route("/uploads/<nome>")
def uploads(nome):
    return send_from_directory(str(UPLOAD_DIR), nome)


@app.errorhandler(413)
def muito_grande(_exc):
    return jsonify({"erro": "A imagem é muito grande (máximo 16 MB)."}), 413


if __name__ == "__main__":
    print("\nARborIA rodando em http://127.0.0.1:5000")
    print("   Pressione Ctrl+C para parar.\n")
    app.run(debug=False, host="0.0.0.0", port=5000)
