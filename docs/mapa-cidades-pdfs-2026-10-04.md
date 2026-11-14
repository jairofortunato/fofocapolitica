# Cidades de Santa Catarina ainda sem PDF — 04/10/2026

Fonte dos 295 municípios: [API de Localidades do IBGE](https://servicodados.ibge.gov.br/api/v1/localidades/estados/42/municipios), consultada em 04/10/2026. A lista local de regiões (`build_regioes.py`) foi comparada à lista oficial; os 295 nomes coincidem após normalização de acentos e pontuação.

O [índice dos PDFs](../PDFS-CIDADES-CONSOLIDADOS/INDICE.csv) reúne 268 arquivos diferentes. O nome de cada arquivo foi associado a um município, contando versões diferentes da mesma cidade uma única vez.

| Situação | Municípios |
|---|---:|
| Com ao menos um PDF em que o bloco eleitoral foi detectado | 105 |
| Com PDF, mas sem o bloco eleitoral detectado em nenhum | 73 |
| **Sem nenhum PDF de cidade no acervo consolidado** | **117** |

## Sem nenhum PDF (117)

| Região | Qtd. | Municípios |
|---|---:|---|
| Grande Florianópolis / GRANFPOLIS | 7 | Antônio Carlos, Angelina, Alfredo Wagner, Leoberto Leal, Major Gercino, Rancho Queimado, São Pedro de Alcântara |
| Oeste / AMOSC | 18 | Águas de Chapecó, Caxambu do Sul, Cordilheira Alta, Coronel Freitas, Formosa do Sul, Guatambú, Irati, Jardinópolis, Nova Erechim, Nova Itaberaba, Planalto Alegre, Quilombo, Santiago do Sul, Serra Alta, Sul Brasil, União do Oeste, Arvoredo, Paial |
| Alto Vale do Itajaí / AMAVI | 13 | Agronômica, Atalanta, Braço do Trombudo, Chapadão do Lageado, Dona Emma, José Boiteux, Laurentino, Mirim Doce, Petrolândia, Pouso Redondo, Rio do Campo, Santa Terezinha, Trombudo Central |
| Alto Vale do Rio do Peixe / AMARP | 10 | Arroio Trinta, Calmon, Ibiam, Iomerê, Lebon Régis, Macieira, Matos Costa, Pinheiro Preto, Rio das Antas, Salto Veloso |
| Alto Irani / AMAI | 12 | Bom Jesus, Entre Rios, Faxinal dos Guedes, Ipuaçu, Lajeado Grande, Marema, Ouro Verde, Passos Maia, Ponte Serrada, São Domingos, Vargeão, Xaxim |
| Alto Uruguai Catarinense / AMAUC | 8 | Alto Bela Vista, Arabutã, Jaborá, Lindóia do Sul, Peritiba, Piratuba, Presidente Castello Branco, Xavantina |
| Extremo Oeste / AMEOSC | 13 | Anchieta, Bandeirante, Barra Bonita, Belmonte, Dionísio Cerqueira, Iporã do Oeste, Mondaí, Palma Sola, Paraíso, Princesa, Santa Helena, São João do Oeste, Tunápolis |
| Entre Rios / AMERIOS | 13 | Bom Jesus do Oeste, Caibi, Campo Erê, Cunhataí, Flor do Sertão, Iraceminha, Palmitos, Riqueza, Romelândia, Santa Terezinha do Progresso, São Miguel da Boa Vista, Saudades, Tigrinhos |
| Foz do Rio Itajaí / AMFRI | 1 | Bombinhas |
| Meio Oeste / AMMOC | 7 | Erval Velho, Herval d'Oeste, Ibicaré, Lacerdópolis, Luzerna, Ouro, Vargem Bonita |
| Noroeste / AMNOROESTE | 4 | Coronel Martins, Galvão, Jupiá, Novo Horizonte |
| Planalto Norte / AMPLANORTE | 2 | Canoinhas, Papanduva |
| Planalto Sul / AMPLASC | 6 | Abdon Batista, Brunópolis, Celso Ramos, Monte Carlo, Vargem, Zortéa |
| Contestado / AMURC | 3 | Frei Rogério, Ponte Alta do Norte, São Cristóvão do Sul |

## Com PDF, mas sem identificação eleitoral detectada (73)

Estas cidades têm ao menos um PDF no acervo, porém nenhum deles passou no teste textual do bloco eleitoral exigido pelo projeto. Não são contadas entre as 117 sem PDF.

| Região | Qtd. | Municípios |
|---|---:|---|
| Carbonífera / AMREC | 8 | Balneário Rincão, Cocal do Sul, Criciúma, Forquilhinha, Orleans, Siderópolis, Treviso, Urussanga |
| Extremo Sul / AMESC | 10 | Balneário Gaivota, Ermo, Maracajá, Meleiro, Morro Grande, Passo de Torres, Santa Rosa do Sul, São João do Sul, Sombrio, Timbé do Sul |
| Tubarão-Laguna / AMUREL | 16 | Armazém, Braço do Norte, Capivari de Baixo, Grão-Pará, Gravatal, Imaruí, Jaguaruna, Laguna, Pescaria Brava, Rio Fortuna, Sangão, Santa Rosa de Lima, São Ludgero, São Martinho, Treze de Maio, Pedras Grandes |
| Oeste / AMOSC | 1 | Chapecó |
| Alto Vale do Itajaí / AMAVI | 1 | Presidente Getúlio |
| Extremo Oeste / AMEOSC | 1 | Descanso |
| Médio Vale do Itajaí / AMMVI | 12 | Apiúna, Ascurra, Benedito Novo, Botuverá, Brusque, Doutor Pedrinho, Gaspar, Guabiruba, Pomerode, Rio dos Cedros, Rodeio, Timbó |
| Nordeste / AMUNESC | 5 | Araquari, Balneário Barra do Sul, Campo Alegre, Rio Negrinho, São Francisco do Sul |
| Contestado / AMURC | 1 | Curitibanos |
| Serra Catarinense / AMURES | 16 | Anita Garibaldi, Bocaina do Sul, Bom Jardim da Serra, Bom Retiro, Campo Belo do Sul, Capão Alto, Cerro Negro, Correia Pinto, Painel, Palmeira, Ponte Alta, Rio Rufino, São Joaquim, São José do Cerrito, Urubici, Urupema |
| Vale do Itapocu / AMVALI | 2 | Corupá, Guaramirim |

## Critério de leitura

- “Tem PDF” indica existência de arquivo, não cobertura completa dos últimos quatro anos nem validação do conteúdo dos casos.
- A identificação eleitoral foi verificada por extração de texto da capa/contracapa; falhas de extração podem produzir falso negativo. Confira visualmente antes de distribuir.
- PDFs de diários oficiais brutos e peças intermediárias de diagramação não foram contados como dossiês de cidade.
- A [planilha completa dos 295 municípios](mapa-cidades-pdfs-2026-10-04.csv) informa região, número de PDFs, presença do bloco e nomes dos arquivos.
