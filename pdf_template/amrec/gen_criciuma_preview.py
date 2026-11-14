#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Preview de Criciúma com título/descrição/status reescritos por leitura editorial
(Claude), em vez dos campos derivados por regex. Piloto para validar o formato antes
de rodar nas 12 cidades da AMREC.

Correções nesta versão:
- Remove casos que só caíram em Criciúma por causa da comarca judicial (ex.: um
  caso da Prefeitura de Nova Veneza que tramita na comarca de Criciúma) — ver
  mask em /tmp/criciuma_mp_city_mask.json, gerado com a mesma prioridade
  (menção explícita > comarca) já corrigida em build_regioes.py.
- Casos de severidade "alta" ganham destaque visual (fundo + selo CASO GRAVE).
- A referência embaixo de cada card virou uma citação de fonte de verdade, com
  link direto e verificado (HTTP 200) para a edição do Diário Oficial.
"""
import json, os
from gen_amrec import CITY_COLOR, FINANCAS, IMGS, fmt_brl, fmt_pop, esc
from gen_amrec_full import pill_cls

ASSETS = "./assets"
CITY = "Criciúma"
SCRATCH = "/private/tmp/claude-501/-Users-jairofortunato-mp/e0df0885-a2e2-4707-a4fc-3eee743e938d/scratchpad"

MESES_PT = {1:"JAN",2:"FEV",3:"MAR",4:"ABR",5:"MAI",6:"JUN",7:"JUL",8:"AGO",9:"SET",10:"OUT",11:"NOV",12:"DEZ"}

raw = json.load(open("/tmp/criciuma_raw.json"))
mp_curated = json.load(open(os.path.join(SCRATCH, "mp_curated_all_fixed.json")))
tce_curated = json.load(open(os.path.join(SCRATCH, "tce_curated_0.json"))) + \
              json.load(open(os.path.join(SCRATCH, "tce_curated_1.json")))

def mp_source_link(ymd):
    y, m, d = ymd
    return f"https://www.mpsc.mp.br/documents/d/guest/do_mpsc_{y:04d}-{m:02d}-{d:02d}"

def tce_source_link(ymd):
    y, m, d = ymd
    return f"https://consulta.tce.sc.gov.br/Diario/dotc-e{y:04d}-{m:02d}-{d:02d}.pdf"

def build_cards(raw_list, curated_list, src):
    cards = []
    for r, c in zip(raw_list, curated_list):
        if not c.get("keep"):
            continue
        y, m, d = r["ymd"]
        dm = f"{d:02d} {MESES_PT.get(m,'')}" if m else ""
        if src == "MP":
            ref = r.get("ref", "")
            fonte_nome = "Diário Oficial Eletrônico do MPSC (DO-MPSC)"
            link = mp_source_link(r["ymd"]) if y else ""
        else:
            ref = r.get("ref", "").lstrip("⭐•· ").split(" — ")[0]
            fonte_nome = "Diário Oficial Eletrônico de Contas (DOTC-e/TCE-SC)"
            link = tce_source_link(r["ymd"]) if y else ""
        data_br = f"{d:02d}/{m:02d}/{y}" if y else "data não informada"
        fonte_html = (
            f'Fonte: {fonte_nome}, edição de {data_br} · Processo nº {esc(ref)}'
            + (f' · <a href="{link}">conferir a edição original</a>' if link else "")
        )
        cards.append({
            "ymd": r["ymd"], "dm": dm, "status": r["status"], "cls": pill_cls(r["status"]),
            "title": esc(c["title"]), "line": esc(c["description"]),
            "fonte_html": fonte_html,
            "src": src, "severity": c.get("severity", "media"),
        })
    return cards

cards = build_cards(raw["mp"], mp_curated, "MP") + build_cards(raw["tce"], tce_curated, "TCE")
cards.sort(key=lambda c: c["ymd"], reverse=True)
n_mp = sum(1 for c in cards if c["src"] == "MP"); n_tce = len(cards) - n_mp
n_alta = sum(1 for c in cards if c["severity"] == "alta")

def card_html(c, color):
    y = c["ymd"][0]
    src_badge = f'<span class="src {c["src"].lower()}">{c["src"]}</span>'
    sev_cls = " sev-alta" if c["severity"] == "alta" else ""
    sev_tag = '<span class="sev-tag">⬤ CASO GRAVE</span>' if c["severity"] == "alta" else ""
    return f'''<div class="case{sev_cls}">
      <div class="rail" style="--rc:{color}"><div class="yr">{y or ''}</div><div class="dm">{c["dm"]}</div></div>
      <div class="body">
        <div class="pl"><span class="pill {c['cls']}">{esc(c['status'])}</span>{src_badge}{sev_tag}</div>
        <h3>{c['title']}</h3>
        <div class="ln">{c['line']}</div>
        <div class="ref">{c['fonte_html']}</div>
      </div></div>'''

color = CITY_COLOR[CITY]; fin = FINANCAS.get(CITY, {})
imgs = IMGS.get(CITY, {})
flag = imgs.get("bandeira"); bras = imgs.get("brasao")
flag_html = f'<img class="c-flag" src="{flag}">' if flag else ''
bras_html = f'<img class="c-bras" src="{bras}">' if bras else ''
info = f'''<div class="cinfo">
    <div class="ci"><span class="cl">População</span><b>{fmt_pop(fin.get("pop",0))}</b><span class="cu">Censo 2022</span></div>
    <div class="ci"><span class="cl">Arrecadou 2025</span><b>{fmt_brl(fin.get("rec",0))}</b><span class="cu">receita realizada</span></div>
    <div class="ci"><span class="cl">Gastou 2025</span><b>{fmt_brl(fin.get("desp",0))}</b><span class="cu">despesa empenhada</span></div>
  </div>''' if fin else ''

body = f'''<section class="cityblock" style="--city:{color}">
  <div class="cityhead">
    <div class="h-t"><div class="small">Região Carbonífera · AMREC</div><div class="big">{esc(CITY)}</div></div>
    <img class="h-logo" src="{ASSETS}/logo-preto.png">
  </div>
  <div class="csymbols">{flag_html}{bras_html}{info}</div>
  <div class="ccount">{len(cards)} casos selecionados (revisão editorial) · {n_mp} do Ministério Público · {n_tce} do Tribunal de Contas · {n_alta} marcados como grave</div>
  {"".join(card_html(c, color) for c in cards)}
</section>'''

CSS = open(os.path.join(os.path.dirname(__file__), "amrec_full_css.css")).read()
cover = open(os.path.join(os.path.dirname(__file__), "amrec_cover.html")).read()
cta = open(os.path.join(os.path.dirname(__file__), "amrec_cta.html")).read()

out = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>{cover}<div class="doc">{body}</div>{cta}</body></html>"""

open(os.path.join(os.path.dirname(__file__), "criciuma_preview.html"), "w").write(out)
print(f"criciuma_preview.html gerado: {len(cards)} casos ({n_mp} MP + {n_tce} TCE), {n_alta} graves")
