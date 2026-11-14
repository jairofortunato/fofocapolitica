# Prompt de continuação — pipeline "Fofoca Política: Transparência Radical"

Cole o bloco abaixo inteiro no outro modelo. Ele já contém o teste de aferição.

---

Você vai continuar um pipeline de jornalismo de dados que já está rodando. Leia
tudo antes de agir. O diretório de trabalho é `/Users/jairofortunato/mp`.

## O produto

"Fofoca Política: Transparência Radical" é um dossiê em PDF **por cidade** que
expõe, em linguagem de jornal, o que o Ministério Público (MPSC) e o Tribunal de
Contas (TCE-SC) apuram sobre a prefeitura e a câmara daquela cidade. Santa
Catarina tem 21 regiões (associações de municípios) e 303 cidades. Cinco regiões
já estão prontas e publicadas em `resumos/dossies-cidades/`: AMREC, AMESC,
AMUREL, AMURES e AMVALI — 70 cidades, 70 PDFs.

A região em andamento é a **AMMVI** (Médio Vale do Itajaí, 14 cidades) — **concluída** (14 PDFs, 1.346 casos publicados de 2.902 brutos). Depois
dela faltam 15 regiões.

## A regra que manda em tudo

**Cada caso é lido e reescrito por um modelo, nunca por regex ou palavra-chave.**
Isso não é preferência de estilo — é o requisito central do projeto. Toda vez que
alguém tentou resolver por filtro de texto o que exigia leitura, saiu conteúdo
errado sobre pessoas reais: já houve 287 cards afirmando condenações sem fonte, e
um conselheiro do TCE descrito como se tivesse sido multado pelo próprio tribunal
em que julga. Se você se pegar escrevendo um regex para decidir se um caso entra
no dossiê, ou qual o desfecho dele, pare: essa é a decisão que exige leitura.

Regex é legítimo para tarefas mecânicas (validar alinhamento, contar arquivos,
achar duplicatas óbvias). Não para julgar conteúdo.

## Arquitetura

Tudo em `pdf_template/`:

| arquivo | função |
|---|---|
| `CURADORIA.md` | **critério editorial — leia antes de curar qualquer coisa** |
| `regiao_config.py` | sigla/nome/label/ordem/cores/finanças de cada região |
| `extract_city_raw.py` | extrai os casos de cada cidade a partir dos MDs de região |
| `enrich_tce.py` | anexa o dispositivo das decisões aos casos do TCE |
| `make_batches.py` | quebra os casos em lotes de 70 para a curadoria |
| `assemble_curated.py` | remonta os lotes curados em um arquivo por cidade |
| `check_conselheiros.py` | trava: conselheiro do TCE citado como investigado |
| `gen_cores.py` | cor de destaque por cidade, a partir da bandeira |
| `dl_assets.py` | baixa bandeira e brasão da Wikipédia |
| `gen_dossie.py` | gera os PDFs |

Dados por região ficam em `pdf_template/<sigla>/`: `financas.json`, `cores.json`,
`assets/cidades/`, `_curated_data/raw/`, `_lotes/`, `_lotes_curados/`,
`_curated_data/curated/`.

## A convenção crítica: alinhamento posicional

A curadoria casa com o caso bruto **por posição**. O arquivo curado tem que ter
exatamente o mesmo tamanho, na mesma ordem, com os mesmos `i` e `tipo` da
entrada. Nunca reordene, omita ou acrescente item. Um deslocamento de um índice
faz o PDF publicar a descrição de um caso sob o número de processo de outro —
ou seja, atribui a conduta de um investigado a outra pessoa.

Por isso também: **nunca re-extraia o bruto de uma cidade cuja curadoria já
existe.** Re-extrair muda contagem e ordem e invalida todo o trabalho editorial.
`enrich_tce.py` enriquece justamente para não precisar re-extrair.

## Onde o trabalho está agora

AMMVI concluída: 47 lotes curados, 14 dossiês em `resumos/dossies-cidades/AMMVI/`
(1.346 publicados / 2.902 brutos, 46% de aproveitamento, 164 graves).
Base: finanças (13/14 — Timbó sem RREO desde 2023), 28 imagens, `cores.json`.

## SEU PRIMEIRO PASSO: o teste

Antes de tocar em qualquer outro lote, faça só isto:

1. Leia `pdf_template/CURADORIA.md` inteiro.
2. Leia um lote já curado por outro modelo, para calibrar o padrão — compare
   `pdf_template/ammvi/_lotes/blumenau__0.json` (entrada) com
   `pdf_template/ammvi/_lotes_curados/blumenau__0.json` (saída aprovada).
3. Cure **apenas** `pdf_template/ammvi/_lotes/rodeio__0.json` (41 casos, cidade
   pequena) e grave em `pdf_template/ammvi/_lotes_curados/rodeio__0.json`.
4. Rode a validação e me mostre a saída:

```bash
cd /Users/jairofortunato/mp/pdf_template && python3 - <<'PY'
import json
b=json.load(open('ammvi/_lotes/rodeio__0.json'))['casos']
c=json.load(open('ammvi/_lotes_curados/rodeio__0.json'))
assert len(b)==len(c), f'TAMANHO {len(c)} vs {len(b)}'
for x,y in zip(b,c):
    assert x['i']==y['i'] and x['tipo']==y['tipo'], f"DESALINHADO i={x['i']}"
sem=[y['i'] for y in c if y.get('keep') and not y.get('status','').strip()]
assert not sem, f'keep sem status: {sem}'
keep=[y for y in c if y.get('keep')]
print(f"OK — {len(c)} casos, {len(keep)} publicados, {sum(1 for y in keep if y['severity']=='alta')} graves")
for y in keep[:5]: print(' •', y['status'], '|', y['title'])
PY
```

5. **Pare e me mostre o resultado.** Não siga para os outros lotes antes de eu
   conferir. Quero ver os títulos, não só os números.

## Curadoria (após aprovação do teste)

Cure os lotes restantes da região, em levas de agentes paralelos (2–3 lotes por
agente). Regras de operação aprendidas na marra:

- **Grave cada lote assim que terminar**, antes de começar o próximo. A sessão
  cai por limite de uso com frequência, e o que não foi gravado se perde. Com
  gravação incremental, retomar é trivial: basta re-disparar os lotes que não têm
  arquivo em `_lotes_curados/`.
- Lotes de 70 casos, no máximo. Poucos arquivos por agente.
- Não rode mais de ~8 agentes ao mesmo tempo.
- Se o `assemble_curated.py` acusar `tipo: None` em itens curados, o agente
  omitiu o campo `tipo`. Corrija copiando do bruto (alinhamento posicional).

Quando todos os lotes estiverem prontos:

```bash
cd /Users/jairofortunato/mp/pdf_template
python3 assemble_curated.py ammvi --lotes ammvi/_lotes_curados   # valida alinhamento
python3 check_conselheiros.py ammvi                              # trava de segurança
python3 gen_dossie.py ammvi                                      # gera os 14 PDFs
```

Se `assemble_curated.py` acusar buraco, **não improvise**: o lote correspondente
foi gravado incompleto e precisa ser recurado.

## Para abrir uma região nova (as 15 restantes)

Ordem exata:

```bash
# 1. população IBGE Censo 2022 (agregado 4714, variável 93) e finanças
#    Siconfi RREO 2025 6º bimestre, Anexo 01:
#      rec  = TotalReceitas,  coluna "Até o Bimestre (c)"
#      desp = TotalDespesas,  coluna "DESPESAS EMPENHADAS ATÉ O BIMESTRE (f)"
#    NUNCA usar a receita bruta do DCA: é ~6% maior e infla a cidade na comparação.
#    Cidade sem RREO fica com null e a lacuna vai documentada em "_lacunas".
#    -> escrever pdf_template/<sigla>/financas.json
# 2. acrescentar o bloco da região em regiao_config.py (ordem = maiores primeiro)
python3 dl_assets.py <sigla>          # bandeiras e brasões
python3 gen_cores.py <sigla>          # cores com contraste WCAG
python3 extract_city_raw.py <sigla> --out <sigla>/_curated_data/raw
python3 enrich_tce.py <sigla>         # SEMPRE antes de make_batches
python3 make_batches.py <sigla> --out <sigla>/_lotes --tamanho 70
# então a curadoria, e depois assemble -> check -> gen_dossie
```

`enrich_tce.py` antes de `make_batches.py` não é detalhe: sem o dispositivo da
decisão no lote, o curador julga o TCE às cegas e inventa desfecho. Foi assim que
saíram os 287 cards com condenação sem fonte.

## Armadilhas já mapeadas

- O campo `status` do dado bruto vem de um classificador por palavra-chave e
  **erra muito**. Há casos rotulados "ACP ajuizada" cujo texto diz que o processo
  foi arquivado sem responsabilizar ninguém. Quando o rótulo contradiz o texto, o
  texto vence — sempre.
- O Diário republica a mesma decisão várias vezes, em datas diferentes. Mantenha
  uma ocorrência e corte as repetições, senão o dossiê fica com cards idênticos.
- O parser do TCE às vezes cola no caso o dispositivo de um processo de outro
  município. Se o dispositivo fala de outra cidade, corte — não publique a
  rejeição de contas de Garopaba num card de Guaramirim.
- Chrome headless: **não** passe `--user-data-dir` nas chamadas de print-to-pdf.
  Um profile novo dispara o "first run" do Chrome e o processo trava com o PDF já
  escrito. `gen_dossie.py` já tem timeout e retry por causa disso.
- Imagens da Wikipédia: `dl_assets.py` já resolve o rate limit (usa `curl`, não
  `urllib`), o comentário HTML colado no parâmetro da infobox, o GIF servido com
  nome de PNG e o redimensionamento para 1000px. Bandeira gigante já gerou PDF de
  13 MB.

## O que é inegociável

É um documento público que nomeia pessoas reais. Descrever como condenado alguém
que foi absolvido, ou como desvio o que foi arquivado, é o erro mais grave
possível aqui. Na dúvida sobre o desfecho, descreva o que consta e diga que o
desfecho não está claro — os selos `❔` existem exatamente para isso. Caso
arquivado por falta de provas nunca é `severity: alta`: a pessoa não foi
responsabilizada.
