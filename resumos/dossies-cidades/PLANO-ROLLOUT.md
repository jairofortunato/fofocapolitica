# Plano de rollout — Fofoca Política: Transparência Radical

Objetivo: repetir o pipeline da AMREC nas outras 20 regiões de SC (291 cidades),
**uma região por vez**, com validação do Jairo entre cada uma.

Próxima região: **AMESC / Extremo Sul (Araranguá)** — 15 cidades, 2.180 casos MP + 292 TCE.

---

## O que já existe (não precisa refazer)

| Item | Estado |
|---|---|
| MDs de região MP (`resumos/regioes/regiao-*.md`) | ✅ 21 regiões |
| MDs de região TCE (`tcesc/resumos/regioes/regiao-*-tce.md`) | ✅ 21 regiões |
| Template HTML/CSS (capa, miolo, contracapa) | ✅ pronto e validado na AMREC |
| Gerador de PDF (`gen_amrec_curated.py`) | ⚠️ funciona, mas amarrado à AMREC |

## O que falta, por etapa

### Etapa 0 — Destravar a fonte de dados (decisão pendente, ver abaixo)

Os MDs de região no disco são de **12/07 11:01**; a correção de atribuição de
cidade em `build_regioes.py` é de **12/07 15:34**. Ou seja: **todos os MDs
carregam o bug** de atribuir à cidade errada quando a *comarca* judicial bate com
uma cidade vizinha maior. E `parsed/` não existe nesta máquina, então os MDs não
podem ser regerados sem re-scraping.

Medido na AMREC: a seção "Treviso" do MD tem 38 processos MP; depois de reaplicar
a atribuição correta sobram **17**. Mais da metade era caso de outra cidade que só
tramitava na comarca de Criciúma. Na AMESC o mesmo vai acontecer com as cidades
pequenas cuja comarca é Araranguá (Ermo, Morro Grande, Timbé do Sul, Maracajá...).

### Etapa 1 — Extrator de casos por cidade (código novo)

Não existe script disso — os `raw/*.json` da AMREC foram feitos ad-hoc no
scratchpad da sessão passada. Escrever `extract_city_raw.py`:
- lê a seção `## <Cidade>` do MD da região (MP e TCE)
- reaplica a regra de atribuição (menção institucional explícita > comarca)
- emite `_curated_data/raw/<slug>.json` no schema `{city, mp[], tce[]}`

### Etapa 2 — Dados por cidade

| Dado | Fonte | Observação |
|---|---|---|
| `pop` (Censo 2022) | IBGE | direto |
| `rec` / `desp` 2025 | **fonte a confirmar com o Jairo** | ver pergunta aberta |
| bandeira + brasão | Wikipédia / site da prefeitura | 2 imagens por cidade |
| `CITY_COLOR` | cor dominante da bandeira | dá pra derivar da imagem |

### Etapa 3 — Curadoria editorial (a parte cara)

Cada caso lido e reescrito por agentes Claude em paralelo: título de manchete,
descrição em linguagem simples com status, `severity`, `keep`.
Ver [[usar-julgamento-editorial-nao-regex]] — **não** fazer por regex.
AMESC: ~2.472 casos brutos a triar.

### Etapa 4 — Generalizar o gerador

- `load_curated_for_city()` hoje é um `if/elif` por lote da AMREC → trocar por
  convenção: um arquivo curado por cidade (`curated/<slug>.json`).
- Tirar o hardcode de região de 3 lugares: `build_cover_html()` (label + "12
  cidades"), `build_city_html()` (cabeçalho) e `footer_css` (rodapé de página).
- `ORDEM`, `IMGS`, `FINANCAS`, `CITY_COLOR` saem de `gen_amrec.py` e viram um
  arquivo de dados por região.

### Etapa 5 — Gerar, revisar, validar com o Jairo

---

## Decisões tomadas (19/07/2026)

1. **Fonte de dados**: seguir com os MDs atuais, reaplicando a correção de
   atribuição no extrator. Sem re-scraping por ora. Consequência aceita: parte
   dos casos mantém texto truncado com "…".
2. **Receita/despesa**: levantar do Siconfi/Tesouro Nacional, validando contra os
   valores da AMREC que já estão em `FINANCAS` antes de usar nas demais cidades.

## Validação do extrator

O extrator é conferido contra a AMREC: rodando nos MDs da AMREC, ele tem que
reproduzir os `_curated_data/raw/<slug>.json` já existentes (ex.: Treviso = 17
processos MP). Se bater, a regra de atribuição está correta e pode ser aplicada
à AMESC com confiança.
