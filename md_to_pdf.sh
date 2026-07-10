#!/usr/bin/env bash
# Converte arquivos markdown em PDFs estilizados usando pandoc + Chrome headless.
# Uso: ./md_to_pdf.sh arquivo1.md arquivo2.md ...

set -euo pipefail

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS=$(cat <<'EOF'
@page {
  size: A4;
  margin: 18mm 16mm 18mm 16mm;
  @bottom-right { content: counter(page) " / " counter(pages); }
}
body {
  font-family: -apple-system, "Helvetica Neue", "Segoe UI", Roboto, sans-serif;
  font-size: 11pt;
  line-height: 1.45;
  color: #222;
  max-width: 100%;
}
h1 {
  font-size: 22pt;
  color: #0b3a66;
  border-bottom: 3px solid #0b3a66;
  padding-bottom: 6px;
  margin-top: 0;
}
h2 {
  font-size: 16pt;
  color: #0b3a66;
  border-bottom: 1px solid #c2d3e3;
  padding-bottom: 4px;
  margin-top: 28px;
  page-break-after: avoid;
}
h3 {
  font-size: 13pt;
  color: #344;
  margin-top: 18px;
  page-break-after: avoid;
}
h4 {
  font-size: 11.5pt;
  color: #555;
  margin-top: 12px;
}
hr {
  border: none;
  border-top: 1px dashed #c8c8c8;
  margin: 14px 0;
}
blockquote {
  border-left: 4px solid #fbbf24;
  background: #fef9e7;
  padding: 6px 12px;
  margin: 10px 0;
  font-size: 10.5pt;
}
code {
  background: #f1f1f1;
  padding: 1px 4px;
  border-radius: 3px;
  font-family: "SF Mono", "Menlo", monospace;
  font-size: 10pt;
}
pre {
  background: #f6f8fa;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 9.5pt;
}
table {
  border-collapse: collapse;
  width: 100%;
  margin: 10px 0;
  font-size: 10pt;
}
th, td {
  border: 1px solid #ddd;
  padding: 6px 8px;
  text-align: left;
  vertical-align: top;
}
th {
  background: #0b3a66;
  color: #fff;
  font-weight: 600;
}
tr:nth-child(even) td { background: #fafafa; }
a { color: #0b66c3; text-decoration: none; }
strong { color: #000; }
ul, ol { padding-left: 20px; }
li { margin: 2px 0; }
hr + h2, hr + h3 { page-break-before: auto; }
.page-break { page-break-after: always; }
EOF
)

for src in "$@"; do
  if [ ! -f "$src" ]; then
    echo "ERRO: arquivo nao existe: $src" >&2
    continue
  fi
  base="${src%.md}"
  html_tmp="${base}.html"
  pdf_out="${base}.pdf"

  echo "→ Convertendo $src ..."

  # Gera HTML standalone com CSS embutido
  pandoc "$src" \
    --from=gfm \
    --to=html5 \
    --standalone \
    --metadata title:"$(basename "$base")" \
    --metadata lang:pt-BR \
    -H <(printf '<meta charset="utf-8"><style>%s</style>' "$CSS") \
    -o "$html_tmp"

  # HTML → PDF via Chrome headless
  abs_html="$(cd "$(dirname "$html_tmp")" && pwd)/$(basename "$html_tmp")"
  "$CHROME" \
    --headless=new \
    --disable-gpu \
    --no-pdf-header-footer \
    --print-to-pdf-no-header \
    --print-to-pdf="$pdf_out" \
    "file://$abs_html" 2>/dev/null

  rm -f "$html_tmp"
  echo "  ✓ $pdf_out ($(du -h "$pdf_out" | cut -f1))"
done
