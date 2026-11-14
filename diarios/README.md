# diarios: coletor de diários oficiais por cidade

Junta, para uma cidade, o que saiu em todos os diários e fontes públicas numa janela de datas.

```
python3 -I diarios/coletar.py criciuma                 # últimos 7 dias, todas as fontes
python3 -I diarios/coletar.py criciuma --dias 30
python3 -I diarios/coletar.py criciuma --fontes dou,doe,djen
python3 -I diarios/coletar.py icara --inicio 2026-10-01 --fim 2026-10-31
```

Saída: `diarios/dados/<cidade>/<data-fim>/` com um `<fonte>.json` por fonte e um `resumo.md`.
PDFs e ZIPs ficam em `diarios/cache/` (fora do git) e não são baixados de novo.
Usa só a biblioteca padrão do Python e o `pdftotext`.

## Fontes

| Fonte | O que pega | Como |
|---|---|---|
| `municipal` | diário do município | Criciúma: PDF diário em `criciuma.sc.gov.br/does.php`. Demais cidades: DOM/SC pelos dados abertos do CIGA (`dados.ciga.sc.gov.br`), filtrando o campo município |
| `doe` | DOE-SC, matérias que citam a cidade | API da busca do portal DOE (`/apis/busca-materia`). `da_prefeitura` marca o que a própria prefeitura publicou |
| `dou` | DOU, atos que citam a cidade | busca do in.gov.br |
| `djen` | TJSC, comunicações em que o município é parte | API pública do DJEN/CNJ (`comunicaapi.pje.jus.br`). Execução fiscal e afins ficam marcadas como `rotina`; improbidade, ACP, ação popular, MS e penal como `destaque` |
| `pncp` | compras de órgãos sediados na cidade (todas as esferas) | API de consulta do PNCP por código IBGE, as 13 modalidades |
| `mpsc` | trechos do diário do MPSC que citam a cidade | mesmo índice do `../download_pdfs.sh`; descarta escalas e listas de lotação |
| `tcesc` | trechos do DOTC-e que citam a cidade | mesmo padrão de URL do `../tcesc/download_pdfs.sh` |

## Trocar ou adicionar cidade

Editar `cidades.json`:

- `ibge`: código IBGE (usado no PNCP).
- `termos`: como a cidade aparece no texto (busca sem acento e por palavra inteira).
- `partes_djen`: nome da parte no TJSC, normalmente `MUNICÍPIO DE <NOME>`.
- `diario_municipal`: `{"tipo": "domsc", "municipio": "<nome exato no DOM/SC>"}` na maioria das cidades de SC. Criciúma não publica no DOM/SC e tem diário próprio (`"tipo": "criciuma"`).

## Limites conhecidos

- A busca por nome pega homônimos e menções laterais (endereço, comarca, naturalidade). O resumo é pauta bruta: confira na fonte.
- O `total` da busca do DOE conta registros repetidos; o número que vale é o de itens únicos.
- O PNCP limita requisições (429); o coletor espera e tenta de novo.
- Ainda não entram: diário da ALESC e da Câmara de Vereadores (a de Criciúma publica compras no PNCP, que já entra).
