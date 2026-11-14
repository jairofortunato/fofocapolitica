#!/bin/bash
# Benchmark de modelos baratos contra o padrão-ouro do rodeio__0 (curado e auditado).
# Uso: bash ammvi/_correcoes/bench.sh
set -a; . "$HOME/.env"; set +a
cd /Users/jairofortunato/mp
D=pdf_template/ammvi/_correcoes
for M in qwen/qwen3.7-flash z-ai/glm-4.7-flash google/gemini-2.5-flash-lite deepseek/deepseek-v4-flash; do
  SLUG=$(echo "$M" | tr '/.' '__')
  echo "=== $M"
  opencode run --dir /Users/jairofortunato/mp -m "$M" "Você é curador editorial do dossiê 'Fofoca Política: Transparência Radical'.

Leia pdf_template/CURADORIA.md (critério completo) e cure pdf_template/ammvi/_lotes/rodeio__0.json.

Saída: JSON array do MESMO tamanho e MESMA ordem, cada item {\"i\",\"tipo\",\"keep\",\"title\",\"description\",\"status\",\"severity\"}, com \"i\" e \"tipo\" copiados da entrada. NUNCA reordene, omita ou acrescente item.

Regras que mais pegam:
- Caso do TCE sem o campo 'decisao' nao vira card afirmando desfecho (nem aprovacao nem rejeicao): keep=false.
- Arquivamento de PAP ou por seletividade e '❔ nao conhecido (sem analise)', nao '🟢 julgado regular'.
- Consulta ao TCE nao e julgamento sobre a cidade: corte.
- Fonte que nao diz o que a pessoa/orgao fez: keep=false. Nunca escreva 'supostas irregularidades'.
- severity alta so com multa, dano ao erario, improbidade ajuizada, fraude em licitacao ou nepotismo confirmado.

Grave em $D/teste_$SLUG.json e nao escreva em mais nenhum arquivo." > "$D/log_$SLUG.txt" 2>&1
done
echo "=== comparando com o padrão-ouro ==="
python3 pdf_template/ammvi/_correcoes/compara.py
