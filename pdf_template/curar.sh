#!/bin/bash
# Dispara a curadoria editorial de lotes via opencode, um agente por grupo de lotes.
#
# Uso:  bash curar.sh <sigla> <lotes-por-agente> <lote1> <lote2> ...
#       bash curar.sh amunesc 3 joinville__0.json joinville__1.json ...
#       bash curar.sh amunesc 3 --faltando        # todos os lotes ainda sem curadoria
#
# O modelo vem de CURAR_MODEL (padrão gpt-5.4-mini, escolhido em teste cego contra
# o padrão-ouro do rodeio__0: alinhamento intacto, zero selo inválido, zero falso
# negativo). A chave sai de ~/.env porque o shell não-interativo não roda o .zshrc.
set -euo pipefail
REPO=/Users/jairofortunato/mp
cd "$REPO"
set -a; . "$HOME/.env"; set +a
MODEL="${CURAR_MODEL:-openai/gpt-5.4-mini}"

SIGLA="$1"; POR="$2"; shift 2
LOTES=("$@")
if [ "${LOTES[0]}" = "--faltando" ]; then
  LOTES=()
  for p in pdf_template/"$SIGLA"/_lotes/*__*.json; do
    n=$(basename "$p")
    [ -f "pdf_template/$SIGLA/_lotes_curados/$n" ] || LOTES+=("$n")
  done
fi
echo "modelo: $MODEL | região: $SIGLA | lotes: ${#LOTES[@]} | por agente: $POR"
[ "${#LOTES[@]}" -eq 0 ] && { echo "nada a fazer"; exit 0; }

LOG=pdf_template/"$SIGLA"/_logs; mkdir -p "$LOG"
i=0; grupo=()
disparar() {
  [ "${#grupo[@]}" -eq 0 ] && return
  local lista=""; for l in "${grupo[@]}"; do lista="$lista
  - pdf_template/$SIGLA/_lotes/$l"; done
  local tag; tag=$(echo "${grupo[0]}" | sed 's/\.json//')
  opencode run --dir "$REPO" -m "$MODEL" "Você é curador editorial do dossiê \"Fofoca Política: Transparência Radical\".

PRIMEIRO leia pdf_template/CURADORIA.md — é o critério completo e obrigatório.

Seus lotes, nesta ordem:$lista

Para cada lote:
- Leia o arquivo ({\"cidade\":..., \"casos\":[...]}) e julgue CADA caso individualmente, lendo a fonte. Nunca decida por padrão de texto.
- Casos \"tipo\":\"tce\" trazem \"decisao\" (dispositivo do acórdão): o desfecho e o selo saem DELE, nunca do campo \"status\" bruto, que vem de um classificador por palavra-chave e erra muito.
- Saída: JSON array do MESMO tamanho e MESMA ordem de \"casos\". Cada item: {\"i\",\"tipo\",\"keep\",\"title\",\"description\",\"status\",\"severity\"}, com \"i\" e \"tipo\" copiados da entrada. NUNCA reordene, omita ou acrescente item — o casamento é posicional e um deslocamento atribui a conduta de um investigado a outra pessoa.
- Grave cada lote em pdf_template/$SIGLA/_lotes_curados/<mesmo nome> ASSIM QUE terminar, antes de começar o próximo.

As cinco regras que mais pegam:
1. Caso do TCE sem \"decisao\" não vira card afirmando desfecho, nem aprovação nem rejeição: keep=false. A regra é simétrica.
2. Arquivamento de PAP, ou por seletividade/intempestividade, é \"❔ não conhecido (sem análise)\" — não \"🟢 julgado regular\": ninguém julgou o mérito.
3. Consulta (CON) respondida pelo TCE não é julgamento sobre a cidade: corte.
4. Fonte que não diz o que a pessoa ou o órgão fez: keep=false. Nunca escreva \"supostas irregularidades\" para preencher a lacuna — nomear alguém como investigado sem dizer do quê é o pior erro possível aqui.
5. Fases do MESMO processo compartilham o número (PAP 22/80059813 e REP 22/80059813; PAF 24/80026196 e RLI 24/80026196). Publique só a fase mais avançada e corte as anteriores e as republicações idênticas.

severity \"alta\" só com multa aplicada, dano ao erário, improbidade ajuizada, fraude em licitação, nepotismo confirmado ou prejuízo direto a serviço essencial. Caso arquivado por falta de provas nunca é alta.

Registro previdenciário de rotina (aposentadoria/pensão julgada legal) é keep=false. Caso cujo dispositivo trata de outro município não entra no dossiê desta cidade.

Este é trabalho editorial próprio: NÃO leia curadoria pronta de outras regiões para copiar julgamento.

Ao final relate, por lote: quantos casos, quantos keep:true, quantos severity alta." > "$LOG/$tag.log" 2>&1 &
  grupo=()
}
for l in "${LOTES[@]}"; do
  grupo+=("$l"); i=$((i+1))
  [ $((i % POR)) -eq 0 ] && disparar
done
disparar
wait
echo "=== leva concluída ==="
for p in pdf_template/"$SIGLA"/_lotes/*__*.json; do
  n=$(basename "$p"); [ -f "pdf_template/$SIGLA/_lotes_curados/$n" ] || echo "  ainda falta: $n"
done
