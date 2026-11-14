# fofoca-casos

Pasta de destino dos **casos fechados** do Fofoca Política dentro do `mp/`:
o material apurado a partir do Diário Oficial do MPSC que já está pronto para
virar post, vídeo ou carrossel.

Não confundir com o repositório `../../fofoca-politica/`, que é a ferramenta de
produção (coleta de pauta, `dados.json`, artes). Aqui ficam os **dossiês de
cidade** — markdown + PDF — que servem de fonte para aquele repositório.

Os arquivos `nova-trento-casos-graves.*` e `vidal-ramos-casos-graves.*` são
versões anteriores. Para distribuição, use os respectivos
`*-casos-investigacoes.pdf`: as versões novas conferem o dispositivo e os
recursos posteriores. Os rótulos automáticos das versões antigas confundiam
aprovação de contas com rejeição e cautelar revogada com sustação vigente.

## Origem dos dados

Tudo sai de `../resumos/regioes/regiao-*.md`, que por sua vez é gerado por
`../build_regioes.py` a partir das edições do DO-MPSC em `../parsed/`.
Cada caso citado aqui traz o número do procedimento e a data da edição, para
conferência no diário original.

## Como gerar o PDF e publicar

```
cd ../pdf_template && ../.venv/bin/python gen_graves_md.py \
    ../fofoca-casos/<arquivo>.md --regiao <sigla> --cidade "<Cidade>"
cp fofoca-casos/<arquivo>.pdf ~/FOFOCA-CASOS-CERTO/<REGIAO>_<Cidade>-GRAVES.pdf
```

O `gen_graves_md.py` põe estes dossiês na identidade do produto: a **mesma capa
e a mesma contracapa** do `<REGIAO>_<Cidade>.pdf` diagramado, o mesmo cabeçalho
com bandeira, brasão e finanças, e a cor da cidade como fio condutor. O que muda
é o miolo — aqui o caso é meia página de texto apurado, não um card de quatro
linhas. **Não use mais o `md_to_pdf.sh`** para este material: ele é o CSS
genérico de markdown e sai um relatório azul sem relação nenhuma com o resto.

Os **markdowns ficam aqui**, versionados junto do pipeline que os gera. O PDF
final vai para `~/FOFOCA-CASOS-CERTO/`, onde estão todos os dossiês publicados.
A diferença entre os dois arquivos de uma mesma cidade daquela pasta:
`<REGIAO>_<Cidade>.pdf` é o dossiê completo, com todos os casos em card;
`-GRAVES.pdf` é a seleção apurada um a um, em texto longo.

## Regras que valem aqui

As cinco regras de `../../fofoca-politica/CLAUDE.md`. As duas que mais pesam
neste material:

- **Acusação é acusação, não fato.** Inquérito civil instaurado não é condenação,
  e arquivamento não é absolvição de ninguém — é o MP dizendo que não achou
  base para processar. O status de cada caso está explícito.
- **Nada entra que não esteja na fonte.** Se um número não está no extrato do
  DO, ele não entra no post.

## Conteúdo

| Arquivo | Cidade | Fontes | Casos | Publicado como |
|---|---|---|---|---|
| `florianopolis-casos-graves.md` | Florianópolis | MPSC | 15 de 741 | `GRANFPOLIS_Florianopolis-GRAVES.pdf` |
| `cacador-casos-graves.md` | Caçador | MPSC + TCE/SC | 14 de 185 + 136 | `AMARP_Cacador-GRAVES.pdf` |
| `jacinto-machado-casos-graves.md` | Jacinto Machado | MPSC + TCE/SC | 10 de 25 + 10 | `AMESC_Jacinto-Machado-GRAVES.pdf` |
| `presidente-getulio-casos-graves.md` | Presidente Getúlio | MPSC + TCE/SC | 14 de 106 + 23 | `AMAVI_Presidente-Getulio-GRAVES.pdf` |
| `governador-celso-ramos-casos-graves.md` | Governador Celso Ramos | MPSC + TCE/SC | 12 de 66 + 42 | `GRANFPOLIS_Governador-Celso-Ramos-GRAVES.pdf` |
| `imbituba-casos-graves.md` | Imbituba | MPSC + TCE/SC | 14 de 220 + 308 | `AMUREL_Imbituba-GRAVES.pdf` |
| `ararangua-casos-graves.md` | Araranguá | MPSC + TCE/SC | 13 de 348 + 83 | `AMESC_Ararangua-GRAVES.pdf` |
| `pinhalzinho-casos-graves.md` | Pinhalzinho | MPSC + TCE/SC | 10 de 76 + 21 | `AMOSC_Pinhalzinho-GRAVES.pdf` |
| `praia-grande-casos-graves.md` | Praia Grande | MPSC + TCE/SC | 10 de 41 + 23 | `AMESC_Praia-Grande-GRAVES.pdf` |
| `nova-veneza-casos-graves.md` | Nova Veneza | MPSC + TCE/SC | 11 de 44 + 14 | `AMREC_Nova-Veneza-GRAVES.pdf` |
| `sao-jose-do-cedro-casos-graves.md` | São José do Cedro | MPSC + TCE/SC | 11 de 38 + 12 | `AMEOSC_Sao-Jose-Do-Cedro-GRAVES.pdf` |
| `itapoa-casos-graves.md` | Itapoá | MPSC + TCE/SC | 14 de 176 + 50 | `AMUNESC_Itapoa-GRAVES.pdf` |
| `tijucas-casos-graves.md` | Tijucas | MPSC + TCE/SC | 14 de 182 + 93 | `GRANFPOLIS_Tijucas-GRAVES.pdf` |
| `balneario-camboriu-casos-graves.md` | Balneário Camboriú | MPSC + TCE/SC | 16 de 862 + 382 | `AMFRI_Balneario-Camboriu-GRAVES.pdf` |
| `ibirama-casos-graves.md` | Ibirama | MPSC + TCE/SC | 14 de 64 + 13 | `AMAVI_Ibirama-GRAVES.pdf` |
| `paulo-lopes-casos-graves.md` | Paulo Lopes | MPSC + TCE/SC | 12 de 50 + 13 | `GRANFPOLIS_Paulo-Lopes-GRAVES.pdf` |
| `porto-belo-casos-graves.md` | Porto Belo | MPSC + TCE/SC | 13 de 887 + 47 | `AMFRI_Porto-Belo-GRAVES.pdf` |
| `sao-jose-casos-graves.md` | São José | MPSC + TCE/SC | 14 de 719 + 189 | `GRANFPOLIS_Sao-Jose-GRAVES.pdf` |
| `fraiburgo-casos-graves.md` | Fraiburgo | MPSC + TCE/SC | 13 de 66 + 29 | `AMARP_Fraiburgo-GRAVES.pdf` |
| `aurora-casos-graves.md` | Aurora | MPSC + TCE/SC | 12 de 55 + 15 | `AMAVI_Aurora-GRAVES.pdf` |
| `mafra-casos-graves.md` | Mafra | MPSC + TCE/SC | 13 de 306 + 54 | `AMPLANORTE_Mafra-GRAVES.pdf` |
| `rio-do-oeste-casos-graves.md` | Rio do Oeste | MPSC + TCE/SC | 12 de 179 + 9 | `AMAVI_Rio-Do-Oeste-GRAVES.pdf` |
| `rio-do-sul-casos-graves.md` | Rio do Sul | MPSC + TCE/SC | 14 de 414 + 37 | `AMAVI_Rio-Do-Sul-GRAVES.pdf` |
| `guaraciaba-casos-graves.md` | Guaraciaba | MPSC + TCE/SC | 10 de 18 + 7 | `AMEOSC_Guaraciaba-GRAVES.pdf` |
| `itaiopolis-casos-graves.md` | Itaiópolis | MPSC + TCE/SC | 13 de 270 + 38 | `AMPLANORTE_Itaiopolis-GRAVES.pdf` |
| `santa-cecilia-casos-graves.md` | Santa Cecília | MPSC + TCE/SC | 12 de 171 + 19 | `AMURC_Santa-Cecilia-GRAVES.pdf` |
| `anitapolis-casos-graves.md` | Anitápolis | MPSC + TCE/SC | 11 de 48 + 13 | `GRANFPOLIS_Anitapolis-GRAVES.pdf` |

## Armadilha de comarca

O `build_regioes.py` agrupa por **comarca**, não por município. Em Caçador isso
significa que 574 casos aparecem sob a cidade mas só 185 são dela — o resto é
Macieira, Rio das Antas e Calmon. **Sempre filtre por "Município/Prefeitura/Câmara
de <cidade>" antes de escrever.** Florianópolis não tem esse problema: a Comarca
da Capital cobre só a Capital.

**Rio do Sul** é o pior caso de todos: sede de comarca, cobre Lontras, Aurora,
Presidente Nereu e Agronômica — **303 dos 819 registros são dos vizinhos**. Em
**Rio do Oeste** a comarca cobre Laurentino (96 de 308).

Em **Porto Belo** a comarca cobre Bombinhas (330 dos 1.242 registros) e em
**Fraiburgo** cobre Monte Carlo (55 de 142). **São José** quase não sofre com isso
— só 38 registros são de São Pedro de Alcântara —, mas sofre de outra coisa: o
prefixo do nome. São José do Cerrito, São José do Cedro, São Francisco do Sul,
São João Batista e São Bento do Sul entram na base por semelhança, e **dois dos
três "pareceres pela rejeição" que aparecem sob São José são de São José do
Cedro**. **Sempre confira a unidade gestora antes de atribuir qualquer decisão.**

Caso à parte é o **CINCATARINA**: o consórcio intermunicipal tem sede em
Fraiburgo, e **68 dos 101 processos do TCE listados sob a cidade são dele** — de
outros municípios, inclusive uma multa ao ex-prefeito de São Francisco do Sul.

O mesmo vale para **Ibirama**: a comarca cobre José Boiteux e Vitor Meireles, e dos
120 casos listados sob a cidade **30 são desses dois municípios**. **Paulo Lopes**
é outra exceção que confirma a regra: pertence à Comarca de Garopaba, mas os 60
registros citam todos o município.

O mesmo vale para **Presidente Getúlio**: dos 232 casos listados sob a cidade, só
**106** citam o município — os outros são de Dona Emma, Vitor Meireles e
Witmarsum. **Jacinto Machado** é a exceção que confirma a regra: pertence à
Comarca de Turvo, mas os 25 casos listados citam todos o município.

Do lote de 2026, o pior caso é **Pinhalzinho**: dos 76 procedimentos únicos, só
cerca de **26** são do município — o resto é de Nova Erechim e Saudades.
**Araranguá** também morde: dos 348 únicos, **129** citam Araranguá; os demais
são de Maracajá, Balneário Arroio do Silva ou do Estado (22ª GERED, Corpo de
Bombeiros, Presídio Regional). Já **Governador Celso Ramos** (Comarca de
Biguaçu), **Imbituba** e **Praia Grande** (Comarca de Santa Rosa do Sul) não têm
esse problema: praticamente todos os casos listados citam o próprio município.

## Armadilha do extrator

O extrator de texto do DO às vezes **cola ao fim de um extrato o começo de outro**
— normalmente uma notificação de alerta fiscal de outra cidade. Já apareceu
Forquilhinha em Caçador, Otacílio Costa em Jacinto Machado, e Rio Fortuna e
Presidente Nereu em Presidente Getúlio. **Todo valor em reais precisa ser conferido
contra a unidade gestora do processo antes de virar post.**

No lote de 2026 apareceram mais quatro, todas documentadas dentro de cada dossiê:

- **Governador Celso Ramos** — o RLI 25/00165919 vem colado com Rio Negrinho,
  Urussanga, Itapema e portarias internas do TCE. Descartado.
- **Imbituba** — a PCP 24/00242067 (Contas de 2023) traz, no corpo da decisão,
  uma multa de R$ 8.600,13 ao prefeito **de Itajaí**. Não é de Imbituba.
- **Araranguá** — a REP 25/00126930 traz R$ 370.129.284,51 de uma concorrência
  **estadual** (SIE) para construir quatro penitenciárias. Não é do município.
- **Pinhalzinho** — o PAP 23/80043927 mistura Pinhalzinho com a **Prefeitura de
  São José** e um valor de R$ 34,7 milhões. Caso publicado com alerta explícito.
- **Praia Grande** — a REP 22/80037330 de 15/07/2026 tem, sob "Decisão", uma
  portaria do TCE sobre uma "Sala de Concentração" para seus servidores.

Outro padrão recorrente do extrator: ao fim de quase toda decisão do TCE vem
colado **o nome da cidade do documento seguinte do diário** ("Jaraguá do Sul",
"Içara", "Guaramirim", "Tijucas"). **Não são partes do processo.**


## Lote de setembro/2026 — Nova Veneza, São José do Cedro, Itapoá e Tijucas

Quatro cidades novas, extraídas com `extract_city_strict.py` para
`pdf_template/_graves_raw/` (diretório separado, **sem tocar** no
`_curated_data/raw/` das regiões já curadas).

**A armadilha mais grave descoberta neste lote: o rótulo de parecer de contas.**
O classificador marcou as contas de 2021 e 2022 de **São José do Cedro** como
"parecer pela rejeição". Fomos ao DOTC-e original: **as duas são APROVAÇÃO**. O
que engana o classificador é a fórmula padrão do parecer, que cita a palavra
"rejeição" justamente para afastá-la — *"as restrições não são consideradas
gravíssimas, não podendo, portanto, ensejar a rejeição das contas"*. **Nunca
publique "contas rejeitadas" sem abrir a edição do DOTC-e e ler o dispositivo.**
No mesmo lote, o único caso de rejeição real é o de **Tijucas** (exercício de
2024, Parecer Prévio n. 283/2025) — e esse foi conferido no original.

**Segunda armadilha: o rótulo "ACP ajuizada".** Em Tijucas, 22 procedimentos
vinham marcados como ACP; **só 10** dizem no texto que o MP ajuizou ação. Os
outros dizem *"inexistência de fundamento para ajuizamento"* e terminam em
arquivamento. Mesmo padrão, menor escala, em Nova Veneza e Itapoá.

**Placar da primeira armadilha até aqui: seis falsos contra três verdadeiros.**
Pareceres prévios rotulados como **"rejeição"** que na verdade são **APROVAÇÃO**:
dois em **Mafra** (exercícios 2023 e 2024), dois em **Guaraciaba** (2021 e 2022)
e dois em **Itaiópolis** (2023 e 2024). As rejeições reais, conferidas no
original, são três: **Tijucas** (2024, PP 283/2025), **Aurora** (2024, PP
263/2025) e **São José** (2024, PP 269/2025). **Nunca publique rejeição sem abrir
o `EMITE PARECER` no DOTC-e.**

**Mafra é o caso-escola da primeira armadilha.** Dois pareceres prévios do
município aparecem na base como **"parecer pela rejeição"** e os dois são
**APROVAÇÃO** — exercícios 2023 e 2024. A fórmula padrão do voto diz que as
restrições *"não são consideradas gravíssimas… não podendo, portanto, ensejar a
rejeição das contas prestadas"*, e o classificador lê "rejeição". No mesmo lote,
**Aurora tinha uma rejeição de verdade** (exercício 2024) e **São José** outra
(2024). **Nunca publique rejeição sem abrir o `EMITE PARECER` no DOTC-e.**

**Terceira: a decisão que muda depois.** Em Tijucas, o TCE imputou a Elói Mariano
Rocha um débito de R$ 70.140,00 (Acórdão 354/2024) e **cancelou esse débito em
recurso** em 12/12/2025. Contar só a primeira metade seria o erro mais grave
possível aqui. **Sempre procure o REC com o mesmo número de processo de origem.**

**Quarta: valores de outra cidade colados no bloco.** Além do padrão já conhecido,
apareceram aqui Notificações de Alerta inteiras coladas ao fim da decisão —
Otacílio Costa em Nova Veneza, Ponte Serrada, Joinville e Papanduva em Itapoá — e,
em Tijucas, **seis blocos** cujo campo "Decisão" traz portarias e contratos
internos do próprio Tribunal de Contas (compra de ar-condicionado, aditivo de
elevador, palestra). Todo valor em reais precisa ser conferido contra a unidade
gestora antes de virar post.

## Lote de 29/09/2026 — nove cidades

Os PDFs `*-casos-investigacoes.pdf` de Presidente Nereu, Lontras, Balneário
Camboriú, Itapiranga, Águas Frias, Modelo, Saltinho, Irani e Catanduvas estão no
layout compacto de `gen_graves_md.py`. Lontras e Itapiranga foram reutilizados;
os outros sete foram escritos a partir dos resumos por cidade, com consulta ao
dispositivo original nos casos de desfecho duvidoso. O recorte é por **data da
edição**, desde 29/09/2022. O acervo local consultado termina em agosto de 2026:
o lote não declara cobertura exaustiva até 29/09/2026.

Os arquivos novos de Balneário Camboriú substituem, para distribuição, o antigo
`balneario-camboriu-casos-graves.pdf`; o Markdown antigo permanece como histórico.
Casos com recursos ou decisões posteriores foram resumidos pelo desfecho mais
recente localizado. Atenção às correções verificadas: os pareceres das contas de
2023 e 2024 de **Modelo** recomendam **aprovação**, apesar do rótulo bruto de
rejeição; em **Catanduvas**, o recurso REC 24/00113500 afastou as multas da REP
23/80044737 e a REP 16/00206627 terminou prescrita em 2025. A representação
sobre o pregão de uniformes de **Presidente Nereu** teve cautelar **indeferida**
em 2025 e julgamento de procedência em 2026. Esses desfechos prevalecem sobre
os rótulos automáticos.
