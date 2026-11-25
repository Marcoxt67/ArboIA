# 🎮 Regras do ARboIA

### Jogo didático colaborativo sobre os 9 limites planetários

---

## 1. Objetivo do jogo

Construir, em grupo, **combinações coerentes de fichas** que representem uma proposta de intervenção socioambiental. Não existe uma únicaresposta correta: o objetivo é **tornar explícitas as relações** entre limites, problemáticas e soluções — e descobrir efeitos colaterais que passaram despercebidos.

> 🧠 O ARboIA é um jogo de **pensamento sistêmico**, não de memorização.

---

## 2. Participantes e tempo

| Item | Recomendação |
|---|---|
| Público | Ensino médio (15–18 anos) |
| Grupos | 3 a 5 estudantes |
| Duração total | 45 a 90 minutos |
| Mediação | 1 professor(a) por turma |
| Material por grupo | 9 fichas azuis + 27 laranjas + 27 verdes (ou um baralho compartilhado) |

---

## 3. Tipos de ficha

| Cor | Tipo | O que faz | Exemplo |
|---|---|---|---|
| 🔵 Azul | **Limite planetário** | Define o sistema biofísico em foco | Mudança climática |
| 🟠 Laranja | **Problemática** | Traz um cenário real a ser enfrentado | "Emissões do transporte crescem 4% ao ano" |
| 🟢 Verde | **Intervenção** | Propõe uma ação possível | "Eletrificação da frota de ônibus" |

Cada ficha traz ainda:
- um **código** (ex.: I1.1) usado pela IA;
- uma **palavra-chave** para leitura por OCR;
- uma **dica de conexão** no rodapé.

---

## 4. Preparação (professor)

1. Imprima e recorte as fichas (`jogo/imprimir/fichas.html`).
2. Separe 3 baralhos por mesa (ou um baralho central).
3. Escolha o **limite central** da rodada — sugere-se começar por **Mudança climática** ou **Perda de biodiversidade funcional** (limites centrais).
4. Explique: *"Vocês não vão acertar ou errar. Vão construir uma hipótese e deixar a IA mostrar o que estamos deixando de ver."*

---

## 5. Rodada padrão (passo a passo)

### Etapa 1 — Aquecimento (10 min)
O professor apresenta o limite central e lê em voz alta uma problemática.

### Etapa 2 — Montagem (20 min)
Cada grupo dispõe as fichas sobre a mesa seguindo esta regra mínima:

```
[LIMITE]  +  [PROBLEMÁTICA]  →  [INTERVENÇÃO]  →  [LIMITE AFETADO]
```

Exemplo：

```
[Mudança climática] + [P1.1 Transporte urbano]
        → [I1.1 Ônibus elétricos]
        → [Fósforo]  ← efeito colateral da demanda por lítio
```

**Regras de ouro da montagem:**
- Use **pelo menos 1 ficha de cada cor**.
- Tente conectar **pelo menos 2 limites planetários**.
- Deixe as fichas ** espaçadas e legíveis** — a IA vai fotografar.
- Se perceber um efeito colateral, coloque a ficha afetada **ao lado da intervenção**.

### Etapa 3 — Registro (2 min)
Um integrante fotografa a combinação com o celular, enquadrando todas as fichas.

### Etapa 4 — Análise da IA (1–3 min)
1. Acesse `http://127.0.0.1:5000`
2. Envie a foto em **Analisar combinação**
3. Leia o feedback em voz alta no grupo

### Etapa 5 — Discussão (15 min)
Cada grupo responde:
- Qual conexão nossa a IA reconheceu?
- Qual conexão nós esperávamos que fosse reconhecida e não foi?
- Qual *trade-off* apareceu e como poderíamos mitigá-lo?
- Se tivéssemos mais uma ficha, qual seria?

### Etapa 6 — Rodada extra (opcional)
Troque o limite central e repita. Ao final, compare as combinações das duas rodadas.

---

## 6. Pontuação (leve, opcional)

Não pontue "acerto". Pontue **qualidade da reflexão**:

| Critério | Pontos |
|---|---|
| Pelo menos 2 limites conectados | +1 |
| Sinergia detectada pela IA | +1 |
| Trade-off identificado pelo grupo | +2 |
| Pergunta reflexiva bem formulada | +2 |
| Intervenção que contempla justiça social | +1 |

> 🏆 O prêmio simbólico: **"Guardiã da Interconexão"** para o grupo que encontrar o efeito colateral mais surpreendente.

---

## 7. Papéis na mesa

Roteiro para grupos de 4:

| Papel | Responsabilidade |
|---|---|
| 🔵 Guardião do limite | Escolhe e lê a ficha azul central |
| 🟠 Detetive do problema | Seleciona a problemática e justifica |
| 🟢 Arquiteto da solução | Escolhe a intervenção e explica |
| 📷 Registrador | organiza a mesa, fotografa e envia à IA |

*Rotacione os papéis a cada rodada.*

---

## 8. Dicas para uma boa foto (importante para a IA)

✅ **Fazer:**
- Luz natural ou boa iluminação
- Fichas planas, sem sobreposição
- Texto voltado para a câmera
- Enquadramento firme (sem tremor)

❌ **Evitar:**
- Sombras fortes sobre o texto
- Fichas dobradas ou viradas
- Muitas fichas amontoadas
- Escrever por cima do código da ficha

> Se a IA não reconhecer uma ficha, isso também é pedagogicalamente útil: discutam **por que o sistema não viu o que vocês viam**.

---

## 9. Variações

### 9.1 Modo "Limite central sorteado"
Sorteie um dos dois limites centrais no início. Toda a rodada gira em torno dele.

### 9.2 Modo "Conflito"
O professor entrega uma problemática e **proíbe** a intervenção óbvia. O grupo precisa encontrar uma alternativa menos direta.

### 9.3 Modo "Jogo de papéis"
Cada estudante recebe um limite planetário e deve defender que sua ficha seja incluída na combinação final.

### 9.4 Modo "Sem fichas verdes"
Os grupos montam apenas limite + problemática e a IA sugere intervenções possíveis a partir da base.

---

## 10. Como a IA pontua (na verdade, como ela devolve)

O sistema devolve um relatório com:

| Seção | O que contém |
|---|---|
| 🎯 Fichas reconhecidas | O que a IA conseguiu ler |
| 🌍 Limites abordados | Quais dos 9 apareceram |
| 🔗 Sinergias | Conexões positivas entre fichas |
| ⚠️ Trade-offs | Efeitos colaterais identificados |
| 💪 Pontos fortes | O que a combinação fez bem |
| 🔍 Lacunas | Limites não contemplados |
| ❓ Perguntas reflexivas | Provocações para a discussão |

> O relatório **nunca dá a resposta final**. Ele devolve perguntas — porque o objetivo é aprendizagem significativa, não apenas acerto.

---

*Boa jogada! 🌱*
