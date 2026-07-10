# 🔎 DOSSIÊ TÉCNICO — Portal da Transparência da AFASC vs. a Lei

> Complemento do [Caso 5 — AFASC: modelo de gestão](caso5-afasc-modelo-de-gestao.md).
> Raspagem completa do portal em 31/05/2026 + análise de conformidade legal.
> Fonte raspada: https://www.afasc.com.br/portal-de-transparencia
> CNPJ AFASC: **75.565.572/0001-17**

---

## 1. Sumário executivo (o veredito)

A AFASC **mantém** um portal de transparência com volume razoável de documentos (**80 pastas, 340 arquivos**): estatutos, contrato de gestão, termos de colaboração, contratos com fornecedores, balanços e relação de funcionários. **Não é um portal vazio.**

Mas, confrontado com a lei, ele tem **5 falhas estruturais** que são exatamente o tipo de coisa que sustenta a investigação do MP por descumprimento da **Lei de Acesso à Informação**:

1. **Não há canal de pedido de informação (e-SIC/SIC)** — nem formulário, nem e-mail dedicado, nem responsável nomeado.
2. **A "folha de pagamento" não existe como tal** — o que há é só uma **tabela de headcount** (quantos funcionários por mês), **sem nomes e sem remuneração**.
3. **Receitas/despesas e a aplicação dos recursos públicos** não estão num demonstrativo claro e acessível — a "prestação de contas" é jogada para um **sistema externo** (gerr.com.br) que sequer abre direito.
4. **Defasagem temporal**: balanços só vão até ~2023/2024; várias seções param em 2020–2023.
5. **Formato fechado** (PDF, alguns escaneados) — nada em dado aberto/legível por máquina.

> ⚖️ **Em uma frase:** a AFASC publica *documentos*, mas não entrega *transparência ativa* no padrão que a LAI exige de quem vive de dinheiro público — e não oferece o caminho para o cidadão *pedir* o que falta.

---

## 2. O que a AFASC PUBLICA hoje (inventário real do portal)

Raspagem recursiva das 5 seções (datas = o que efetivamente está no ar):

| Seção | Conteúdo encontrado | Observação crítica |
|---|---|---|
| **Balanço Patrimonial** | 2019, 2020, 2021, 2022 (recortes da *Gazeta*), 2023 (arquivo "balanco afasc 2024.pdf") | **Para em 2023/24.** Sem 2025. Sem DRE/notas explicativas separadas. |
| **Contratos** | **Contrato de Gestão / Educação** (28 arquivos); **Termos de Colaboração** (Criança, Assistência Social, Idoso, Praça Céu, Lar Azul, Abrigo Florescer); **Prestação de Serviço** (CASAN, Portabilis, Müller Auditores, vigilância, etc. — dezenas de fornecedores) | Ponto **forte**: o contrato de gestão e os termos estão lá. Falta o **plano de trabalho, metas e aditivos com valores consolidados**. |
| **Estrutura Organizacional** | Estatuto Social (8 versões históricas), Regimento Interno, Organograma, Constituição OS, Qualificação OS, Acordos Coletivos (só 2020 e 2021), Agenda de Conselhos (xlsx), Edital de Matrícula, Guia de Procedimentos | Acordos coletivos **param em 2021**. Sem atas/pareceres do Conselho Fiscal. |
| **Inventário de Bens** | Cessão de Uso de Imóveis (29 arquivos), Patrimônio Próprio (2 arquivos) | OK como existência; sem relação patrimonial valorada/atualizada. |
| **Pessoal** | "Relação de Funcionários" 2020–2025 (1 PDF/ano) | ⚠️ **É só contagem mensal** (ex.: 2025 → 1.372 CLT ativos em jan). **Sem nomes, sem cargos individualizados, sem salários.** |
| **Links úteis** | "PRESTAÇÃO DE CONTAS" → sistema externo **gerr.com.br** (chave 82916818000113) · "Conversor PDF" → ilovepdf | A prestação de contas **não está no portal**; depende de sistema de terceiro que **não carregou** na verificação. |

**Dirigentes identificados no portal:** Presidente de Honra **Gisele Bolan**, Presidente do Conselho **Celito Cardoso**, Diretora Executiva **Gheniffer Dutra**.
*(Obs.: nomes distintos do caso da AMA-REC — não confundir entidades.)*

---

## 3. O regime jurídico — o que a lei EXIGE de quem recebe dinheiro público

A AFASC é entidade privada sem fins lucrativos qualificada como **OS** (contrato de gestão p/ educação) e parceira via **termos de colaboração** (assistência social/idoso). Por isso incidem, em camadas:

1. **Lei nº 12.527/2011 (LAI) — Art. 2º e parágrafo único.** A LAI alcança "entidades privadas sem fins lucrativos que recebam recursos públicos... mediante contrato de gestão, termo de parceria, convênios...". O parágrafo único determina publicidade quanto à **"parcela dos recursos públicos recebidos e à sua destinação"**, sem prejuízo dos relatórios contábeis. → *É a base direta do IC do MP.*
2. **LAI — Art. 8º (transparência ativa) e Art. 9º (SIC).** Rol mínimo no site (registros de despesas, contratos, repasses) **em formato aberto** (§3º) e **canal para pedidos de informação** com prazo de resposta.
3. **Lei nº 13.019/2014 (MROSC) — Art. 11.** A OSC **"deverá divulgar na internet e em locais visíveis de suas sedes... todas as parcerias celebradas com a administração pública"**, com dados de execução. Some-se a prestação de contas dos Arts. 63–72.
4. **Lei nº 9.637/1998 (OS) / lei municipal de OS.** Contrato de gestão exige **relatório anual de execução com comparativo de metas e resultados** e publicação.
5. **LC nº 101/2000 (LRF) + LC nº 131/2009.** Transparência da aplicação de recursos públicos, preferencialmente em tempo real.
6. **STF, Tema 483 (ARE 652.777).** Legitimidade da divulgação **nominal e individualizada da remuneração** custeada com recursos públicos — fundamento para exigir folha com valores de quem é pago com dinheiro do convênio/contrato de gestão.

---

## 4. Análise de conformidade — o que falta ou está deficiente

| # | Exigência legal | Está no portal? | Evidência da raspagem | Base legal |
|---|---|---|---|---|
| 1 | **Canal de pedido de informação (e-SIC/SIC)** + responsável + prazo | ❌ **Não** | Nenhum SIC/e-SIC, sem e-mail/forma dedicada à LAI | LAI Art. 9º |
| 2 | **Remuneração individual** de quem é pago com recurso público | ❌ **Não** | "Relação de Funcionários" = só nº de colaboradores/mês | LAI Art. 8º §1º; STF Tema 483 |
| 3 | **Valor, origem e aplicação** dos recursos públicos (demonstrativo claro) | ⚠️ **Deficiente** | Empurrado p/ gerr.com.br (externo, não abriu); sem painel próprio | LAI Art. 2º §único; LRF/LC 131 |
| 4 | **Receitas e despesas / execução** das parcerias | ⚠️ **Parcial** | Só balanço patrimonial até 2023/24; sem execução por parceria | MROSC Arts. 11, 63–72 |
| 5 | **Relatório de execução do contrato de gestão + metas** | ❌ **Não localizado** | Há o contrato, não o relatório comparativo de metas | Lei 9.637/98 |
| 6 | **Atualidade (tempestividade)** | ⚠️ **Defasado** | Balanços ~2023, acordos coletivos 2021, relação 2025 só jan–mar | LAI Art. 8º §3º VI |
| 7 | **Formato aberto / legível por máquina** | ❌ **Não** | Tudo PDF (alguns escaneados), nenhum CSV/planilha aberta | LAI Art. 8º §3º II e III |
| 8 | **Plano de trabalho, aditivos e valores consolidados** dos contratos | ⚠️ **Parcial** | Contratos sim; planos/metas/valores agregados não | MROSC Art. 11 |
| 9 | **Atas/pareceres do Conselho Fiscal** | ❌ **Não** | Só "agenda de reunião" (xlsx) | Estatuto/OS |

**Pontos a favor da AFASC (para equilíbrio editorial):** estatutos, contrato de gestão, termos de colaboração e contratos com fornecedores **estão publicados** — o que é mais do que muitas OSCs fazem. O problema não é ausência total; é **transparência ativa incompleta + ausência de via de acesso passivo (SIC)**.

---

## 5. Como isso amarra na investigação do MP

- **IC 06.2020.00004363-0** (concluído em 20/05/2026): apurava **improbidade por descumprimento da LAI** envolvendo **Município de Criciúma + AFASC + Instituto Maria Schmitt** — exatamente a falta de transparência das entidades que recebem recursos públicos via contrato de gestão. **As lacunas 1, 2 e 3 acima são a materialização disso.**
- **IC 06.2026.00002086-1** (instaurado em 22/05/2026): "regularidade e **viabilidade do modelo de gestão**". Um portal que não mostra remuneração nem a aplicação do dinheiro **dificulta o controle social** do modelo — reforça a pertinência da investigação.
- **TCE/SC** (ver `tcesc/resumos/cidades/amrec-tce.md`): já registrava "AFASC/Maria Schmitt LAI — ACP iminente".

---

## 6. Roteiro de pedido de informação (pauta de apuração)

Como **não há e-SIC**, o próprio "não ter onde pedir" já é matéria. Perguntas a protocolar (via Fale Conosco / ouvidoria do município / MP):
1. Qual o **valor total repassado** pela Prefeitura de Criciúma à AFASC em 2023, 2024 e 2025, por instrumento (contrato de gestão x termos de colaboração)?
2. Cadê a **folha com remuneração** dos cargos custeados com recurso público (ao menos por cargo/faixa)?
3. Onde está o **relatório de execução do contrato de gestão** com **comparativo de metas** de cada exercício?
4. Por que os **balanços param em 2023/2024**? Onde está o de 2024/2025 auditado?
5. A AFASC possui **regulamento próprio de compras** e publica suas **cotações/seleções de fornecedores**?
6. Existe **SIC/e-SIC** e quem é o responsável pela LAI na entidade?

---

## 7. Ganchos para vídeo
- "Fomos no portal da transparência da AFASC: tem 340 arquivos — mas faltam justamente os que a lei mais exige."
- Comparação visual: **"o que eles mostram" × "o que a lei manda mostrar"** (a tabela da seção 4 vira um quadro na tela).
- Ângulo cidadão: "Você quer saber quanto a AFASC recebe e paga de salário com seu dinheiro? **Não tem onde pedir.**"
- ⚠️ **Equilíbrio:** dizer também o que ELES publicam (estatuto, contratos), e procurar a AFASC para resposta. Lacuna de transparência ≠ prova de desvio.

---

## 8. Anexos / como reproduzir
- Inventário bruto raspado: pasta `afasc_scrape/` (HTMLs das seções, `func2025.pdf`, `balanco2023.pdf`).
- Padrão de download dos arquivos do portal: `https://www.afasc.com.br/baixar.php?arquivo=portal-transparencia/<SEÇÃO>/<...>/<arquivo>`.
- Prestação de contas externa: `https://gerr.com.br/principal.php?m=portal&chave=82916818000113&proponente=75.565.572/0001-17` (não carregou na verificação — confirmar manualmente no navegador).

## Fontes legais
- [LAI — Lei nº 12.527/2011 (Planalto)](https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2011/lei/l12527.htm) — Art. 2º §único, Arts. 8º e 9º
- [MROSC — Lei nº 13.019/2014 (Planalto)](https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2014/lei/l13019compilado.htm) — Art. 11
- [Lei das OS — nº 9.637/1998 (Planalto)](https://www.planalto.gov.br/ccivil_03/leis/l9637.htm)
- STF, Tema 483 / ARE 652.777 (remuneração individual custeada com recurso público)
- Portal raspado: https://www.afasc.com.br/portal-de-transparencia
