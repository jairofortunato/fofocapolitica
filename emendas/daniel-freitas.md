# Rastro das emendas de Daniel Freitas (PL-SC)

Levantamento em 03/11/2026. Material de apuração: cada número traz a fonte. "A verificar"
não é acusação; são pontos que pedem documento antes de publicar.

- Parte 1: as 62 emendas Pix dele, lado federal (Transferegov), todas as cidades.
- Parte 2: rastro completo das duas emendas Pix de Criciúma (federal + diário + portal).
- Parte 3: o que falta e como estender para as outras cidades.

Dados brutos: `dados/daniel-freitas/resumo.csv` (uma linha por plano) e `planos.json`
(tudo o que a API devolve). Gerados por `python3 -I emendas/transferegov.py "Daniel Freitas"`.

---

## Parte 1. Panorama das emendas Pix (2022–2026)

Fonte: Transferegov, transferências especiais (API aberta). Não inclui emendas de saúde
fundo a fundo (FNS) nem convênios; em Criciúma, por exemplo, há 3 emendas dele de 2026 para o
Piso da Atenção Primária (R$ 500 mil, R$ 1 mi e R$ 200 mil), ainda sem pagamento, que só
aparecem no portal municipal.

| Ano | Planos | Valor |
|---|---|---|
| 2022 | 10 | R$ 8.800.000,00 |
| 2023 | 8 | R$ 15.477.488,00 |
| 2024 | 11 | R$ 17.971.585,00 |
| 2025 | 20 | R$ 16.212.225,15 |
| 2026 | 13 | R$ 18.805.500,00 |
| **Total** | **62** | **R$ 77.266.798,15**, 37 beneficiários |

Pago pela União até agora: R$ 66.985.041,23. Maiores beneficiários: Passo de Torres
(R$ 6,46 mi, quase tudo numa emenda de R$ 5,47 mi de 2026 para a orla), Garopaba (5,58 mi),
Balneário Gaivota (5,43 mi), Rancho Queimado (5,40 mi), Florianópolis (4,77 mi),
Criciúma (4,68 mi), Balneário Rincão (4,39 mi), Forquilhinha (3,88 mi). Objeto dominante:
pavimentação.

**Cuidado com os relatórios de gestão.** O relatório "novo" do Transferegov declara executado
zero em várias emendas antigas (Meleiro, Lauro Müller, São Ludgero, Gov. Celso Ramos), mas o
relatório antigo de Meleiro diz que a obra foi 100% executada em 2024 (Supreme Construtora,
R$ 511.132,99). Ou seja: "executado = 0" no relatório novo **não** prova que o dinheiro está
parado. Só a ponta municipal (portal + diário) responde.

### Balneário Gaivota: auditoria da CGU (fonte primária)

**CGU, Relatório de Avaliação 1790304, "Transferências especiais (ADPF 854): Balneário Gaivota",
publicado em 05/06/2025** (e-Aud, id 1790307; cópia em `evidencias/cgu/`). Trata da emenda
**202439490003**, plano 09032024-068228, R$ 3.432.000,00, depositada em 04/07/2024. É a auditoria
que Flávio Dino remeteu à PF na ADPF 854.

1. **Dinheiro da emenda usado para pagar despesas antigas.** 15 das 18 licitações informadas pela
   prefeitura são de 2022–2023. Foram transferidos R$ 892.389,71 da conta da emenda para a conta
   própria da prefeitura, para cobrir pagamentos já feitos; 27 empenhos foram anulados e
   reemitidos com a emenda como fonte (as notas fiscais são anteriores aos empenhos). Viola o
   art. 60 da Lei 4.320/64.
2. **R$ 285.778,00 pagos por serviço não executado:** asfalto mais fino que o contratado e pago,
   em obras da **Fabran Construções LTDA** (Balneário Gaivota; sócia Flavia Stippe). Na Estrada
   Geral Anita Garibaldi, 4 cm (R$ 61.060); na Rua Tubarão, 2,5 cm (R$ 224.718). As obras foram
   concluídas e estão em bom estado; o problema é a espessura. A amostra também tinha a D&R
   Pavimentação (Sombrio), sem achado.
3. **Plano genérico:** duas metas ("Pavimentação de Vias", 10 un., R$ 3.332.000; "Equipamentos
   para Saúde", R$ 100.000), sem indicar ruas.
4. **Transparência insuficiente:** o portal não liga a emenda aos gastos, e a prefeitura não
   publicou as contratações no PNCP.
5. Os equipamentos de saúde estavam em uso e foram comprados de forma adequada.

**Resposta da prefeitura (16/04/2025):** reconheceu o erro; devolveu os R$ 892.389,71 à conta da
emenda "para novos investimentos" e passou a transferir também os R$ 285.778,00. **Isso explica o
relatório de gestão de 30/06/2026 com executado R$ 0 e pendente R$ 3.432.000:** o dinheiro voltou
para a conta. Falta saber o que foi feito com ele depois de 2025.

**O que as matérias erraram:** a newsletter (13/12/2025) fala em "obras não entregues, apesar de
pagas"; a CGU diz que as obras auditadas foram concluídas, só que com menos asfalto que o pago. O
Canal Criciúma (09/06/2025) liga o caso à Av. Beira Mar Norte, que não está na amostra da CGU.
Nenhum dos sócios da Fabran ou da D&R aparece como doador em 2022.

Na mesma série, o relatório da CGU sobre o **Estado de SC** (1823331) trata de emendas de Jorge
Seif e Caroline de Toni, não de Freitas.

### Padrão a investigar: software de PROCON

Em 2024, Freitas mandou quatro emendas com objeto quase idêntico (software de gestão para PROCON):
Estado de SC R$ 1,3 mi, Florianópolis R$ 1,2 mi, Joinville R$ 316 mil, Palhoça R$ 218 mil.
Total: R$ 3,03 mi.

| Beneficiário | Valor | União pagou | Executado declarado (2026) | Compra no PNCP |
|---|---|---|---|---|
| Estado de SC | 1.300.000 | 03/07/2024 | 0 | não encontrada |
| Florianópolis | 1.200.000 | 03/07 e 12/12/2024 | 0 | não encontrada |
| Joinville | 316.000 | 12/12/2024 | 0 | não encontrada |
| Palhoça | 218.000 | 12/12/2024 | 0 | não encontrada |

Busca feita em 03/11/2026 na API de consulta do PNCP, pelo CNPJ de cada ente, de 07/2024 a
11/2026, modalidades pregão, dispensa, inexigibilidade, concorrência e credenciamento; filtro por
"PROCON" ou "software" + "consumidor" no objeto. Só apareceram compras sem relação (coletes do
PROCON de Palhoça, R$ 4.960; plataforma de IA em Joinville, R$ 43.200).

Ainda não prova dinheiro parado: o PROCON pode comprar por CNPJ próprio (fundo municipal ou
PROCON estadual) ou por adesão a ata, e o "executado 0" do relatório novo já se mostrou pouco
confiável (Balneário Gaivota, Meleiro). Próximos passos: CNPJs dos PROCONs/fundos; diários
(DOM/SC para Palhoça; diários de Florianópolis e Joinville; DOE-SC); pedido via LAI do extrato da
conta da emenda e do processo de compra nos quatro entes.

Emendas que merecem ser as próximas a rastrear (pagas há tempo e com execução declarada zero
ou sem relatório): 2022 Lauro Müller (R$ 1 mi, restauração), São Ludgero (R$ 500 mil),
Gov. Celso Ramos (R$ 1 mi), Treviso (R$ 400 mil, sem relatório novo); 2024 Balneário Gaivota
(R$ 3,43 mi, já auditada pela CGU, ver acima: falta o destino do dinheiro devolvido à conta), Gov. Celso Ramos (R$ 2 mi), Estado de SC (R$ 1,3 mi), Florianópolis (R$ 1,2 mi).

---

## Parte 2. Criciúma: as duas emendas Pix

### Emenda 202239490001 — R$ 1.700.000,00 — viaduto da Rua Virgínio Conti

| Data | Evento | Fonte |
|---|---|---|
| 04/10/2021 | Contrato 258/PMC/2021: projeto executivo do viaduto, Econômica Engenharia e Obras, R$ 106.448,46 | DOM Criciúma nº 2831 |
| 24/01/2022 | Concorrência 392/PMC/2021 (obra do viaduto) **deserta** | DOM nº 2898 |
| 25/02/2022 | Edital da Concorrência 029/PMC/2022, viaduto de 83 m, recurso declarado: **transferência especial do Governo do Estado (Portaria 364/SEF/2021)** | DOM nº 2921 |
| 05/04/2022 | **Contrato 078/PMC/2022, SETEP Construções S.A., R$ 6.710.518,90** | DOM nº 2953 |
| 01/07/2022 | União paga a emenda (OB 2022OB802691), conta Caixa 575864735 | Transferegov |
| 18/08/2022 | Empenho 5277/2022, "alteração parcial de fonte de recurso do empenho 2360/2022", R$ 1,7 mi; **pago R$ 1.360.935,47** | Portal Betha, execução |
| 16/01/2023 | Empenho 576/2023, **pago R$ 339.064,53** | Portal Betha |
| 20/12/2024 | Relatório **final**: R$ 1.700.000,00 executados | Transferegov |

1.360.935,47 + 339.064,53 = **1.700.000,00**: a emenda inteira foi para a SETEP, na obra do
viaduto. Total pago à SETEP pelo viaduto (todas as fontes): R$ 6.388.771,49.

### Emenda 202339490001 — R$ 2.977.488,00 — viaduto + praças + Rua Martinho Brunelli

União pagou em 30/08/2023 (OB 2023OB808111, conta Caixa 575864736). Plano de trabalho de
30/08/2023 a **30/08/2026**.

**O plano tem duas versões de metas**, cada uma somando R$ 2.977.488,00:

| Versão A (a que o relatório usa) | Valor | Versão B | Valor |
|---|---|---|---|
| Viaduto Virgínio Conti (83 m) | 544.970,80 | Praça Abele Colle | 601.306,38 |
| Praça Abelle Colle | 130.229,22 | Praça da Santa Bárbara | 528.062,58 |
| Pavimentação Rua Martinho Brunelli (2.969 m, obra total R$ 6,5 mi) | 2.302.287,98 | "Parques e Praças (com local a definir)" | 1.848.119,04 |

Relatório parcial de 30/06/2026: executado R$ 675.200,02 (= viaduto + praça da versão A),
pendente R$ 2.302.287,98 (= Martinho Brunelli).

O que o diário e o portal mostram:

| Obra | Licitação | Contrato | Contratada | Valor | Pago (todas as fontes) |
|---|---|---|---|---|---|
| Viaduto | Concorrência 029/2022 | 078/PMC/2022 | SETEP Construções S.A. (Criciúma) | 6.710.518,90 | 6.388.771,49 |
| Praça Abelle Colle | Tomada de Preços 211/2023, edital cita "Emenda de Transferência Especial Nº 09032023-037199"; 4 concorrentes (Consoni, Fabris, West, Alianz) | 210/PMC/2023, 27/09/2023 | West Engenharia LTDA (Criciúma) | 601.306,38 | 540.654,35 |
| Praça Santa Bárbara | Tomada de Preços 160/2023 | 191/PMC/2023, 04/09/2023 | West Engenharia LTDA | 552.593,68 | 420.830,70 |
| Rua Martinho Brunelli | Concorrência Eletrônica 031/2026 | 059/PMC/2026, 19/06/2026, 300 dias | Confer Construtora Fernandes LTDA (Siderópolis) | 8.353.001,90 | 1.160.299,41 (até out/2026) |

Atos orçamentários: lei/decreto de 08/08/2023 (DOM nº 3284) abre R$ 785.975,52 para
Parques/Praças "por conta da emenda 202339490001", valor igual ao estimado da praça Abelle
Colle; decreto de abril/2026 (DOM nº 3960) reabre por superávit o saldo da emenda
202339490001 existente em 31/12/2025.

**Empenho 4303/2026 (22/06/2026), Confer, R$ 2.302.287,98**: exatamente o saldo pendente da
emenda. Pago até agora: R$ 0.

### Pontos a verificar

1. **Dinheiro parado por quase 3 anos.** A União pagou R$ 2,98 mi em 30/08/2023; R$ 2,30 mi
   seguiam em conta em 31/12/2025 (decreto de superávit) e só foram empenhados em 22/06/2026,
   ano eleitoral, numa obra de R$ 8,35 mi. O prazo do plano venceu em 30/08/2026 com a parcela
   da emenda sem pagamento. Pedir: prorrogação no Transferegov e extratos da conta 575864736.
2. **Mesma obra, três fontes.** O viaduto foi licitado como "transferência especial do Governo
   do Estado" (Portaria 364/SEF/2021) e recebeu R$ 1,7 mi da emenda de 2022 e, pelo relatório,
   mais R$ 544.970,80 da de 2023. Conferir se as fontes somadas não passam do custo da obra e
   quem é creditado pela obra na comunicação oficial.
3. **Duas versões de metas.** A versão B tira o viaduto e a Martinho Brunelli e põe R$ 1,85 mi
   em "parques e praças com local a definir". O relatório continua usando a versão A. Qual vale?
4. **Valores do relatório × pagamentos.** O relatório credita só R$ 130.229,22 à praça Abelle
   Colle, mas o contrato com edital vinculado à emenda é de R$ 601.306,38 (pagos R$ 540.654,35).
   A parcela de R$ 544.970,80 do viaduto não foi localizada nos empenhos da SETEP (a API do
   portal não traz a fonte de recurso de cada empenho).
5. **Uma empresa, duas praças em 30 dias.** West Engenharia (sócio único Daniel Amboni,
   capital R$ 1,2 mi, aberta em 2018) ganhou as duas praças (04/09 e 27/09/2023).
6. **Laço local do deputado.** O diário registra Daniel Freitas como ex-vereador (suplente em
   conselho, 2016) e ex-presidente da Fundação Cultural de Criciúma, e um representante dele
   ("Nicola Martins") numa comissão municipal nomeada em fevereiro de 2025 (DOM nº 3667).
   Contexto, não irregularidade.
7. **Os Smielevski (verificado em fontes primárias; parentesco NÃO verificado):**
   - **César Smielevski** doou R$ 10.000 a Daniel Freitas em 28/10/2022, depois do 1º turno (TSE,
     receitas de candidatos 2022). A Receita (QSA) o lista como **sócio da Betha Sistemas LTDA
     desde a fundação, em 1995** (CNPJ 00.456.865/0001-67, sede em Criciúma). A Betha é
     fornecedora da prefeitura: R$ 2,0–2,3 mi pagos por ano em 2022–2024, R$ 4,27 mi em 2026; venceu
     o Pregão 141/2025 (gestão pública, R$ 6,51 mi homologados → contrato 137/2025, R$ 6,79 mi) e o
     Pregão 140/2025 (gestão escolar, R$ 222,6 mil, estimado em R$ 875 mil). A Betha também é o
     sistema do portal de transparência, aquele que não mostra as emendas Pix (ver rastro Guidi).
     Não há indício de que isso seja intencional; vale perguntar à prefeitura e à Betha.
   - **Kátia Maria Smielevski Gomes**, engenheira de carreira (origem CODEPLA), foi secretária de
     Infraestrutura; foi afastada em jan/2021 no caso da Operação Blackout (Gaeco, 2020); foi
     absolvida e voltou em jun/2026 (Portal Engeplus, 26/06/2026). O MPSC instaurou o **IC
     06.2026.00002801-0** (11ª PJ, jun/2026) para apurar a reintegração e a possível designação dela
     para chefia ou cargo comissionado. Um IC anterior (06.2023.00004547-3, desvio de função) foi
     arquivado em 2024.
   - **Contradição a esclarecer:** a matéria diz que ela estava longe do Paço desde jan/2021, com
     cautelares que a impediam de trabalhar. Mas o diário de Criciúma a mostra **atuando em
     2022**: pareceres técnicos 001 e 002/2022 (21/01/2022, Concorrência 392/2021, a do viaduto,
     DOM nº 2898), resposta assinada no edital do viaduto (Concorrência 029/2022, DOM nº 2941,
     25/03/2022), nomeação para comissão de concurso (DOM nº 2924, 02/03/2022) e parecer
     103/2022 (13/06/2022, DOM nº 2996). Na folha de pagamento do portal, ela aparece como
     "Trabalhando" em todos os meses de jan/2024 a out/2026, menos abr–mai/2026 ("Licença"), com
     R$ 9,2 mil a R$ 10,8 mil brutos. Hipótese a checar: o afastamento de jan/2021 era só do cargo
     de secretária-geral, e a proibição de frequentar a prefeitura veio depois. Pedir as decisões
     judiciais (com datas) e o histórico funcional.
   - **Não há documento ligando César e Kátia.** Mesmo sobrenome, mesma cidade. Não publicar
     parentesco sem prova.

### Quem doou (TSE 2022)

Daniel Costa de Freitas, deputado federal, PL, nº 2211: R$ 1.799.004,88 arrecadados, sendo
R$ 1 mi da direção nacional do PL e R$ 785.100 de pessoas físicas. Maiores: Jorge Luiz Savi de
Freitas (150 mil), Eli Fortunato Filho (135 mil), Ronaldo Accioli de Freitas (65 mil), Gilberto
Luiz Zanette (60 mil), Ricardo Castellar de Faria, Themines Agricio de Freitas, Rui Denardin,
Paula da Silva Zaccaron, José Aparecido dos Santos (50 mil cada).
**Nenhum dirigente da SETEP, da West ou da Confer aparece como doador dele nem de qualquer
candidato de SC em 2022.**

---

## Parte 3. Próximos passos

- **Doadores × empresas:** cruzar os doadores pessoa física acima com o quadro de sócios das
  empresas contratadas com dinheiro das emendas nas outras 36 cidades.
- **Outras cidades:** o lado federal já está pronto em `resumo.csv`. Para cada cidade, o lado
  municipal sai do DOM/SC (`mp/diarios/coletar.py <cidade> --fontes municipal`) e do portal
  (muitas usam Betha, o mesmo cliente de `~/99x/transparencia`).
- **Saúde (fundo a fundo):** as emendas de saúde não passam pelo Transferegov; a fonte é o FNS.

## Evidências

`evidencias/cgu/`: relatórios CGU 1790304 (Balneário Gaivota) e 1823331 (Estado de SC), CNPJs da Fabran e da D&R.
`evidencias/daniel-freitas-criciuma/`: PDFs do diário de Criciúma (nº 2831, 2921, 2953, 3284,
3308, 3324, 3960, 4010), `pagamentos.txt` (empenhos do portal por obra), `cnpj_*.json`
(Receita). Federal: `dados/daniel-freitas/planos.json`.
