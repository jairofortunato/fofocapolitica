# Modelo "Transparência Radical" — como gerar o PDF

Estilo APROVADO em 08/07/2026. Não mudar o visual sem combinar.

## Arquivos
- `modelo-transparencia-radical.html` — o layout (capa + identidade da cidade + linha do tempo + CTA)
- `assets/` — fontes (Anton/Archivo), logos JAIRO, foto sem fundo, bandeira/brasão

## Gerar o PDF
```bash
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf-no-header \
  --allow-file-access-from-files \
  --print-to-pdf="saida.pdf" "file://$PWD/modelo-transparencia-radical.html"
```

## Link do WhatsApp (contracapa)
Trocar `https://chat.whatsapp.com/SUBSTITUA_PELO_LINK_DO_GRUPO` no HTML pelo link real.
Links `<a href>` viram clicáveis no PDF automaticamente. Recomendado: usar link fixo
(wa.me/NÚMERO ou encurtador redirecionável) porque link de grupo pode expirar.

## Regras de conteúdo
- Linguagem simples, sem juridiquês. Estrutura de cada caso: "o que aconteceu / quem / em que pé está".
- Ordenar por cidade → por data (mais recente primeiro).
- Selos: 🔴 irregularidade encontrada · 🟢 investigado e arquivado · ⬛ TCE (já tem decisão).
- Prefeito/vereadores/bandeira/brasão são dados reais (web) — NUNCA inventar nomes.
