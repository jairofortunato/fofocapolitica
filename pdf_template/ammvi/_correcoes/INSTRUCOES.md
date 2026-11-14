# Correções da AMMVI — instruções para o executor

A curadoria da AMMVI está mecanicamente correta (47/47 lotes, alinhamento
perfeito), mas a auditoria encontrou três defeitos de conteúdo. As listas neste
diretório dizem exatamente onde estão.

**Você edita apenas arquivos em `pdf_template/ammvi/_lotes_curados/`.** Cada
entrada das listas traz `lote` (nome do arquivo) e `pos_no_lote` (índice no array
daquele arquivo), além de `i` e `tipo` para conferência. Mantenha tamanho, ordem,
`i` e `tipo` de cada arquivo intactos — o casamento com o bruto é posicional e um
deslocamento faz o PDF atribuir a conduta de um investigado a outra pessoa.

## item1.json — 28 cards do TCE sem dispositivo

Cards que afirmam desfecho sem a decisão estar na fonte. A maioria é prestação de
contas com "parecer pela aprovação" — ou seja, o erro favorece o gestor.

**Ação: `keep: false` em todos os 28.** Pode zerar `title`, `description` e
`status`, e deixar `severity: "media"`.

A regra é simétrica e vale para qualquer classe processual: **sem `dispositivo`,
não se afirma nem aprovação nem rejeição.** O campo `status` do bruto vem de um
classificador por palavra-chave e erra muito — nunca use ele como fonte.

## item2.json — 13 selos fora da tabela

`⬛ decisão singular` (11 em Blumenau) e `⬛ acórdão (decisão)` (2 em Brusque) não
existem no `CURADORIA.md`: descrevem a forma processual, não o desfecho. O leitor
não aprende nada com "decisão singular".

**Ação:** o campo `dispositivo` está na própria lista. Leia e escolha o selo real
da tabela. Se o dispositivo não permitir afirmar desfecho, use `❔ em tramitação`
e diga na descrição que o desfecho não consta. Ajuste o título junto.

## item3.json — 184 cards do MP a revisar (o mais grave)

Cards publicados cuja fonte não diz o que se apura. Exemplo real, publicado como
CASO GRAVE:

> título: "MP ajuiza ACP em Brusque envolvendo Hermenegildo Dalcegio"
> descrição: "O inquérito civil apurou supostas irregularidades envolvendo o
> Município de Brusque e Hermenegildo Dalcegio."
> fonte inteira: "Município de Brusque e Hermenegildo Dalcegio. Conclusão:
> propositura de Ação Civil Pública."

A fonte não diz nada sobre o que a pessoa fez. "Supostas irregularidades" é
enchimento, não informação. Isso põe o nome de um cidadão real ao lado de um selo
de improbidade e do selo CASO GRAVE, sem uma linha que o leitor possa conferir.

**Esta lista é triagem por tamanho de fonte, não veredito. Leia cada caso.**

Critério de decisão, um por card:

- Se você **não consegue escrever numa frase o que a pessoa ou o órgão fez**,
  usando só o que está em `fonte_completa` → `keep: false`.
- Se a fonte diz o que aconteceu, mesmo sendo curta → mantenha, e corrija a
  descrição para dizer isso em vez de "supostas irregularidades".
- Nunca complete a lacuna com linguagem genérica. Cortar é sempre melhor que
  publicar algo inconferível sobre pessoa nomeada.

O `CURADORIA.md` é explícito: quando o texto é vago demais para dizer honestamente
o que aconteceu, é melhor cortar do que publicar algo que o leitor não consegue
conferir. Isso vale tanto para instaurações quanto para conclusões.

## Ao terminar

```bash
cd /Users/jairofortunato/mp/pdf_template
python3 assemble_curated.py ammvi --lotes ammvi/_lotes_curados
python3 check_conselheiros.py ammvi
python3 gen_dossie.py ammvi
```

Relate: quantos cards saíram em cada item, e a saída dos três comandos.
