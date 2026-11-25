# 🌍 ARborIA

> **ARborIA — Plataforma de Aprendizagem Ambiental com Inteligência Artificial**

Jogo didático sobre os 9 limites planetários com interface de IA para apoio à
aprendizagem significativa no ensino médio.

Protótipo funcional que integra **fichas físicas impressas** e **fichas digitais** a
um sistema de IA capaz de ler fotografias das combinações montadas pelos
estudantes, interpretar relações entre fichas e gerar **feedback pedagógico** —
sem entregar respostas prontas.

---

## ✅ Status atual

| Componente | Status |
|---|---|
| Documentação do projeto | ✅ Pronto |
| Conteúdo das 9 fichas (limites, problemáticas, intervenções) | ✅ Pronto |
| Regras do jogo | ✅ Pronto |
| Base de conhecimento em JSON | ✅ Pronto |
| Motor de análise (OCR + regras + grafo) | ✅ Pronto |
| Integração opcional com IA multimodal (compatível com OpenAI/Coarena) | ✅ Pronto (usa sua chave) |
| Identidade visual verde-escuro / verde-limão / azul-ciano | ✅ Pronto |
| Dashboard inicial com indicadores e cartões interativos | ✅ Pronto |
| Jogo com fichas digitais selecionáveis e animadas | ✅ Pronto |
| Assistente IA com análise por foto **e** análise digital | ✅ Pronto |
| Seção interativa com os 9 limites planetários | ✅ Pronto |
| Gamificação: trilha de 10 fases com metas 60/70/80/90 | ✅ Pronto |
| Medalhas, histórico e indicador de progresso | ✅ Pronto |
| Layout responsivo, menu inferior e acesso à câmera | ✅ Pronto |
| Fichas para impressão em HTML/PDF | ✅ Pronto |

> **Nota sobre o nome:** o nome exibido na plataforma é **ARborIA**. O repositório
> e alguns módulos internos mantêm a grafia `ARboIA` da versão anterior; a
> interface já foi unificada para `ARborIA`.

---

## 📁 Estrutura

```
ARboIA/
├── .ferramentas/               # Tesseract + idiomas por/eng (baixado, sem sudo)
├── docs/
│   ├── projeto.md              # Justificativa, objetivos, metodologia, cronograma
│   └── referencias.md          # Referências bibliography-style
├── jogo/
│   ├── fases.json              # Trilha de 10 fases e metas de pontuação
│   ├── fichas-limites.md       # Os 9 limites + problemáticas + intervenções
│   ├── regras.md               # Manual do jogo
│   └── imprimir/
│       ├── fichas.html         # Fichas prontas para imprimir
│       └── gerar_fichas.py     # Regera o HTML a partir do JSON
├── ia/
│   ├── limites.json            # Base de conhecimento estruturada
│   ├── ocr.py                  # Leitura de imagem + detecção de fichas
│   ├── analise.py              # Grafo de relações + feedback pedagógico
│   ├── pontuacao.py            # Rubrica de 0 a 100 por fase
│   ├── conquistas.py           # Medalhas e critérios de desbloqueio
│   └── ia_multimodal.py        # Integração opcional com visão multimodal
├── app/
│   ├── app.py                  # Servidor Flask e rotas
│   ├── static/
│   │   ├── estilo.css          # Identidade visual e animações leves
│   │   ├── app.js              # Fichas digitais, câmera e prévia
│   │   └── terra.svg           # Ilustração da Terra (folhas + circuitos)
│   ├── templates/
│   │   ├── base.html           # Layout compartilhado (sidebar + bottom nav)
│   │   ├── index.html          # Dashboard inicial
│   │   ├── jogar.html          # Montagem digital das combinações
│   │   ├── limites.html        # Os 9 limites (cartões interativos)
│   │   ├── ia.html             # Assistente virtual (foto + digital)
│   │   ├── progresso.html      # Pontos, medalhas e histórico
│   │   ├── jogo.html           # Painel da trilha de 10 fases
│   │   ├── fase.html           # Desafio da fase atual
│   │   ├── resultado_fase.html # Nota, meta e feedback da fase
│   │   ├── resultado.html      # Feedback da IA (foto livre)
│   │   ├── fichas.html         # Fichas para consulta/impressão
│   │   └── sobre.html          # Sobre o projeto
│   └── uploads/                # Imagens enviadas (gerado automaticamente)
├── scripts/
│   └── instalar_tesseract.sh   # Reproduz a instalação local do OCR
├── .env.example                # Modelo para configurar a chave de API
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🎨 Identidade visual e navegação

A interface usa **verde-escuro** (sustentabilidade), **verde-limão** (ações e
destaques), **azul/ciano** (tecnologia e IA) e **branco** (leitura). A ilustração
do planeta em `app/static/terra.svg` mistura folhas e circuitos.

| Página | Rota | Conteúdo |
|---|---|---|
| Início | `/` | Dashboard, boas-vindas, indicadores e cartões de funcionalidades |
| Jogar | `/jogar` | Fichas digitais (limites, problemáticas, soluções) com animação ao selecionar |
| Os 9 Limites | `/limites` | Cartões ilustrados com explicação, importância, problemas e soluções |
| Inteligência Artificial | `/ia` | Assistente com análise por fotografia e análise digital |
| Desafios | `/jogo` | Trilha de 10 fases com metas progressivas |
| Meu Progresso | `/progresso` | Pontos, medalhas, histórico e indicador de progresso |
| Sobre o Projeto | `/sobre` | Objetivos, fundamentos e ficha técnica |

**Mobile first:** menu lateral no desktop, navegação inferior no celular,
botões grandes, cartões verticais, animações leves e acesso à câmera com
autorização do navegador. O campo manual de texto continua disponível como
recurso de acessibilidade e fallback do OCR.

---

## 🚀 Instalação

### 1. Tesseract + idiomas (✅ já baixado neste projeto)

O OCR local usa o **Tesseract 5.3.4** com os pacotes `por` e `eng`.
Como não havia sudo nesta máquina, os pacotes `.deb` foram baixados e
extraídos em `.ferramentas/` — o `ia/ocr.py` detecta e configura o binário
automaticamente (inclusive `TESSDATA_PREFIX` e `LD_LIBRARY_PATH`).

Para reproduzir em outra máquina, sem sudo:

```bash
bash scripts/instalar_tesseract.sh
```

Se você tiver sudo, também pode usar a via tradicional:

```bash
sudo apt-get install -y tesseract-ocr tesseract-ocr-por tesseract-ocr-eng
```

> Se o Tesseract não estiver disponível de forma alguma, use o campo
> **Texto das fichas (opcional)** na tela de upload. Com chave de API,
> a IA multimodal lê a imagem diretamente.

### 2. Dependências Python (✅ já instaladas no perfil do usuário)

```bash
python3 -m pip install --user --break-system-packages -r requirements.txt
```

> Se preferir ambiente virtual e tiver `python3-venv`:
>
> ```bash
> python3 -m venv .venv
> source .venv/bin/activate
> python -m pip install -r requirements.txt
> ```

Depois rode com `python3 app/app.py`.

### 3. Chave de API (opcional, mas recomendada)

Você está configurando a chave — faça assim:

```bash
cp .env.example .env
nano .env
```

Edite conforme seu provedor:

```env
# OpenAI padrão
OPENAI_API_KEY=sk-proj-COLOQUE_SUA_CHAVE_AQUI
OPENAI_MODEL=gpt-4o-mini
USE_IA_MULTIMODAL=true

# Coarena (chave coa_...) — detectada automaticamente
OPENAI_API_KEY=coa_SUA_CHAVE
OPENAI_BASE_URL=https://coarena.ai/api/v1
OPENAI_MODEL=gemini-3-8-flash
USE_IA_MULTIMODAL=true
```

> ⚠️ **Nunca** commite o arquivo `.env`. Ele já está listado no `.gitignore`.

**Sem chave:** o sistema funciona 100% offline usando OCR + regras (modo local).
**Com chave:** o sistema tenta primeiro a visão multimodal e usa o modo local como fallback.
**Nesta máquina:** a chave Coarena já está configurada e validada com o modelo `gemini-3-8-flash`.

### 4. Rodar

```bash
python app/app.py
```

Acesse: **http://127.0.0.1:5000**

---

## 🎮 Como usar

1. Abra `/fichas` na aplicação (ou imprima `jogo/imprimir/fichas.html`).
2. Em grupos, os estudantes dispõem as fichas na mesa formando propostas de intervenção.
3. Fotografam a disposição com o celular.
4. Enviam a foto em `/` → **Analisar combinação**. Se a foto não for lida,
   preenchem o campo opcional **Texto das fichas** com os códigos/palavras visíveis.
5. A IA devolve:
   - limites planetários reconhecidos;
   - intervenções identificadas;
   - sinergias e conflitos entre fichas;
   - pontos fortes, lacunas e perguntas reflexivas.
6. Leem o feedback e discutem em grupo.

Também existe o endpoint JSON:

```
POST /api/analisar   (multipart/form-data, campo "imagem")
```

---

## 🎮 Trilha de gamificação (10 fases)

A plataforma agora tem uma **trilha progressiva** em `/jogo`. Cada fase exige uma
pontuação mínima para desbloquear a seguinte:

| Fase | Nome | Meta | Foco |
|---|---|---:|---|
| 01 | Primeiro Contato | 60 | Mudança climática |
| 02 | Cidade em Movimento | 60 | Clima + aerossóis/fósforo |
| 03 | Gotas que Contam | 60 | Água doce |
| 04 | Nutrientes em Excesso | 70 | Nitrogênio + fósforo |
| 05 | Fósforo Finito | 70 | Ciclo do fósforo |
| 06 | Vida que Some | 70 | Extinção + biodiversidade |
| 07 | Coração de Corais | 80 | Oceanos + clima |
| 08 | Ar que Respiramos | 80 | Aerossóis |
| 09 | Rede da Vida | 90 | Biodiversidade funcional |
| 10 | Guardiões da Terra | 90 | Limites centrais + trade-offs |

### Como a nota é calculada (0 a 100)

| Critério | Pontos máximos |
|---|---:|
| Completude: ficha azul + laranja + verde (10 cada) | 30 |
| Bônus de combinação completa (os 3 tipos presentes) | 10 |
| Conexão entre limites (10 por limite, até 3) | 30 |
| Sinergias detectadas (10 cada, até 2) | 20 |
| Trade-offs identificados (5 cada, até 2) | 10 |
| Limite central incluído (clima ou biodiversidade) | 10 |
| **Total** | **100** |

A nota **não** mede decorar a resposta certa: mede a qualidade da conexão
sistêmica. O progresso fica salvo na sessão do navegador; use `/reiniciar`
para começar de novo. Configuração em `jogo/fases.json`; cálculo em
`ia/pontuacao.py`.

---

## 🧠 Como a IA funciona

### Modo local (offline)

```
imagem → pré-processamento (OpenCV) → OCR (Tesseract)
       → normalização → casamento com a base de conhecimento (difflib + palavras-chave)
       → construção do grafo de relações → feedback pedagógico
```

### Modo multimodal (com chave)

```
imagem → GPT-4o Vision (prompt pedagógico estruturado)
       → JSON com limites, intervenções, relações e análise
       → renderização do feedback
```

Se a chamada falhar (sem internet, cota, erro), o sistema **cai automaticamente** para o modo local e avisa na interface.

---

## 📚 Base teórica

- **Aprendizagem significativa** — David Ausubel / Joseph Novak
- **Metodologias ativas** — Paulo Freire, Celso de Moraes Kaplun, Silvio Gabarda
- **Limites planetários** — Rockström et al. (2009); Steffen et al. (2015)
- **Educação ambiental** — Lei 9.795/1999 (Brasil); UNESCO

Ver `docs/projeto.md` e `docs/referencias.md`.

---

## 🔧 Próximos passos (sugestões)

- [ ] Testes com fotos reais de fichas em sala de aula
- [ ] Ajuste do OCR para fonts manuscritas
- [ ] Versão mobile (PWA) para fotografia direta
- [ ] Exportar relatório da análise em PDF para o professor
- [ ] Painel do professor com histórico de turmas

---

Feito com 🌱 para o ensino médio.

## Atualização visual da interface

A interface recebeu uma reformulação com foco em dispositivos móveis:

- Página inicial reorganizada em apresentação, resumo da jornada e cartões de acesso rápido.
- Paleta verde-floresta e verde-claro com contraste mais suave e menos efeitos neon.
- Cartões, botões, campos e navegação inferior padronizados.
- Layout adaptável para celular, tablet e telas maiores.
- Atalho dedicado para enviar uma fotografia das fichas físicas.

As rotas Flask, os templates das demais telas, o sistema de análise, as fichas, a pontuação e as conquistas foram preservados. Para aplicar a atualização, substitua os arquivos do projeto pelos desta versão e mantenha suas variáveis locais no arquivo `.env` (ele não é incluído no pacote por segurança; use `.env.example` como referência).

## Fluxo principal atualizado — tabuleiro físico + IA

1. O botão **Jogar** (na página inicial e na navegação) abre `/jogo`, a **Trilha de Desafios**.
2. O estudante escolhe a fase liberada e lê o desafio e a dica pedagógica.
3. A montagem acontece no **tabuleiro físico**, com as fichas reais de limite planetário, problemática e solução.
4. Na tela da fase, o estudante fotografa o tabuleiro pelo celular ou escolhe uma imagem da galeria. O campo “Texto das fichas” é opcional e pode complementar a leitura.
5. A plataforma envia a imagem para o pipeline de IA/OCR, apresenta a análise e calcula a pontuação da fase conforme a rubrica.
6. Ao atingir a meta, a fase seguinte é desbloqueada. Caso contrário, o estudante recebe o retorno e pode reorganizar as fichas e tentar novamente.

A rota antiga `/jogar` redireciona para `/jogo`, para que qualquer acesso ao botão **Jogar** comece pela trilha. A análise digital de fichas continua no código como funcionalidade auxiliar, mas o percurso principal foi orientado ao tabuleiro físico.
