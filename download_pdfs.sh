#!/usr/bin/env bash
set -u

DT_INICIO="${DT_INICIO:-2026-01-01}"
DT_FIM="${DT_FIM:-2026-05-20}"
OUT_DIR="${OUT_DIR:-$(dirname "$0")/pdfs}"
INDEX_URL="https://intranet.mpsc.mp.br/spo/diariooficial/index"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
PARALLEL="${PARALLEL:-6}"

mkdir -p "$OUT_DIR"
LIST="$(mktemp)"
trap 'rm -f "$LIST"' EXIT

echo "Buscando edições entre $DT_INICIO e $DT_FIM..."
curl -sSL -A "$UA" \
  "${INDEX_URL}?dt_inicio=${DT_INICIO}&dt_fim=${DT_FIM}&orgao=-1&tipo=-1&q=" \
  | grep -oE 'https://www\.mpsc\.mp\.br/documents/d/guest/do_mpsc_[A-Za-z0-9._-]+' \
  | sort -u > "$LIST"

TOTAL=$(wc -l < "$LIST" | tr -d ' ')
echo "Encontradas $TOTAL edições. Baixando em $OUT_DIR (paralelismo=$PARALLEL)..."

fetch_one() {
  local url="$1"
  local name
  name="$(basename "$url").pdf"
  local dest="$OUT_DIR/$name"
  if [ -s "$dest" ]; then
    echo "skip   $name"
    return 0
  fi
  if curl -fsSL -A "$UA" -o "$dest.part" "$url"; then
    mv "$dest.part" "$dest"
    local size
    size=$(stat -f%z "$dest" 2>/dev/null || stat -c%s "$dest")
    echo "ok     $name ($size bytes)"
  else
    rm -f "$dest.part"
    echo "FAIL   $name" >&2
    return 1
  fi
}
export -f fetch_one
export OUT_DIR UA

xargs -I{} -P "$PARALLEL" bash -c 'fetch_one "$@"' _ {} < "$LIST"

DOWNLOADED=$(ls -1 "$OUT_DIR"/*.pdf 2>/dev/null | wc -l | tr -d ' ')
echo "---"
echo "Concluído: $DOWNLOADED PDFs em $OUT_DIR"
