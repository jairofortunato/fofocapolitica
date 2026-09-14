#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os dossiês "Fofoca Política: Transparência Radical" de uma região.

Um PDF por cidade: capa personalizada + os casos daquela cidade + contracapa.

Generaliza o `amrec/gen_amrec_curated.py`, que era específico da AMREC em dois
pontos que não escalavam:
  1. região/sigla/contagem de cidades escritos direto no HTML e no código —
     agora vêm de `regiao_config.py`;
  2. `load_curated_for_city()` era um if/elif por lote de curadoria (small1_0,
     icara_mp_1, ...), fruto de como os agentes foram disparados naquela sessão.
     Aqui a convenção é fixa: um arquivo curado por cidade,
     `<regiao>/_curated_data/curated/<slug>.json`, alinhado posicionalmente com
     o raw correspondente.

Uso:
    python3 gen_dossie.py amesc
    python3 gen_dossie.py amesc --cidade Araranguá   # só uma, para revisar
"""
from __future__ import annotations

import argparse
import html
import json
import os
import subprocess
import sys
import tempfile
import time

from pypdf import PdfReader, PdfWriter

import regiao_config as rc

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(HERE, "templates")
REPO = os.path.join(HERE, "..")
CSS = open(os.path.join(TEMPLATES, "dossie.css")).read()

MESES_PT = {1: "JAN", 2: "FEV", 3: "MAR", 4: "ABR", 5: "MAI", 6: "JUN",
            7: "JUL", 8: "AGO", 9: "SET", 10: "OUT", 11: "NOV", 12: "DEZ"}

CHROME = ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def esc(s):
    return html.escape(str(s))


def fmt_pop(v):
    return f"{v:,}".replace(",", ".") if v else "—"


def fmt_brl(v):
    if not v:
        return "—"
    if v >= 1_000_000_000:
        return f"R$ {v/1_000_000_000:.2f} bi".replace(".", ",")
    return f"R$ {v/1_000_000:.0f} mi"


def mp_source_link(ymd):
    y, m, d = ymd
    return f"https://www.mpsc.mp.br/documents/d/guest/do_mpsc_{y}-{m:02d}-{d:02d}"


def tce_source_link(ymd):
    y, m, d = ymd
    return f"https://consulta.tce.sc.gov.br/Diario/dotc-e{y}-{m:02d}-{d:02d}.pdf"


# classificação da "pílula" de status: reusa a da AMREC em vez de reescrever,
# senão as cores dos status divergem entre regiões.
sys.path.insert(0, os.path.join(HERE, "amrec"))
from gen_amrec_full import pill_cls  # noqa: E402


# --- dados ---------------------------------------------------------------

def load_raw(reg, city):
    path = os.path.join(reg.dir, "_curated_data", "raw", f"{rc.slugify(city)}.json")
    return json.load(open(path))


def load_curated(reg, city):
    """Um arquivo por cidade, alinhado posicionalmente com o raw.

    Cada entrada: {keep, title, description, severity}. `tipo` separa mp/tce
    quando o arquivo traz os dois (é o formato que os agentes de curadoria
    devolvem).
    """
    path = os.path.join(reg.dir, "_curated_data", "curated", f"{rc.slugify(city)}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"falta a curadoria de {city}: {path}\n"
            f"rode a revisão editorial antes de gerar o PDF desta cidade."
        )
    data = json.load(open(path))
    if isinstance(data, dict):
        return data.get("mp", []), data.get("tce", [])
    mp = [r for r in data if r.get("tipo") == "mp"]
    tce = [r for r in data if r.get("tipo") == "tce"]
    return mp, tce


# Selos em que algo de fato aconteceu: houve responsabilização, acordo, punição,
# medida judicial ou providência cumprida. Ficam de fora "arquivado", "julgado
# regular" e os "❔" — em Joinville isso é 85% dos casos, e é o que faz o dossiê
# passar de 1.890 cards. Um caso arquivado não deixa de ser público; ele só não
# cabe na versão curta, que existe para ser lida.
SELOS_COM_DESFECHO = (
    "⬛ julgado irregular", "⬛ julgado irregular + multa", "🔴 multa aplicada",
    "🔴 apontou irregularidade", "🔴 parecer pela rejeição", "🔴 ACP ajuizada",
    "🔴 ADI ajuizada", "🟠 TAC firmado", "🟠 ACNP firmado", "🟠 cautelar / sustação",
    "🟡 em instrução (citação/audiência)", "🟡 em apuração",
    "🟢 recomendação cumprida", "⚫ prescrito",
)


def tem_desfecho(card):
    """Card entra na versão curta? Grave sempre entra, mesmo com selo brando."""
    return card["severity"] == "alta" or card["status"] in SELOS_COM_DESFECHO


# Peso do selo na ordenação por gravidade. A escala segue o quanto o caso já
# produziu consequência concreta: condenação e multa no topo, ação judicial e
# irregularidade apontada logo abaixo, acordos no meio (houve correção, mas sem
# condenação), apuração em aberto mais abaixo, e arquivado/regular no fim — não
# porque deixem de ser públicos, mas porque não é o que a pessoa procura quando
# abre um dossiê de 3 páginas.
PESO_SELO = {
    "⬛ julgado irregular + multa": 100,
    "⬛ julgado irregular": 92,
    "🔴 multa aplicada": 88,
    "🔴 ACP ajuizada": 84,
    "🔴 ADI ajuizada": 84,
    "🔴 apontou irregularidade": 76,
    "🔴 parecer pela rejeição": 74,
    "🟠 cautelar / sustação": 70,
    "🟠 ACNP firmado": 64,
    "🟠 TAC firmado": 60,
    "🟡 em instrução (citação/audiência)": 48,
    "🟡 em apuração": 40,
    "⚫ prescrito": 30,
    "🟢 recomendação cumprida": 22,
    "❔ em tramitação": 18,
    "❔ status indef.": 16,
    "🟢 julgado regular": 8,
    "🟢 arquivado": 5,
}

# "grave" pesa mais que qualquer degrau isolado da escala de selos: um caso
# marcado como grave na revisão editorial e depois arquivado ainda interessa
# mais que um TAC de rotina.
BONUS_GRAVE = 60


def relevancia(card):
    """Score de gravidade. A data entra só como desempate, para que entre dois
    casos igualmente graves o mais recente apareça primeiro."""
    peso = PESO_SELO.get(card["status"], 16)
    grave = BONUS_GRAVE if card["severity"] == "alta" else 0
    ano = card["ymd"][0] or 0
    recencia = max(0, ano - 2020)  # 2022 -> 2, 2026 -> 6
    return peso + grave + recencia


def dedup_processo(cards):
    """Um caso por número de processo.

    O levantamento é por edição de diário, então um mesmo processo reaparece a
    cada movimentação: em Criciúma, o processo da Festa das Etnias sozinho
    ocupava 5 das 17 vagas do dossiê curto, com cinco cards contando etapas do
    mesmo julgamento. No dossiê completo isso é histórico e faz sentido; num
    recorte de "os mais graves" é desperdício de espaço.

    Recebe a lista já ordenada por relevância e guarda a primeira ocorrência de
    cada processo — que é a de maior score e, no empate, a mais recente. Casos
    sem número de processo passam sempre, porque não há como saber se repetem.
    """
    vistos, unicos = set(), []
    for c in cards:
        ref = (c.get("ref") or "").strip()
        if ref and ref in vistos:
            continue
        if ref:
            vistos.add(ref)
        unicos.append(c)
    return unicos


def build_cards(reg, city):
    raw = load_raw(reg, city)
    mp_cur, tce_cur = load_curated(reg, city)

    for label, a, b in (("MP", raw["mp"], mp_cur), ("TCE", raw["tce"], tce_cur)):
        if len(a) != len(b):
            print(f"  [AVISO] {city}: raw {label}={len(a)} != curated {label}={len(b)}",
                  file=sys.stderr)

    cards = []
    for src, raws, curs, fonte_nome, linker in (
        ("MP", raw["mp"], mp_cur, "Diário Oficial Eletrônico do MPSC (DO-MPSC)", mp_source_link),
        ("TCE", raw["tce"], tce_cur, "Diário Oficial Eletrônico de Contas (DOTC-e/TCE-SC)", tce_source_link),
    ):
        for r, c in zip(raws, curs):
            if not c.get("keep"):
                continue
            y, m, d = r["ymd"]
            fonte = (f'Fonte: {fonte_nome}, edição de {d:02d}/{m:02d}/{y}'
                     f' · Processo nº {esc(r["ref"])}')
            if y:
                fonte += f' · <a href="{linker(r["ymd"])}">conferir a edição original</a>'
            # o status do bruto vem de um classificador por palavra-chave e
            # contradiz o texto em parte dos casos (selo "ACP ajuizada" sobre
            # manchete de arquivamento). Quando a revisão editorial informou o
            # status, ele manda — foi lido junto com o texto da decisão.
            status = c.get("status") or r["status"]
            cards.append({
                "ymd": r["ymd"],
                "dm": f"{d:02d} {MESES_PT.get(m, '')}" if m else "",
                "status": status, "cls": pill_cls(status),
                "title": esc(c["title"]), "line": esc(c["description"]),
                "fonte_html": fonte, "src": src, "ref": r["ref"],
                "severity": c.get("severity", "media"),
            })
    cards.sort(key=lambda c: c["ymd"], reverse=True)
    return cards


# --- HTML ----------------------------------------------------------------

def card_html(c, color, rank=None):
    y = c["ymd"][0]
    src_badge = f'<span class="src {c["src"].lower()}">{c["src"]}</span>'
    sev_cls = " sev-alta" if c["severity"] == "alta" else ""
    sev_tag = '<span class="sev-tag">⬤ CASO GRAVE</span>' if c["severity"] == "alta" else ""
    # no modo ranqueado a posição vai no trilho junto da data: sem isso a lista
    # fora de ordem cronológica parece erro de geração, não escolha editorial.
    rk = f'<div class="rk">#{rank}</div>' if rank else ""
    return f'''<div class="case{sev_cls}">
      <div class="rail" style="--rc:{color}">{rk}<div class="yr">{y or ''}</div><div class="dm">{c["dm"]}</div></div>
      <div class="body">
        <div class="pl"><span class="pill {c['cls']}">{esc(c['status'])}</span>{src_badge}{sev_tag}</div>
        <h3>{c['title']}</h3>
        <div class="ln">{c['line']}</div>
        <div class="ref">{c['fonte_html']}</div>
      </div></div>'''


def build_cover_html(reg, city):
    tpl = open(os.path.join(TEMPLATES, "cover.html")).read()
    imgs = reg.imgs(city)
    simbolos = "".join(f'<img class="cf-{cls}" src="{src}" alt="{esc(city)}">'
                       for cls, src in (("flag", imgs.get("bandeira")),
                                        ("bras", imgs.get("brasao"))) if src)
    out = (tpl.replace("{{CIDADE}}", esc(city))
              .replace("{{NA_REGIAO}}", f"na região do {reg.nome}" if reg.nome.startswith("Extremo")
                       else f"na {reg.nome}")
              .replace("{{SIMBOLOS}}", simbolos)
              .replace("{{REGIAO_LABEL}}", esc(reg.label))
              .replace("{{TEXTO_CAPA}}", esc(reg.texto_capa(city))))
    return wrap(out)


# Bloco de propaganda eleitoral. Fica deliberadamente separado do corpo do
# dossiê e rotulado como tal: o resto do documento é apuração de fontes oficiais
# e não pode parecer que os casos foram levantados como peça de campanha.
CAMPANHA_HTML = '''<div class="campanha">
      <div class="c-num">14999</div>
      <div class="c-txt"><b>Jairo</b><span>Deputado Estadual</span></div>
      <div class="c-tag">Propaganda eleitoral</div>
    </div>'''


def build_cta_html(reg, city, campanha=False):
    tpl = open(os.path.join(TEMPLATES, "cta.html")).read()
    return wrap(tpl.replace("{{CIDADE}}", esc(city))
                   .replace("{{CAMPANHA}}", CAMPANHA_HTML if campanha else ""))


def build_city_html(reg, city, so_desfecho=False, ranked=False, limite=None,
                    cards=None, so_graves=False):
    cards = list(cards) if cards is not None else build_cards(reg, city)
    if so_desfecho:
        cards = [c for c in cards if tem_desfecho(c)]
    n_total = len(cards)
    if ranked:
        # dedup antes de filtrar por gravidade, e não depois: o denominador que
        # o cabeçalho mostra tem de ser o universo levantado para a cidade, não
        # o subconjunto que sobrou do filtro — senão sai "os 9 casos mais graves
        # de 9 levantados", que não informa nada.
        cards.sort(key=lambda c: (relevancia(c), c["ymd"]), reverse=True)
        cards = dedup_processo(cards)
        n_total = len(cards)
    if so_graves:
        cards = [c for c in cards if c["severity"] == "alta"]
    if limite:
        cards = cards[:limite]
    n_mp = sum(1 for c in cards if c["src"] == "MP")
    n_alta = sum(1 for c in cards if c["severity"] == "alta")
    color = reg.cores.get(city, "#C4161C")
    fin = reg.financas.get(city, {})
    imgs = reg.imgs(city)

    flag = f'<img class="c-flag" src="{imgs["bandeira"]}">' if imgs.get("bandeira") else ""
    bras = f'<img class="c-bras" src="{imgs["brasao"]}">' if imgs.get("brasao") else ""
    info = f'''<div class="cinfo">
        <div class="ci"><span class="cl">População</span><b>{fmt_pop(fin.get("pop", 0))}</b><span class="cu">Censo 2022</span></div>
        <div class="ci"><span class="cl">Arrecadou 2025</span><b>{fmt_brl(fin.get("rec", 0))}</b><span class="cu">receita realizada</span></div>
        <div class="ci"><span class="cl">Gastou 2025</span><b>{fmt_brl(fin.get("desp", 0))}</b><span class="cu">despesa empenhada</span></div>
      </div>''' if fin else ""

    if ranked:
        # a linha de contagem vira o aviso de ordenação. É o único lugar em que
        # o leitor descobre que a lista não é cronológica antes de estranhar as
        # datas fora de ordem, então ela diz as duas coisas: o recorte (N de M)
        # e o critério.
        titulo = (f'<b>Os {len(cards)} casos graves</b>' if so_graves
                  else f'<b>Os {len(cards)} casos mais graves</b>')
        conta_html = (
            f'<div class="ccount ranked">'
            f'{titulo} de {n_total} levantados em fontes oficiais'
            f' · {n_mp} do Ministério Público · {len(cards)-n_mp} do Tribunal de Contas'
            f'<span class="ordaviso">Ordenado por gravidade, do mais grave para o menos grave —'
            f' <b>não é ordem cronológica</b>. A data de cada caso está à esquerda.</span>'
            f'</div>')
    else:
        conta_html = (
            f'<div class="ccount">{len(cards)} casos selecionados (revisão editorial)'
            f' · {n_mp} do Ministério Público · {len(cards)-n_mp} do Tribunal de Contas'
            f' · {n_alta} marcados como grave</div>')

    body = f'''<section class="cityblock" style="--city:{color}">
      <div class="cityhead">
        <div class="h-t"><div class="small">{esc(reg.label)}</div><div class="big">{esc(city)}</div></div>
        <img class="h-logo" src="./assets/logo-preto.png">
      </div>
      <div class="csymbols">{flag}{bras}{info}</div>
      {conta_html}
      {"".join(card_html(c, color, rank=(i if ranked else None))
               for i, c in enumerate(cards, start=1))}
    </section>'''

    # o aviso de IA vai no rodapé de toda página, não só na contracapa: as
    # pessoas imprimem ou printam folhas soltas, e cada folha precisa carregar a
    # ressalva junto com os casos.
    footer = f'''@page {{ size: A4; margin: 16mm 14mm 18mm 14mm;
      @bottom-left {{ content: "{city} · {reg.nome} ({reg.sigla.upper()})"; font-size: 8pt; color: #999; font-family: 'Archivo', sans-serif; }}
      @bottom-center {{ content: "Coleta e resumo por IA — confira na fonte citada"; font-size: 7.5pt; color: #b0b0b0; font-family: 'Archivo', sans-serif; }}
      @bottom-right {{ content: "Fofoca Política: Transparência Radical"; font-size: 8pt; color: #999; font-family: 'Archivo', sans-serif; }}
    }}'''
    doc_cls = "doc ranked" if ranked else "doc"
    return wrap(f'<div class="{doc_cls}">{body}</div>', extra_css=footer), len(cards), n_total


def wrap(body, extra_css=""):
    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
            f'<style>{CSS}\n{extra_css}</style></head><body>{body}</body></html>')


# --- PDF -----------------------------------------------------------------

def html_to_pdf(reg, html_str, out_pdf, tries=2):
    """O HTML temporário precisa ficar no diretório da região: o CSS referencia
    assets por caminho relativo ('./assets/...').

    Sem --user-data-dir de propósito: um profile novo dispara o first-run do
    Chrome e o processo trava com o PDF já escrito.
    """
    # apaga o alvo antes: a checagem de sucesso abaixo é "o arquivo existe e não
    # está truncado", e um PDF da geração anterior passa nela. Foi assim que
    # Içara saiu com capa nova e 35 páginas de conteúdo de um mês antes.
    if os.path.exists(out_pdf):
        os.unlink(out_pdf)
    fd, tmp = tempfile.mkstemp(suffix=".html", dir=reg.dir)
    os.write(fd, html_str.encode())
    os.close(fd)
    try:
        for attempt in range(tries):
            try:
                subprocess.run(
                    [CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                     f"--print-to-pdf={out_pdf}", f"file://{tmp}"],
                    timeout=120, capture_output=True,
                )
            except subprocess.TimeoutExpired:
                pass
            if os.path.exists(out_pdf) and os.path.getsize(out_pdf) > 1000:
                return
            time.sleep(1)
        raise RuntimeError(f"Chrome não gerou {out_pdf}")
    finally:
        os.unlink(tmp)


def display_name(city):
    return rc.slugify(city).replace("_", "-").title()


def fit_paginas(reg, city, base, args, out_pdf):
    """Acha o maior nº de casos que cabe no teto de páginas e deixa esse PDF
    escrito em `out_pdf`.

    Busca binária em cima do render real do Chrome, e não por estimativa de
    altura: a altura de um card varia muito (título de uma ou três linhas,
    tarja de caso grave, resumo curto ou longo), então contar página estimada
    erra para os dois lados. São ~10 renders por cidade — caro, mas é o que
    garante que o PDF publicado tem exatamente o número de páginas prometido.
    """
    orcamento = args.paginas_casos  # só as páginas de casos; capa e contracapa à parte

    def render(k):
        if os.path.exists(out_pdf):
            os.unlink(out_pdf)  # senão um render falho revalida o PDF anterior
        html, n, n_total = build_city_html(
            reg, city, so_desfecho=args.so_desfecho, ranked=True,
            limite=k, cards=base, so_graves=args.so_graves)
        html_to_pdf(reg, html, out_pdf)
        return len(PdfReader(out_pdf).pages), n, n_total

    pags, n, n_total = render(None)          # tudo: já cabe?
    if pags <= orcamento:
        print(f"  {city}: {n} casos em {pags} pág. (dentro do teto)")
        return n, n_total

    lo, hi, melhor = 1, n_total, 1
    while lo <= hi:
        meio = (lo + hi) // 2
        pags, n, _ = render(meio)
        if pags <= orcamento:
            melhor, lo = meio, meio + 1
        else:
            hi = meio - 1

    pags, n, _ = render(melhor)
    print(f"  {city}: {n} de {n_total} casos cabem em {pags} pág. de conteúdo "
          f"(teto {orcamento})")
    return n, n_total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("regiao")
    ap.add_argument("--cidade", action="append", help="gerar só esta(s) cidade(s)")
    ap.add_argument("--so-desfecho", action="store_true",
                    help="versão curta: só casos graves ou com desfecho (multa, "
                         "acordo, ação, cautelar). Sai com sufixo -RESUMO.")
    ap.add_argument("--campanha", action="store_true",
                    help="inclui a faixa de propaganda eleitoral (14999 Jairo "
                         "Deputado Estadual) na contracapa.")
    ap.add_argument("--so-graves", action="store_true",
                    help="só os casos marcados como grave na revisão editorial. "
                         "Implica --ranked. Sai com sufixo -GRAVES.")
    ap.add_argument("--ranked", action="store_true",
                    help="ordena por gravidade em vez de por data, numera os "
                         "casos e avisa no cabeçalho que não é ordem cronológica.")
    ap.add_argument("--paginas-casos", type=int, metavar="N",
                    help="teto de páginas DE CASOS, sem contar capa e "
                         "contracapa (o PDF final sai com N+2). Corta a cauda "
                         "da lista até caber. Implica --ranked, senão o corte "
                         "seria arbitrário.")
    ap.add_argument("--sufixo", default=None,
                    help="sufixo do nome do arquivo (padrão: -RESUMO com "
                         "--so-desfecho, -TOP com --paginas-casos).")
    args = ap.parse_args()
    if args.paginas_casos or args.so_graves:
        args.ranked = True
    if args.paginas_casos is not None and args.paginas_casos < 1:
        ap.error("--paginas-casos mínimo é 1")

    reg = rc.get(args.regiao)
    cidades = args.cidade or reg.ordem
    build_dir = os.path.join(reg.dir, "_build")
    final_dir = os.path.join(REPO, "resumos", "dossies-cidades", reg.sigla.upper())
    os.makedirs(build_dir, exist_ok=True)
    os.makedirs(final_dir, exist_ok=True)

    total = 0
    for i, city in enumerate(cidades, start=1):
        slug = rc.slugify(city)
        parts = []
        for name, builder in (("cover", lambda: build_cover_html(reg, city)),
                              ("cta", lambda: build_cta_html(reg, city, campanha=args.campanha))):
            p = os.path.join(build_dir, f"{i:02d}_{name}_{slug}.pdf")
            html_to_pdf(reg, builder(), p)
            parts.append((name, p))

        city_pdf = os.path.join(build_dir, f"{i:02d}_{slug}.pdf")
        base = build_cards(reg, city)
        if args.paginas_casos:
            n, n_total = fit_paginas(reg, city, base, args, city_pdf)
        else:
            city_html, n, n_total = build_city_html(
                reg, city, so_desfecho=args.so_desfecho, ranked=args.ranked,
                cards=base, so_graves=args.so_graves)
            html_to_pdf(reg, city_html, city_pdf)

        writer = PdfWriter()
        writer.append(dict(parts)["cover"])
        writer.append(city_pdf)
        writer.append(dict(parts)["cta"])
        sufixo = args.sufixo if args.sufixo is not None else (
            "-TOP" if args.paginas_casos else "-GRAVES" if args.so_graves
            else "-RESUMO" if args.so_desfecho else "")
        out = os.path.join(
            final_dir,
            f"Fofoca-Politica-Transparencia-Radical-{display_name(city)}{sufixo}.pdf")
        writer.write(out)
        writer.close()

        total += n
        print(f"{city}: {n} casos -> {out}")

    print(f"\n{len(cidades)} PDFs em {final_dir} · {total} casos")


if __name__ == "__main__":
    main()
