#!/usr/bin/env bash
# Baixa edições do Diário Oficial Eletrônico do TCE/SC (DOTC-e).
# Por padrão: abril e maio de 2026.
# Uso:
#   ./download_pdfs.sh                     -> abr+mai/2026
#   YEAR=2026 MONTHS="04 05" ./download_pdfs.sh
#   YEAR=2026 MONTHS="06" ./download_pdfs.sh

set -u

YEAR="${YEAR:-2026}"
MONTHS="${MONTHS:-04 05}"
OUT_DIR="${OUT_DIR:-$(dirname "$0")/pdfs}"
BASE="https://consulta.tce.sc.gov.br/Diario/dotc-e"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
PARALLEL="${PARALLEL:-6}"

mkdir -p "$OUT_DIR"
LIST="$(mktemp)"
trap 'rm -f "$LIST"' EXIT

# Gera todos os dias (DOTC-e é publicado em dias úteis; 404 filtra automaticamente)
for m in $MONTHS; do
  case "$m" in
    01|03|05|07|08|10|12) days=31 ;;
    04|06|09|11)          days=30 ;;
    02)
      if (( YEAR % 4 == 0 && (YEAR % 100 != 0 || YEAR % 400 == 0) )); then days=29; else days=28; fi ;;
    *) echo "mês inválido: $m" >&2; exit 1 ;;
  esac
  for d in $(seq -w 1 $days); do
    echo "${BASE}${YEAR}-${m}-${d}.pdf"
    echo "${BASE}${YEAR}-${m}-${d}-E.pdf"   # extraordinárias
  done
done > "$LIST"

TOTAL=$(wc -l < "$LIST" | tr -d ' ')
echo "Testando $TOTAL URLs (regulares + extraordinárias) em $OUT_DIR..."

fetch_one() {
  local url="$1"
  local name
  name="$(basename "$url")"
  local dest="$OUT_DIR/$name"
  if [ -s "$dest" ]; then
    echo "skip  $name"; return 0
  fi
  local code
  code=$(curl -fsSL -A "$UA" -w "%{http_code}" -o "$dest.part" "$url" 2>/dev/null) || code=000
  if [ -s "$dest.part" ] && head -c 4 "$dest.part" | grep -q "%PDF"; then
    mv "$dest.part" "$dest"
    local size
    size=$(stat -f%z "$dest" 2>/dev/null || stat -c%s "$dest")
    echo "OK    $name ($size bytes)"
  else
    rm -f "$dest.part"
    # silencioso: 404 é esperado em finais de semana e feriados
    return 0
  fi
}
export -f fetch_one
export OUT_DIR UA

xargs -I{} -P "$PARALLEL" bash -c 'fetch_one "$@"' _ {} < "$LIST" | grep -v "^skip"

DOWNLOADED=$(ls -1 "$OUT_DIR"/*.pdf 2>/dev/null | wc -l | tr -d ' ')
echo "---"
echo "Concluído: $DOWNLOADED PDFs em $OUT_DIR"
