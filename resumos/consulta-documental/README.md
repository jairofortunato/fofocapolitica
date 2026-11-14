# Compilações documentais

Os Markdown desta pasta reúnem as seções municipais das bases regionais
existentes do MPSC e TCE-SC. Contam registros, não processos únicos. Não houve
seleção nem conferência integral dos diários originais.

Os PDFs em `layout-tubarao/` usam a capa, o CSS, os cards e a impressão do
pipeline existente, tomando `~/Downloads/AMUREL_Tubarao.pdf` como referência.
Na revisão de 21/09/2026, os 279 títulos foram substituídos por resumos dos
respectivos registros. Os selos foram lidos a partir dos extratos disponíveis,
com ressalva de que correspondem à data da publicação. Não foram removidos
arquivamentos nem feita uma nova seleção por gravidade.
Como os textos são extratos completos, o tamanho dos blocos varia. A última
página descreve as fontes e o método da compilação. A identificação eleitoral
da capa foi preservada. Os PDFs anteriores permanecem nos seus caminhos.

Para regenerar, a partir da raiz:

```sh
.venv/bin/python pdf_template/gen_consulta_documental.py resumos/consulta-documental/guaruja-do-sul-base-documental.md --regiao ameosc --cidade 'Guarujá do Sul' --out resumos/consulta-documental/layout-tubarao/AMEOSC_Guaruja-do-Sul.pdf
.venv/bin/python pdf_template/gen_consulta_documental.py resumos/consulta-documental/anitapolis-base-documental.md --regiao granfpolis --cidade 'Anitápolis' --out resumos/consulta-documental/layout-tubarao/GRANFPOLIS_Anitapolis.pdf
.venv/bin/python pdf_template/gen_consulta_documental.py resumos/consulta-documental/schroeder-base-documental.md --regiao amvali --cidade Schroeder --out resumos/consulta-documental/layout-tubarao/AMVALI_Schroeder.pdf
```

Os links para arquivos locais dependem do acesso ao repositório; os extratos
podem conter textos truncados e rótulos incorretos herdados do extrator.
Nos PDFs diagramados, a linha de fonte traz o endereço da edição oficial e o
número do processo, e o rótulo automático original é substituído pelo selo
revisto. Inconsistências identificadas têm nota junto ao registro.

`revisao/*.json` é a fonte dos títulos, selos e notas usados pelo gerador. Cada
registro está vinculado por hash ao bloco do Markdown, para impedir aplicação
de títulos à entrada errada. Os TSV registram os títulos e situações redigidos
durante a leitura; a renderização usa os JSON. O gerador verifica contagem,
alinhamento, presença de todos os títulos no PDF e identificação eleitoral.
