# ARborIA — Projeto de pesquisa e desenvolvimento

## Plataforma de aprendizagem ambiental com inteligência artificial sobre os 9 limites planetários

---

## Resumo

O presente projeto tem como objetivo desenvolver e prototipar o jogo didático **ARboIA**, estruturado a partir do conceito dos nove limites planetários e integrado a um sistema de inteligência artificial capaz de interpretar combinações de soluções socioambientais propostas por estudantes do ensino médio. A proposta fundamenta-se nos princípios de aprendizagem significativa, interdisciplinaridade e metodologias ativas, buscando ampliar as possibilidades pedagógicas para o ensino de temas socioambientais complexos no contexto escolar.

O projeto prevê a elaboração da estrutura do jogo, composto por fichas que representam limites planetários, problemáticas associadas e propostas de intervenção, organizadas em uma dinâmica colaborativa de análise e tomada de decisões. Paralelamente, desenvolve-se um sistema de inteligência artificial voltado à leitura de imagens das combinações de fichas organizadas pelos estudantes durante o jogo, permitindo interpretar as relações estabelecidas entre os elementos e gerar análises sobre as soluções apresentadas.

A integração entre o jogo didático físico e o sistema inteligente busca contribuir para processos de aprendizagem mais interativos e reflexivos, estimulando o pensamento crítico sobre desafios socioambientais contemporâneos. Como resultado, espera-se um protótipo funcional do jogo ARboIA associado a um sistema inicial de IA capaz de apoiar a análise das propostas elaboradas pelos estudantes.

**Palavras-chave:** limites planetários; educação ambiental; aprendizagem significativa; metodologias ativas; inteligência artificial; ensino médio.

---

## 1. Introdução

A crise socioambiental contemporânea é caracterizada pela interdependência entre sistemas naturais e sociais. Problemas como mudanças climáticas, perda de biodiversidade, poluição e escassez de água não podem ser compreendidos de forma isolada, pois se articulam em redes de causalidade que transcendem as fronteiras disciplinares tradicionais (Steffen et al., 2015).

No contexto do ensino médio brasileiro, esses temas aparecem de maneira fragmentada em componentes curriculares como Biologia, Geografia, Química, Física e Ciências Humanas. A Base Nacional Comum Curricular (BNCC) propõe a abordagem de temas contemporâneos transversais e o desenvolvimento de competências gerais como "compreender, utilizar e criar tecnologias digitais" e "exercitar a curiosidade intelectual e recorrer à abordagem própria das ciências" (Brasil, 2018). No entanto, a tradução dessas orientações em práticas pedagógicas efetivas ainda é um desafio.

A inteligência artificial, quando integrada de forma intencional ao processo de ensino-aprendizagem, pode atuar como um **ampliador da mediação pedagógica**, e não como substituto do professor. No caso do ARboIA, a IA não entrega a "resposta correta": ela devolve perguntas, relações e lacunas que estimulam a reflexão dos estudantes sobre as próprias decisões tomadas durante o jogo.

---

## 2. Referencial teórico

### 2.1 Aprendizagem significativa

A teoria da aprendizagem significativa de David Ausubel (1968) postula que a aquisição de novos conhecimentos depende da existência de estruturas cognitivas prévias adequadas — os "conceitos âncora". Joseph Novak (1977) desenvolveu essa ideia por meio dos **mapas conceituais**, nos quais as relações entre conceitos são tão importantes quanto os conceitos em si.

No ARboIA, as fichas funcionam como conceitos âncora. A ação de **organizá-las e relacioná-las** na mesa é, ela própria, um exercício de construção de mapas conceituais. A IA, ao detectar e nomear essas relações, torna explícita a estrutura cognitiva que os estudantes estão construindo.

### 2.2 Metodologias ativas

Metodologias ativas deslocam o eixo do processo de ensino do professor para o estudante, que passa a ser protagonista na construção do conhecimento (Kaplun, 1998; Freire, 1996). O jogo didático é uma dessas metodologias: ele introduz regras, desafios, cooperação e feedback imediato.

O ARboIA combine três mecanismos ativos:

| Mecanismo | Como aparece no jogo |
|---|---|
| Aprendizagem baseada em problemas | Cada rodada apresenta uma problemática real associada a um limite |
| Aprendizagem colaborativa | Grupos decidem juntos quais fichas combinar |
| Gamificação leve | Pontos por sinergia identificada, não por "acerto" |

### 2.3 Limites planetários

O modelo dos limites planetários foi proposto por Rockström et al. (2009) e posteriormente atualizado por Steffen et al. (2015). Ele define nove processos biofísicos que regulam a estabilidade do sistema Terra, cada um com uma variável de controle e limiares estimados. O modelo diferencia:

- **Zona segura** — operação dentro de limites seguros;
- **Zona de incerteza** — risco crescente, conhecimento incompleto;
- **Zona de risco** — possibilidade de mudanças abruptas e irreversíveis.

Steffen et al. (2015) destacam ainda dois **limites centrais** (*core boundaries*): mudança climática e perda de biodiversidade funcional, cuja transgressão pode desestabilizar todo o sistema.

Este projeto adota a versão de 2015 (nove limites), por ser a mais difundida em materiais educacionais atuais.

### 2.4 Inteligência artificial na educação

A USEB (UNESCO, 2021) orienta que a IA na educação deve ser implantada com foco no desenvolvimento humano, inclusão e transparência. No ARboIA, isso se traduz em três princípios:

1. **Explicabilidade** — toda análise gerada é acompanhada das fichas e regras que a sustentam;
2. **Privacidade** — as imagens são processadas localmente sempre que possível;
3. **Mediação, não substituição** — o feedback da IA é insumo para a conversa em sala, não nota final.

---

## 3. Objetivos

### 3.1 Objetivo geral

Desenvolver e prototipar o jogo didático ARboIA, integrando fichas sobre os nove limites planetários a um sistema de inteligência artificial capaz de interpretar combinações propostas por estudantes e gerar analyses que apoiem a aprendizagem significativa em temas socioambientais no ensino médio.

### 3.2 Objetivos específicos

1. Mapear os nove limites planetários e suas variáveis de controle em uma base de conhecimento estruturada.
2. Elaborar fichas didáticas contendo problemáticas reais e propostas de intervenção interdisciplinares.
3. Definir regras de uma dinâmica colaborativa de análise e tomada de decisão.
4. Implementar um sistema de leitura de imagens que identifique fichas e suas relações espaciais.
5. Desenvolver um mecanismo de análise que produza feedback pedagógico: sinergias, conflitos, lacunas e perguntas reflexivas.
6. Integrar tudo em uma aplicação web acessível a professores e estudantes.
7. Avaliar o protótipo em condições reais de sala de aula (etapa subsequente).

---

## 4. Metodologia

### 4.1 Tipo de pesquisa

Trata-se de uma pesquisa aplicada, de caráter qualitativo e exploratório, com abordagem de **design-based research** (Design-Based Research Collective, 2003): o produto é desenvolvido em ciclos iterativos de concepção, aplicação e refinamento.

### 4.2 Etapas

| Etapa | Atividade | Produto |
|---|---|---|
| 1 | Revisão bibliográfica sobre limites planetários e aprendizagem significativa | Referencial teórico |
| 2 | Estruturação da base de conhecimento | `ia/limites.json` |
| 3 | Elaboração das fichas e regras | `jogo/` |
| 4 | Implementação do módulo de visão computacional | `ia/ocr.py` |
| 5 | Implementação do analisador pedagógico | `ia/analise.py` |
| 6 | Integração com IA multimodal (opcional) | `ia/ia_multimodal.py` |
| 7 | Construção da interface web | `app/` |
| 8 | Testes internos e ajustes | Protótipo funcional |
| 9 | Aplicação em sala e coleta de dados | Etapa futura |

### 4.3 Público-alvo

Estudantes do ensino médio (15 a 18 anos), preferencialmente em grupos de 3 a 5 participantes, mediados por um professor da área de Ciências Humanas ou Natureza.

---

## 5. Estrutura do jogo

O jogo é composto por três tipos de fichas:

| Tipo | Cor sugerida | Função | Quantidade |
|---|---|---|---|
| **Limite planetário** | Azul | Define o sistema em discussão | 9 |
| **Problemática** | Laranja | Apresenta um cenário-problema real | 27 (3 por limite) |
| **Intervenção** | Verde | Propõe uma ação socioambiental | 27 (3 por limite) |

### 5.1 Dinâmica resumida

1. **Aquecimento (10 min):** o professor apresenta um limite central e uma problemática.
2. **Montagem (20 min):** os grupos combinam fichas de limites, problemáticas e intervenções sobre a mesa.
3. **Registro (2 min):** foto da combinação.
4. **Análise da IA (1 min):** upload e geração do feedback.
5. **Discussão (15 min):** os grupos comparam suas combinações e respondem às perguntas reflexivas.

### 5.2 Exemplo de combinação

```
[Mudança climática] + [Aumento de emissões por transporte urbano]
        + [Mobilidade elétrica e transporte coletivo]
        + [Mudança no uso do solo] + [Perda de biodiversidade]

→ Sinergia: a eletrificação da frota reduz emissões, mas pode aumentar
  a demanda por lítio, afetando o ciclo do fósforo e a biodiversidade.
  A IA destaca esse trade-off e pergunta: como mitigar esse efeito colateral?
```

### 5.3 Plataforma digital

Além das fichas impressas, a plataforma oferece um ambiente digital com:

- **Dashboard:** boas-vindas, indicadores de progresso e cartões de funcionalidades;
- **Jogar:** 63 fichas digitais selecionáveis por toque, com animação de seleção;
- **Os 9 limites:** cartões interativos com explicação científica simplificada,
  importância, problemas e soluções;
- **Assistente ARborIA:** duas formas de interação — análise por fotografia
  (com acesso à câmera no celular) e análise digital das fichas selecionadas;
- **Desafios:** trilha de 10 fases com metas de 60, 70, 80 e 90 pontos;
- **Meu Progresso:** pontuação acumulada, medalhas, histórico de partidas e
  indicador de progresso.

A identidade visual combina verde-escuro (sustentabilidade), verde-limão
(ações e destaques), azul/ciano (tecnologia e IA) e branco (leitura). A
ilustração do planeta mistura folhas e circuitos, reforçando a união entre
natureza e inteligência artificial. O layout é mobile first: menu inferior no
celular e painel lateral no computador.

---

## 6. Sistema de inteligência artificial

### 6.1 Arquitetura

```
                    ┌──────────────────────┐
                    │  Foto das fichas     │
                    └──────────┬───────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
      ┌───────▼───────┐                 ┌───────▼────────┐
      │ Modo local    │                 │ Modo multimodal│
      │ OpenCV + OCR  │                 │ GPT-4o Vision  │
      │ + regras      │                 │ (com chave API)│
      └───────┬───────┘                 └───────┬────────┘
              └────────────────┬────────────────┘
                               │
                    ┌──────────▼───────────┐
                    │ Analisador pedagógico│
                    │ grafo + feedback     │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │ Interface web        │
                    └──────────────────────┘
```

### 6.2 Leitura de imagem

O módulo `ocr.py` realiza:

1. Redimensionamento e conversão para escala de cinza;
2. Limiarização adaptativa (OpenCV);
3. Extração de texto (Tesseract, idiomas `por+eng`);
4. Detecção de retângulos (contornos) para estimar quantas fichas estão presentes;
5. Cálculo de relações espaciais simples (esquerda/direita/acima/abaixo).

### 6.3 Interpretação e feedback

O módulo `analise.py`:

1. Normaliza o texto extraído (minúsculas, sem acentos);
2. Compara com a base de conhecimento usando similaridade de sequência (`difflib`) e palavras-chave;
3. Monta um grafo de relações entre limites e intervenções;
4. Consulta tabelas de **sinergias** e **trade-offs**;
5. Gera um relatório com:
   - fichas reconhecidas;
   - limites abordados e ausentes;
   - sinergias detectadas;
   - conflitos detectados;
   - pontos fortes;
   - sugestões de melhoria;
   - perguntas reflexivas.

### 6.4 IA multimodal (quando a chave está disponível)

O módulo `ia_multimodal.py` envia a imagem diretamente ao modelo com um prompt que solicita um JSON estruturado. Isso aumenta a precisão na leitura de fichas manuscritas ou dobradas. A chamada é opcional e falha de forma graciosa para o modo local.

### 6.5 Gamificação e avaliação

A nota de 0 a 100 é calculada em `ia/pontuacao.py` a partir de cinco critérios:
completude das fichas (30), bônus de combinação completa (10), conexão entre
limites (30), sinergias (20), efeitos colaterais (10) e presença de limite
central (10). A trilha progressiva (`jogo/fases.json`) exige metas crescentes:

| Fases | Meta |
|---|---:|
| 1–3 | 60 |
| 4–6 | 70 |
| 7–8 | 80 |
| 9–10 | 90 |

O módulo `ia/conquistas.py` converte o histórico em medalhas (Primeiro Passo,
Conector de Sistemas, Sinergista, Equilibrista, Explorador, Olhar Atento, Mente
Digital, Combinação Perfeita e Guardião da Terra). O progresso é salvo na sessão
do navegador; o ranking entre participantes pode ser habilitado pelo professor
em etapa posterior.

---

## 7. Resultados esperados

Ao final, espera-se:

- protótipo funcional do jogo ARboIA com 9 fichas de limites, 27 problemáticas e 27 intervenções;
- aplicação web que aceita fotos e devolve análise em menos de 5 segundos no modo local;
- sistema de IA capaz de reconhecer ao menos 70% das fichas em condições normais de iluminação;
- feedback pedagógico que estimule discussão, sem apresentar respostas definitivas;
- documentação completa para replicação em outras escolas.

---

## 8. Cronograma (sugerido)

| Semana | Atividade |
|---|---|
| 1 | Revisão bibliográfica e definição do referencial |
| 2 | Estruturação da base de conhecimento e fichas |
| 3 | Implementação do OCR e do analisador |
| 4 | Integração com IA multimodal e interface web |
| 5 | Testes internos com fotos simuladas |
| 6 | Ajustes e documentação final |
| 7 | Aplicação piloto em sala de aula |
| 8 | Análise dos dados e artigo de divulgação |

---

## 9. Referências

Ver `docs/referencias.md`.

---

## 10. Considerações finais

O ARboIA não propõe usar IA para "resolver" a crise ambiental, mas para **tornar visíveis as conexões** que os estudantes já percebem intuitivamente. Ao transformar uma disposição de fichas em um objeto de análise, o jogo cria uma ponte entre o concreto (a mesa, o papel, a mão) e o abstrato (sistemas biofísicos globais) — exatamente o tipo de mediação que a aprendizagem significativa demanda.
