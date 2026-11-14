# Contexto do projeto

Este repositório produz os dossiês em PDF por cidade do Fofoca Política:
Transparência Radical, a partir de fontes públicas do MPSC e do TCE-SC.
Leia `fofoca-casos/README.md` e `pdf_template/README.md` para o fluxo atual.
A linha editorial está em `../fofoca-politica/CLAUDE.md`.
Antes de curar conteúdo, leia `pdf_template/CURADORIA.md`.
O `pdf_template/HANDOFF.md` contém contexto histórico; seus caminhos, números
e tarefas de continuação podem estar desatualizados.

## Identificação dos documentos

O usuário informou que é candidato e exige identificação eleitoral nos
documentos destinados à distribuição. Preserve o bloco existente em
`pdf_template/templates/cover.html`:

- Propaganda eleitoral.
- Jairo Fortunato — Deputado Estadual — 14999.
- Partido Missão · CNPJ: 68.475.851/0001-24 · Tiragem: digital/ilimitada.

Estes dados vêm do template existente, não de uma validação cadastral externa.
Não invente nem substitua o CNPJ. Confira a presença e a legibilidade do bloco
no PDF final. A capa já o inclui sem flag; `--campanha` do gerador de graves
acrescenta a faixa também à contracapa. Preserve a identidade visual aprovada.

## Integridade das fontes

Cada nome, valor, data e desfecho deve ser sustentado pela fonte citada.
Distinga investigação, acusação, arquivamento e condenação. Confira recursos
e decisões posteriores. Não confie nos rótulos automáticos de ACP ou rejeição
de contas: leia o dispositivo original. Não atribua à cidade valores ou pessoas
de outro processo colado pelo extrator. Preserve o alinhamento posicional da
curadoria e não reextraia dados brutos que já tenham curadoria.

## Recorte e seleção dos dossiês

O fluxo parte dos diários oficiais do MPSC e do TCE-SC dos **últimos quatro
anos**: confirme o intervalo exato e a cobertura das edições antes de afirmar
que a varredura está completa. A data da edição usada em cada card deve estar
dentro do intervalo; leia também decisões e recursos posteriores pertinentes.
Se a base local parar antes do fim do período, informe a lacuna e não apresente
o PDF como levantamento exaustivo até a data atual.

Selecione primeiro os casos graves com substância verificável. Em cidades
pequenas com poucos graves, inclua também apurações de interesse público com
gravidade média: irregularidades corrigidas, recomendações cumpridas,
investigações ainda abertas e arquivamentos que esclareçam o resultado.
Marque cada uma conforme a decisão original; não pinte casos médios como graves
nem use rótulos automáticos contraditos pelo texto. Títulos e resumos devem
explicar o fato e o estágio em duas a quatro frases.

## Operação

O usuário prefere execução autônoma: prossiga com leituras, edições reversíveis
e verificações necessárias à tarefa solicitada sem confirmações rotineiras.
Pergunte apenas por informação indispensável ausente ou aprovação exigida pelo
ambiente. Respeite as permissões efetivas da sessão.
Preserve alterações preexistentes. Para PDFs de casos graves, utilize
`pdf_template/gen_graves_md.py`, não `md_to_pdf.sh`.
