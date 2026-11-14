#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta o dossiê AMREC completo (12 cidades) com conteúdo curado por leitura
editorial (Claude), não por regex. Cada cidade vira um PDF próprio (com rodapé
estático "@page" mostrando o nome da cidade — Chrome headless não suporta
string-set/running headers dinâmicos, testado), depois tudo é mesclado num único
PDF final via pypdf: capa + 12 cidades (ordem ORDEM) + CTA.
"""
import json, os, re, subprocess, sys
from pypdf import PdfWriter

from gen_amrec import CITY_COLOR, FINANCAS, IMGS, fmt_brl, fmt_pop, esc, ORDEM
from gen_amrec_full import pill_cls

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = "./assets"
SCRATCH = os.path.join(HERE, "_curated_data")  # persistido no repo — o scratchpad de sessão some entre conversas
RAW_DIR = os.path.join(SCRATCH, "raw")
CURATED_DIR = os.path.join(SCRATCH, "curated")
OUT_DIR = os.path.join(HERE, "_build")
os.makedirs(OUT_DIR, exist_ok=True)

MESES_PT = {1:"JAN",2:"FEV",3:"MAR",4:"ABR",5:"MAI",6:"JUN",7:"JUL",8:"AGO",9:"SET",10:"OUT",11:"NOV",12:"DEZ"}
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = open(os.path.join(HERE, "amrec_full_css.css")).read()


def slugify(city):
    import unicodedata
    s = unicodedata.normalize('NFKD', city).encode('ascii', 'ignore').decode()
    return s.lower().replace(' ', '_')


def mp_source_link(ymd):
    y, m, d = ymd
    return f"https://www.mpsc.mp.br/documents/d/guest/do_mpsc_{y:04d}-{m:02d}-{d:02d}"


def tce_source_link(ymd):
    y, m, d = ymd
    return f"https://consulta.tce.sc.gov.br/Diario/dotc-e{y:04d}-{m:02d}-{d:02d}.pdf"


def build_cover_html(city):
    """Capa personalizada por cidade: H1 leva o nome da cidade (não mais 'AMREC'
    genérico), e a fileira de 12 bandeirinhas vira a bandeira+brasão só dessa
    cidade, já que cada PDF agora é o dossiê de uma cidade só."""
    cover_html = open(os.path.join(HERE, "amrec_cover.html")).read()
    imgs = IMGS.get(city, {})
    flag = imgs.get("bandeira"); bras = imgs.get("brasao")
    solo_imgs = "".join(
        f'<img src="{src}" alt="{esc(city)}">' for src in (flag, bras) if src
    )
    old_flags_block = re.search(r'<div class="cover-flags">.*?</div>', cover_html, re.S).group(0)
    old_region_block = re.search(r'<div class="cover-region">.*?</div>\s*</div>', cover_html, re.S).group(0)

    cover_html = cover_html.replace(
        "<h1>Fofoca<br><span class=\"l2\">Política</span><br>AMREC</h1>",
        f'<h1>Fofoca<br><span class="l2">Política</span><br>{esc(city)}</h1>',
    )
    cover_html = cover_html.replace(
        old_flags_block,
        f'<div class="cover-flags solo">{solo_imgs}</div>',
    )
    cover_html = cover_html.replace(
        old_region_block,
        '<div class="cover-region">\n'
        '        <div class="rlabel">Região Carbonífera · AMREC · 2022–2026</div>\n'
        f'        <div class="rcities">{esc(city)} é uma das 12 cidades cobertas pelo monitoramento Transparência Radical nesta região.</div>\n'
        '      </div>',
    )
    return cover_html


def build_cta_html(city):
    """Contracapa por cidade. O texto antes falava da região ('as 12 cidades da
    AMREC') — como cada PDF agora é o dossiê de uma cidade só, o placeholder
    {{CIDADE}} em amrec_cta.html é trocado pelo nome dela."""
    cta_html = open(os.path.join(HERE, "amrec_cta.html")).read()
    cta_html = cta_html.replace("{{CIDADE}}", esc(city))
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{cta_html}</body></html>"""


def load_raw(city):
    raw = json.load(open(os.path.join(RAW_DIR, f"{slugify(city)}.json")))
    if city == "Criciúma":
        # o piloto original (mp_curated_all_fixed.json, 223 entradas) foi curado
        # em cima do criciuma_raw_original.json de ANTES da correção de cidade —
        # a correção lá foi aplicada zerando "keep", não removendo a entrada. Pra
        # alinhar posicionalmente com esse curated, o raw MP também precisa ser
        # essa versão de 223, não o raw/criciuma.json (já refeito com 184).
        old_raw = json.load(open(os.path.join(SCRATCH, "criciuma_raw_original.json")))
        raw["mp"] = old_raw["mp"]
    return raw


def load_curated_for_city(city):
    """Retorna (mp_curated_by_ref, tce_curated_by_ref) pra essa cidade, lendo os
    arquivos certos do diretório curated/ conforme o layout de cada lote.

    Retorna LISTAS ordenadas (não dict por ref) porque alguns processos MP têm
    o mesmo número de processo em dois blocos distintos (instauração + conclusão
    do mesmo inquérito civil) — um dict por ref colidiria e perderia um dos dois.
    O alinhamento com o raw é posicional: mesma ordem de extração, filtrado por
    cidade/tipo preservando a ordem relativa.
    """

    def filt(records, tipo):
        return [r for r in records
                if r.get("tipo") == tipo and (not r.get("cidade") or r["cidade"] == city)]

    if city == "Criciúma":
        mp_list = json.load(open(os.path.join(CURATED_DIR, "..", "mp_curated_all_fixed.json")))
        tce_list = []
        for f in ("tce_curated_0.json", "tce_curated_1.json"):
            for r in json.load(open(os.path.join(CURATED_DIR, "..", f))):
                r = dict(r)
                r["ref"] = r["ref"].lstrip("⭐•· ").split(" — ")[0]
                tce_list.append(r)
    elif city == "Içara":
        mp_list = []
        for f in ("icara_mp_0.json", "icara_mp_1.json"):
            mp_list += json.load(open(os.path.join(CURATED_DIR, f)))
        tce_list = []
        for f in ("icara_tce_0.json", "icara_tce_1.json"):
            tce_list += json.load(open(os.path.join(CURATED_DIR, f)))
    elif city == "Urussanga":
        combined = []
        for f in ("urussanga_0.json", "urussanga_1.json"):
            combined += json.load(open(os.path.join(CURATED_DIR, f)))
        mp_list = filt(combined, "mp"); tce_list = filt(combined, "tce")
    elif city == "Orleans":
        combined = json.load(open(os.path.join(CURATED_DIR, "orleans_0.json")))
        mp_list = filt(combined, "mp"); tce_list = filt(combined, "tce")
    elif city == "Balneário Rincão":
        combined = json.load(open(os.path.join(CURATED_DIR, "rincao_0.json")))
        mp_list = filt(combined, "mp"); tce_list = filt(combined, "tce")
    elif city in ("Cocal do Sul", "Morro da Fumaça", "Siderópolis"):
        combined = json.load(open(os.path.join(CURATED_DIR, "small1_0.json")))
        mp_list = filt(combined, "mp"); tce_list = filt(combined, "tce")
    elif city in ("Forquilhinha", "Treviso"):
        combined = json.load(open(os.path.join(CURATED_DIR, "small2_0.json")))
        mp_list = filt(combined, "mp"); tce_list = filt(combined, "tce")
    elif city in ("Lauro Müller", "Nova Veneza"):
        combined = json.load(open(os.path.join(CURATED_DIR, "small3_0.json")))
        mp_list = filt(combined, "mp"); tce_list = filt(combined, "tce")
    else:
        raise ValueError(f"cidade sem mapeamento de curadoria: {city}")

    return mp_list, tce_list


def build_cards(city):
    raw = load_raw(city)
    mp_curated, tce_curated = load_curated_for_city(city)
    cards = []

    if len(raw["mp"]) != len(mp_curated):
        print(f"  [AVISO] {city}: raw MP={len(raw['mp'])} != curated MP={len(mp_curated)}", file=sys.stderr)
    if len(raw["tce"]) != len(tce_curated):
        print(f"  [AVISO] {city}: raw TCE={len(raw['tce'])} != curated TCE={len(tce_curated)}", file=sys.stderr)

    for r, c in zip(raw["mp"], mp_curated):
        if not c.get("keep"):
            continue
        y, m, d = r["ymd"]
        dm = f"{d:02d} {MESES_PT.get(m,'')}" if m else ""
        fonte_html = (
            f'Fonte: Diário Oficial Eletrônico do MPSC (DO-MPSC), edição de {d:02d}/{m:02d}/{y}'
            f' · Processo nº {esc(r["ref"])}'
            + (f' · <a href="{mp_source_link(r["ymd"])}">conferir a edição original</a>' if y else "")
        )
        cards.append({
            "ymd": r["ymd"], "dm": dm, "status": r["status"], "cls": pill_cls(r["status"]),
            "title": esc(c["title"]), "line": esc(c["description"]), "fonte_html": fonte_html,
            "src": "MP", "severity": c.get("severity", "media"),
        })
    for r, c in zip(raw["tce"], tce_curated):
        if not c.get("keep"):
            continue
        y, m, d = r["ymd"]
        dm = f"{d:02d} {MESES_PT.get(m,'')}" if m else ""
        fonte_html = (
            f'Fonte: Diário Oficial Eletrônico de Contas (DOTC-e/TCE-SC), edição de {d:02d}/{m:02d}/{y}'
            f' · Processo nº {esc(r["ref"])}'
            + (f' · <a href="{tce_source_link(r["ymd"])}">conferir a edição original</a>' if y else "")
        )
        cards.append({
            "ymd": r["ymd"], "dm": dm, "status": r["status"], "cls": pill_cls(r["status"]),
            "title": esc(c["title"]), "line": esc(c["description"]), "fonte_html": fonte_html,
            "src": "TCE", "severity": c.get("severity", "media"),
        })
    cards.sort(key=lambda c: c["ymd"], reverse=True)
    return cards


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


def build_city_html(city):
    cards = build_cards(city)
    n_mp = sum(1 for c in cards if c["src"] == "MP"); n_tce = len(cards) - n_mp
    n_alta = sum(1 for c in cards if c["severity"] == "alta")
    color = CITY_COLOR[city]; fin = FINANCAS.get(city, {})
    imgs = IMGS.get(city, {})
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
        <div class="h-t"><div class="small">Região Carbonífera · AMREC</div><div class="big">{esc(city)}</div></div>
        <img class="h-logo" src="{ASSETS}/logo-preto.png">
      </div>
      <div class="csymbols">{flag_html}{bras_html}{info}</div>
      <div class="ccount">{len(cards)} casos selecionados (revisão editorial) · {n_mp} do Ministério Público · {n_tce} do Tribunal de Contas · {n_alta} marcados como grave</div>
      {"".join(card_html(c, color) for c in cards)}
    </section>'''

    footer_css = f'''@page {{ size: A4; margin: 16mm 14mm 16mm 14mm;
      @bottom-left {{ content: "{city} · Região Carbonífera (AMREC)"; font-size: 8pt; color: #999; font-family: 'Archivo', sans-serif; }}
      @bottom-right {{ content: "Fofoca Política: Transparência Radical"; font-size: 8pt; color: #999; font-family: 'Archivo', sans-serif; }}
    }}'''

    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS}\n{footer_css}</style></head>
<body><div class="doc">{body}</div></body></html>""", len(cards)


def html_to_pdf(html_str, out_pdf):
    # o .html temporário precisa ficar em HERE (não em _build/) porque o CSS/HTML
    # referencia assets com caminho relativo "./assets/..." — em _build/ isso
    # resolveria para uma pasta assets/ que não existe ali.
    html_path = os.path.join(HERE, "_tmp_" + os.path.basename(out_pdf).replace(".pdf", ".html"))
    open(html_path, "w").write(html_str)
    abs_html = os.path.abspath(html_path)
    # (sem --user-data-dir: um profile novo dispara o "first run"/Google Updater
    # do Chrome e o processo nunca fecha limpo, mesmo com o PDF já escrito —
    # isso já travou o build inteiro. Como as chamadas são sequenciais, não há
    # necessidade real de isolar profile entre elas.)
    for attempt in (1, 2):
        try:
            subprocess.run([
                CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                "--print-to-pdf-no-header", "--allow-file-access-from-files",
                f"--print-to-pdf={out_pdf}", f"file://{abs_html}",
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=45)
            break
        except subprocess.TimeoutExpired:
            print(f"  [AVISO] Chrome travou gerando {out_pdf} (tentativa {attempt}), matando e tentando de novo", file=sys.stderr)
            subprocess.run(["pkill", "-9", "-f", abs_html], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(html_path)


def display_name(city):
    return slugify(city).replace("_", "-").title()


def main():
    final_dir = "/Users/jairofortunato/mp/resumos/dossies-cidades/AMREC"
    os.makedirs(final_dir, exist_ok=True)

    total_cases = 0
    for i, city in enumerate(ORDEM, start=1):
        cta_full = build_cta_html(city)
        cta_pdf = os.path.join(OUT_DIR, f"{i:02d}_cta_{slugify(city)}.pdf")
        html_to_pdf(cta_full, cta_pdf)

        cover_html = build_cover_html(city)
        cover_full = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{cover_html}</body></html>"""
        cover_pdf = os.path.join(OUT_DIR, f"{i:02d}_cover_{slugify(city)}.pdf")
        html_to_pdf(cover_full, cover_pdf)

        html_str, n = build_city_html(city)
        city_pdf = os.path.join(OUT_DIR, f"{i:02d}_{slugify(city)}.pdf")
        html_to_pdf(html_str, city_pdf)

        writer = PdfWriter()
        writer.append(cover_pdf)
        writer.append(city_pdf)
        writer.append(cta_pdf)
        out_path = os.path.join(final_dir, f"Fofoca-Politica-Transparencia-Radical-{display_name(city)}.pdf")
        writer.write(out_path)
        writer.close()

        total_cases += n
        print(f"{city}: {n} casos -> {out_path}")

    print(f"\n{len(ORDEM)} PDFs gerados em {final_dir} · {total_cases} casos no total")


if __name__ == "__main__":
    main()
