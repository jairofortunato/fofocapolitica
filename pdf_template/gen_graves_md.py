#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagrama os dossiês de texto de `fofoca-casos/` no visual do dossiê da cidade.

Os `<cidade>-casos-graves.md` eram convertidos pelo `md_to_pdf.sh`, que é um CSS
genérico de markdown: saía um relatório azul sem capa, sem bandeira e sem
relação visual nenhuma com os `<REGIAO>_<Cidade>.pdf` publicados. Aqui o mesmo
markdown entra na identidade do produto — a capa e a contracapa são as mesmas do
`gen_dossie.py` (`templates/cover.html` e `templates/cta.html`), o cabeçalho é o
mesmo `.cityhead` com bandeira, brasão e finanças, e o miolo usa a cor da cidade
como fio condutor.

O miolo NÃO vira card: aqui cada caso é meia página de texto apurado, com
citação da decisão e alerta de armadilha do extrator. O card do `dossie.css`
existe para resumo de quatro linhas. O que se reaproveita é o vocabulário —
trilho à esquerda com a posição do caso, "Onde está" em cinza no fim do bloco.

Uso:
    python3 gen_graves_md.py ../fofoca-casos/pinhalzinho-casos-graves.md \
        --regiao amosc --cidade Pinhalzinho
"""
from __future__ import annotations

import argparse
import html
import os
import re
import subprocess
import sys

from pypdf import PdfWriter

import gen_dossie as gd
import regiao_config as rc

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(HERE, "templates")
LONGFORM_CSS = open(os.path.join(TEMPLATES, "longform.css")).read()


# --- markdown -> html ----------------------------------------------------

def pandoc(md_path):
    """--wrap=none de propósito: o pós-processamento abaixo casa padrões como
    '<p><strong>Onde está.</strong>' no início do parágrafo, e a quebra de linha
    automática do pandoc parte esses padrões no meio."""
    return subprocess.run(
        ["pandoc", "--from=gfm", "--to=html5", "--wrap=none", md_path],
        capture_output=True, text=True, check=True).stdout


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s).strip()


def marca_paragrafos(body):
    """Dá classe aos parágrafos que têm papel fixo no formato dos dossiês."""
    # "Onde está." é a linha de proveniência: número do processo e data da edição.
    body = re.sub(r'<p><strong>Onde est[áa]\.', '<p class="lf-src"><strong>Onde está.', body)
    # "Atenção — ..." é sempre ressalva editorial (extrator contaminado, desfecho
    # a favor do investigado, nome que não pode ser publicado).
    body = re.sub(r'<p><strong>(Aten[çc][ãa]o)', r'<p class="lf-alert"><strong>\1', body)
    # parágrafo só de negrito = linha de apoio do caso ("O caso mais forte da
    # cidade"). Vira a chamada, na cor da cidade.
    body = re.sub(r'<p><strong>([^<]*)</strong></p>', r'<p class="lf-lead">\1</p>', body)
    body = body.replace("<blockquote>", '<blockquote class="lf-quote">')
    return body


def build_body(md_path):
    doc = pandoc(md_path)
    doc = re.sub(r"<hr\s*/?>\s*", "", doc)          # os --- eram só separadores

    m = re.search(r"<h1[^>]*>(.*?)</h1>", doc, re.S)
    titulo = strip_tags(m.group(1)) if m else ""
    doc = re.sub(r"<h1[^>]*>.*?</h1>\s*", "", doc, count=1, flags=re.S)

    partes = re.split(r"(?=<h2\b)", doc)
    intro, secoes = partes[0], partes[1:]

    # abertura: o parágrafo de fontes/universo e o aviso de "acusação não é
    # condenação", que precisa aparecer antes de qualquer caso.
    # o primeiro parágrafo é sempre a ficha do levantamento (fonte, período,
    # universo, recorte) numa frase só. Vira bloco à parte, e cada rótulo em
    # negrito ganha uma linha — em corpo 8pt, tudo corrido fica ilegível.
    # "Fonte:"/"Fontes:" varia de dossiê para dossiê, então o gatilho é a
    # posição, não a palavra.
    def _meta(m):
        inner = re.sub(r'\s+<strong>([^<]{2,40}:)</strong>',
                       r'<br><strong>\1</strong>', m.group(1))
        return f'<div class="lf-meta"><p>{inner}</p></div>'

    intro = re.sub(r'<p>(.*?)</p>', _meta, intro, count=1, flags=re.S)
    intro = intro.replace("<blockquote>", '<div class="lf-warn">').replace("</blockquote>", "</div>")

    out, n_casos = [intro], 0
    for sec in secoes:
        m = re.match(r"<h2[^>]*>(.*?)</h2>(.*)", sec, re.S)
        if not m:
            out.append(sec)
            continue
        titulo_sec, corpo = m.group(1).strip(), marca_paragrafos(m.group(2))
        num = re.match(r"(\d+)\.\s*(.*)", strip_tags(titulo_sec), re.S)
        if num:
            n_casos += 1
            out.append(
                f'<section class="lf-case">'
                f'<div class="rail"><div class="n">{num.group(1)}</div>'
                f'<div class="lbl">caso</div></div>'
                f'<div class="body"><h2>{html.escape(num.group(2))}</h2>{corpo}</div>'
                f'</section>')
        else:
            out.append(f'<section class="lf-sec"><h2>{titulo_sec}</h2>{corpo}</section>')
    return titulo, "".join(out), n_casos


# --- página ---------------------------------------------------------------

def kicker_html(titulo, city):
    """'Pinhalzinho — os casos mais graves no MP e no TCE' vira só a segunda
    metade: o nome da cidade já está em corpo 24pt logo acima."""
    resto = titulo.split("—", 1)[1].strip() if "—" in titulo else titulo
    resto = resto[:1].upper() + resto[1:]
    m = re.match(r"(Os casos mais graves)(.*)", resto, re.I)
    if m:
        return f'<div class="lf-kicker"><span>{html.escape(m.group(1))}</span>{html.escape(m.group(2))}</div>'
    return f'<div class="lf-kicker">{html.escape(resto)}</div>'


def ensure_cor(reg, city):
    """Cidade fora do `cores.json` da região (as regiões montadas cidade a cidade
    só têm a cor das que já foram publicadas) recebe a cor derivada da bandeira,
    pelo mesmo critério do `gen_cores.py`, e a cor fica gravada."""
    if reg.cores.get(city):
        return reg.cores[city]
    flag = reg.imgs(city).get("bandeira")
    if not flag:
        return "#C4161C"
    import json
    import gen_cores
    cor = gen_cores.dominant(os.path.join(reg.dir, flag.lstrip("./")))
    path = os.path.join(reg.dir, "cores.json")
    cores = json.load(open(path)) if os.path.exists(path) else {}
    cores[city] = cor
    json.dump(cores, open(path, "w"), ensure_ascii=False, indent=1)
    reg.cores[city] = cor
    print(f"  cor de {city} derivada da bandeira: {cor}")
    return cor


def build_page_html(reg, city, titulo, body, n_casos, fonte_label):
    color = ensure_cor(reg, city)
    fin = reg.financas.get(city, {})
    imgs = reg.imgs(city)

    flag = f'<img class="c-flag" src="{imgs["bandeira"]}">' if imgs.get("bandeira") else ""
    bras = f'<img class="c-bras" src="{imgs["brasao"]}">' if imgs.get("brasao") else ""
    info = f'''<div class="cinfo">
        <div class="ci"><span class="cl">População</span><b>{gd.fmt_pop(fin.get("pop", 0))}</b><span class="cu">Censo 2022</span></div>
        <div class="ci"><span class="cl">Arrecadou 2025</span><b>{gd.fmt_brl(fin.get("rec", 0))}</b><span class="cu">receita realizada</span></div>
        <div class="ci"><span class="cl">Gastou 2025</span><b>{gd.fmt_brl(fin.get("desp", 0))}</b><span class="cu">despesa empenhada</span></div>
      </div>''' if fin else ""
    simbolos = (f'<div class="csymbols">{flag}{bras}{info}</div>'
                if (flag or bras or info) else "")

    head = f'''<section class="cityblock" style="--city:{color}">
      <div class="cityhead">
        <div class="h-t"><div class="small">{html.escape(reg.label)}</div>
          <div class="big">{html.escape(city)}</div></div>
        <img class="h-logo" src="./assets/logo-preto.png">
      </div>
      {simbolos}
      {kicker_html(titulo, city)}
      <div class="ccount">{n_casos} casos apurados um a um · revisão editorial · {fonte_label}</div>
      <div class="lf">{body}</div>
    </section>'''

    footer = f'''@page {{ size: A4; margin: 15mm 14mm 17mm 14mm;
      @bottom-left {{ content: "{city} · {reg.sigla.upper()}"; font-size: 8pt; color: #999; font-family: 'Archivo', sans-serif; }}
      @bottom-center {{ content: "Coleta e resumo por IA — confira na fonte citada"; font-size: 7.5pt; color: #b0b0b0; font-family: 'Archivo', sans-serif; }}
      @bottom-right {{ content: "Fofoca Política: Transparência Radical"; font-size: 8pt; color: #999; font-family: 'Archivo', sans-serif; }}
    }}
    /* o bloco de casos não é uma cidade nova no meio do documento: sem isso a
       regra `.cityblock{{page-break-before:always}}` do dossiê joga o cabeçalho
       para a página 2 e a primeira folha sai em branco. */
    .cityblock {{ page-break-before: auto; }}'''
    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
            f'<style>{gd.CSS}\n{LONGFORM_CSS}\n{footer}</style></head>'
            f'<body>{head}</body></html>')


def fonte_label(md_text):
    """Só a ficha de abertura conta: Florianópolis cita o TCE no corpo de um caso
    sem que o levantamento tenha varrido o DOTC-e."""
    ficha = md_text.split("\n## ", 1)[0]
    return "MPSC + TCE/SC" if "TCE" in ficha else "MPSC"


def build_compact_page(reg, city, md_path):
    """Use the same compact timeline cards as the approved Tubarão dossier.

    Grave dossiers used to render every decision paragraph in full, which made
    them look like technical process files. The card keeps the faithful title,
    a short source-backed summary and the official reference; the full extract
    remains in the accompanying Markdown source file.
    """
    text = open(md_path).read()
    titulo = text.split("\n", 1)[0].lstrip("# ").strip()
    cards = []
    for i, m in enumerate(re.finditer(r"^##\s+\d+\.\s+([^\n]+)\n+(.*?)(?=^##\s+\d+\.|\Z)", text, re.S | re.M)):
        title, body = m.group(1).strip(), m.group(2).strip()
        md = re.search(r"\*\*Edição:\*\*\s*\[?(\d{4})-(\d{2})-(\d{2})", body)
        if not md:
            continue
        ymd = tuple(map(int, md.groups()))
        ms = re.search(r"\*\*Status:\*\*\s*([^\n]+)", body)
        raw_status = ms.group(1).split(" · ", 1)[0].strip(" ·*") if ms else "🔴 apontou irregularidade"
        status = raw_status
        # The official metadata uses a compact icon label; keep the label in
        # the pill and let the existing palette choose its colour.
        org = re.search(r"\*\*Órgão:\*\*\s*(MPSC|TCE(?:-SC)?)", body)
        src = ("MP" if org.group(1) == "MPSC" else "TCE") if org else ("TCE" if "DOTC" in body else "MP")
        refm = re.search(r"\*\*Onde está\.\*\*.*?processo\s+([^·\n]+)", body, re.I)
        ref = refm.group(1).strip() if refm else ""
        explicit = re.search(r"\*\*Resumo:\*\*\s*(.+?)(?=\n\s*\n|\n\*\*|\Z)", body, re.S)
        sm = re.search(r"\*\*(?:Medida cautelar|A decisão|O acórdão|A decisão do TCE).*?\*\*", body, re.S)
        if explicit:
            summary = re.sub(r"\s+", " ", explicit.group(1)).strip()
        elif sm:
            summary = sm.group(0).strip("*").strip()
        else:
            dm = re.search(r"\*\*Decisão:\*\*\s*(.+?)(?:\n\n|\n\*\*|\Z)", body, re.S)
            summary = re.sub(r"\s+", " ", dm.group(1)).strip() if dm else "Extrato oficial selecionado no recorte de casos graves."
            sentences = re.split(r"(?<=[.!?])\s+", summary)
            summary = " ".join(sentences[:2])
        summary = summary[:900].rstrip() + ("…" if len(summary) > 900 else "")
        fonte_nome = ("Diário Oficial Eletrônico do MPSC (DO-MPSC)" if src == "MP"
                      else "Diário Oficial Eletrônico de Contas (DOTC-e/TCE-SC)")
        source_link = gd.mp_source_link(ymd) if src == "MP" else gd.tce_source_link(ymd)
        fonte = (f"Fonte: {fonte_nome} · Processo nº {gd.esc(ref)} · edição "
                 f"{ymd[2]:02d}/{ymd[1]:02d}/{ymd[0]} · "
                 f'<a href="{source_link}">conferir a edição original</a>')
        extra = re.search(r"\*\*Fonte adicional:\*\*\s*([^\n]+)", body)
        if extra:
            fonte += f" · {gd.esc(extra.group(1).strip())}"
        severity = re.search(r"\*\*Gravidade:\*\*\s*(alta|media)", body)
        cards.append({"ymd": ymd, "dm": f"{ymd[2]:02d} {gd.MESES_PT[ymd[1]]}",
                      "status": status, "cls": gd.pill_cls(status), "title": gd.esc(title),
                      "line": gd.esc(summary), "fonte_html": fonte, "src": src,
                      "ref": ref, "severity": severity.group(1) if severity else "alta"})
    if not cards:
        raise ValueError(f"Nenhum caso reconhecido em {md_path}")
    cards.sort(key=lambda c: c["ymd"], reverse=True)
    inner, _, _ = gd.build_city_html(reg, city, cards=cards)
    style = '''.cityblock{page-break-before:auto}.case .ln{font-size:9.5pt;line-height:1.35}.case .ref{font-size:7.5pt;line-height:1.3}.case{break-inside:avoid;margin-bottom:2.5mm}.cityhead .h-t .small{display:block;line-height:1.15;margin-bottom:1mm}.cityhead .h-t .big{line-height:1.02}.case.sev-alta .sev-tag{color:#b4131c}.case.sev-alta .rail::after{background:#b4131c;border-color:#b4131c}'''
    if len(cards) == 1:
        inner = inner.replace("1 casos selecionados", "1 caso selecionado")
        inner = inner.replace("1 marcados como grave", "1 marcado como grave")
    return inner.replace("</style>", style + "</style>")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md", help="markdown de fofoca-casos/")
    ap.add_argument("--regiao", required=True)
    ap.add_argument("--cidade", required=True)
    ap.add_argument("--out", help="PDF final (padrão: ao lado do markdown)")
    ap.add_argument("--campanha", action="store_true",
                    help="inclui a faixa de propaganda eleitoral na contracapa")
    args = ap.parse_args()

    reg = rc.get(args.regiao)
    city = args.cidade
    if city not in reg.ordem:
        print(f"[AVISO] {city} não está na ordem de {reg.sigla}: "
              f"cor, bandeira e finanças podem faltar", file=sys.stderr)

    md_path = os.path.abspath(args.md)
    titulo, body, n_casos = build_body(md_path)
    page = build_compact_page(reg, city, md_path)
    if n_casos != len(re.findall(r'<div class="case(?: sev-alta)?">', page)):
        raise ValueError(f"{city}: divergência entre casos do Markdown e cards renderizados")

    build_dir = os.path.join(reg.dir, "_build")
    os.makedirs(build_dir, exist_ok=True)
    slug = rc.slugify(city)
    partes = []
    for nome, htm in (("cover", gd.build_cover_html(reg, city)),
                      ("miolo", page),
                      ("cta", gd.build_cta_html(reg, city, campanha=args.campanha))):
        p = os.path.join(build_dir, f"graves_{nome}_{slug}.pdf")
        gd.html_to_pdf(reg, htm, p)
        partes.append(p)

    out = args.out or md_path.replace(".md", ".pdf")
    writer = PdfWriter()
    for p in partes:
        writer.append(p)
    writer.write(out)
    writer.close()
    from pypdf import PdfReader
    print(f"{city}: {n_casos} casos · {len(PdfReader(out).pages)} pág. -> {out}")


if __name__ == "__main__":
    main()
