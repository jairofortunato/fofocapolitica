# Critério editorial — Fofoca Política: Transparência Radical

Guia para a revisão editorial dos casos. Cada caso bruto do Diário Oficial é
**lido e reescrito**. Nunca por regex ou palavra-chave — o julgamento é editorial.

## Entrada

Um JSON com uma lista de casos. Cada um traz:
`i` (índice — preserve), `ref` (nº do processo), `header`, `status`, `data`,
`texto` (partes/objeto/decisão como saiu do Diário).

## Saída

Um JSON array **do mesmo tamanho e na mesma ordem da entrada** — o alinhamento é
posicional, então nunca reordene, omita nem acrescente entradas. Cada item:

```json
{"i": 0, "keep": true, "title": "...", "description": "...", "severity": "media"}
```

Para `keep: false`, os outros campos podem ficar vazios.

## Campos

**`keep`** — o caso entra no dossiê?
- `true`: tem interesse público real. Envolve dinheiro público, cargo público,
  serviço à população, conduta de agente político ou de servidor.
- `false`: puramente processual ou sem substância noticiável (mero despacho,
  redistribuição interna, prorrogação de prazo, caso sem qualquer detalhe do que
  se apura). Também `false` se o texto estiver tão truncado/vago que não dá para
  dizer honestamente o que aconteceu — é melhor cortar do que publicar algo que
  o leitor não consegue conferir.

**`title`** — manchete curta, no máximo ~90 caracteres.
- Linguagem de jornal, direta, sem jargão jurídico.
- **Sempre nomeie o órgão que agiu** (MP ou TCE) ou o alvo. Ex.: "TCE multa
  gestores do Criciúmaprev por irregularidade em aposentadoria".
- Se o caso terminou inocentando alguém, o título tem que dizer isso. Ex.:
  "Servidor de Criciúma foi investigado por uso indevido de carro oficial, mas MP
  arquivou o caso". Nunca escreva um título que sugira culpa quando o processo
  concluiu o contrário.

**`description`** — 2 a 4 frases, linguagem simples.
- O que aconteceu, quem está envolvido, e **qual o status atual**: está em
  apuração? foi arquivado? por quê? houve multa, acordo, ação na Justiça?
- Termine deixando claro em que pé está.
- Não invente detalhes que não estão no texto de origem. Se o valor, o nome ou o
  desfecho não constam, não os afirme.

**`status`** — o selo que aparece no card, ao lado da manchete.

O dado bruto traz um `status` vindo de um classificador por palavra-chave do
scrape, e **ele erra**: há casos rotulados "ACP ajuizada" cujo texto diz que o
processo foi arquivado sem responsabilizar ninguém. O selo é o elemento mais
visível do card, então ele tem que sair da mesma leitura que produziu o título —
nunca do rótulo bruto. Se o rótulo contradisser o texto, **o texto vence**.

Escolha um destes (copie exatamente, com o emoji):

| MP | TCE |
|---|---|
| `🟡 em apuração` | `⬛ julgado irregular` |
| `🟢 arquivado` | `⬛ julgado irregular + multa` |
| `🟢 recomendação cumprida` | `🔴 multa aplicada` |
| `🟠 TAC firmado` | `🔴 apontou irregularidade` |
| `🟠 ACNP firmado` | `🔴 parecer pela rejeição` |
| `🔴 ACP ajuizada` | `🟢 julgado regular` |
| `🔴 ADI ajuizada` | `🟢 parecer pela aprovação` |
| `⚫ prescrito` | `🟠 cautelar / sustação` |
| `❔ status indef.` | `🟡 em instrução (citação/audiência)` |
| | `⚫ prescrito` |
| | `❔ em tramitação` |
| | `❔ não conhecido (sem análise)` |

Use `❔ status indef.` / `❔ em tramitação` quando o texto não permitir afirmar o
desfecho. É preferível ao selo errado.

Três selos existem porque o desfecho real aparece com frequência e não cabia em
nenhum outro:
- `❔ não conhecido (sem análise)` — o TCE arquivou por seletividade ou
  intempestividade, sem julgar o mérito. Não é "regular" nem "irregular": ninguém
  examinou o caso.
- `🔴 ADI ajuizada` — o MP foi ao TJSC contra uma lei municipal. É ação na
  Justiça, mas não é ACP: não imputa conduta a ninguém, questiona a norma.
- `⚫ prescrito` vale para os dois órgãos. No TCE aparece quando o débito ou a
  multa é cancelada pelo tempo decorrido — o card precisa dizer que a
  responsabilização não chegou a ser decidida.

**`severity`** — `"alta"` ou `"media"`.
- `alta` (ganha selo "CASO GRAVE" e fundo destacado): desvio ou dano ao erário,
  improbidade com ação ajuizada, multa aplicada, fraude em licitação, nepotismo
  confirmado, prejuízo direto a serviço essencial (saúde, educação).
- `media`: todo o resto, inclusive o que foi apurado e arquivado.
- Um caso **arquivado por falta de provas não é `alta`** — a pessoa não foi
  responsabilizada.

## Cuidados

- É um documento público que nomeia pessoas reais. Descrever como condenado
  alguém que foi absolvido, ou como desvio o que foi arquivado, é o erro mais
  grave possível aqui. Na dúvida sobre o desfecho, descreva o que consta e diga
  que o desfecho não está claro.
- Preserve a distinção entre os órgãos: **MP investiga e pode processar; TCE
  julga contas e aplica multa.** Não troque um pelo outro.
- Texto cortado com "…" no fim é comum na origem. Trabalhe com o que dá para
  afirmar, ou marque `keep: false`.
