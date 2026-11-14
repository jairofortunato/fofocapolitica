#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dossiê AMREC com TODOS os casos (MP + TCE), lendo os arquivos de região.
Resumo por regras (v1) — para teste do pipeline em volume total.
Conteúdo flui por várias páginas (não fixa 1 página por cidade)."""
import html, re, os
from gen_amrec import CITY_COLOR, FINANCAS, IMGS, fmt_brl, fmt_pop, ORDEM, esc

ASSETS = "./assets"
MP_MD  = "/Users/jairofortunato/mp/resumos/regioes/regiao-amrec.md"
TCE_MD = "/Users/jairofortunato/mp/tcesc/resumos/regioes/regiao-amrec-tce.md"

MESES_PT = {1:"JAN",2:"FEV",3:"MAR",4:"ABR",5:"MAI",6:"JUN",7:"JUL",8:"AGO",9:"SET",10:"OUT",11:"NOV",12:"DEZ"}

# --- filtro de relevância (corta casos processuais/sem mérito) ---
# status com "dentes": já houve consequência real (ação, acordo, multa, prescrição
# reconhecendo o fato) — entram sempre, sem checar especificidade.
TEETH = ("🔴", "🟠", "⚫", "⬛")

NO_MERIT_RE = re.compile(
    r"ausência de (?:elementos|indícios|dolo|comprovação|justa causa|ilegalidade|fundamento|lesão|irregularidade)"
    r"|inexistência de (?:indícios|fundamento|ato|irregularidade)"
    r"|não\s+configura(?:do|da)?"
    r"|indeferimento"
    r"|falta de (?:elementos|justa causa|interesse de agir)"
    r"|sem indícios|sem irregularidade"
    r"|não restou comprovad"
    r"|improcedente"
    r"|regulariz|restabele|readequ|atipicidade material"
    r"|dentro da normalidade|conforme a legislação|não há irregularidade"
    r"|serviço (?:foi|restou) (?:adequado|prestado normalmente)"
    r"|fornecimento (?:foi|restou) adequado",
    re.IGNORECASE,
)

VALUE_RE = re.compile(r"R\$\s?[\d.,]+")
NAMED_PERSON_RE = re.compile(r"[A-ZÀ-Ý][a-zà-ÿ]+\s+[A-ZÀ-Ý][a-zà-ÿ]+")
INSTITUTIONAL_ONLY_RE = re.compile(
    r"^(munic[íi]pio de|prefeitura(?: municipal)? de|c[âa]mara (?:municipal|de vereadores) de)\s+[\wÀ-ÿ]+\.?$",
    re.IGNORECASE,
)

# sinais de que algo real aconteceu (consequência confirmada) — quando presentes,
# ignoram frases de "sem mérito" que às vezes aparecem só sobre uma parte do caso
# (ex.: "ausência de indícios em outros períodos" num caso onde o principal já foi
# comprovado e virou ação).
MERIT_RE = re.compile(
    r"ajuizamento|ação penal|ação civil pública|condenad|indiciad"
    r"|respons[aá]vel pelos desvios|ressarciment|multa aplicada|culpado"
    r"|recomendaç[ãa]o.{0,40}(?:acatad|cumprid|acolhid)"
    r"|exonera[çc][ãa]o|exonerad|afastamento do cargo|constataç[ãa]o positiva",
    re.IGNORECASE,
)

def has_specificity(*texts):
    blob = " ".join(t for t in texts if t)
    if VALUE_RE.search(blob):
        return True
    for t in texts:
        t = (t or "").strip()
        if t and not INSTITUTIONAL_ONLY_RE.match(t) and NAMED_PERSON_RE.search(t):
            return True
    return False

def keep_mp_case(status, star, *texts):
    if any(status.startswith(s) for s in TEETH):
        return True
    blob = " ".join(t for t in texts if t)
    if MERIT_RE.search(blob):
        return True
    if NO_MERIT_RE.search(blob):
        return False
    # caso ainda sem desfecho: só entra se for de alta relevância política
    # (⭐ score≥12) e tiver algo concreto (nome próprio ou valor em R$) — sem
    # isso é apuração de rotina, não "fofoca".
    return star == '⭐' and has_specificity(*texts)

TCE_ROUTINE_RE = re.compile(
    r"ato de aposentadoria|ato de concessão de pensão|registro d[eo] ato de (?:pensão|aposentadoria)"
    r"|^aposentadoria de|^pensão (?:de|e auxílio especial)",
    re.IGNORECASE,
)

def keep_tce_case(status, star, assunto=""):
    if status in ("🟢 julgado regular", "🟢 parecer pela aprovação"):
        return False
    strong = status.startswith("🔴") or status.startswith("🟠") or status.startswith("⬛ julgado irregular")
    # registro individual de aposentadoria/pensão é rotina administrativa —
    # só interessa se o TCE de fato apontou problema nele.
    if TCE_ROUTINE_RE.search(assunto or ""):
        return strong
    if strong:
        return True
    # sem irregularidade/multa/sustação confirmada: só entra se for de alta
    # relevância política (⭐ score≥12) — o resto é trâmite administrativo comum.
    return star == '⭐'

def sections(path):
    txt = open(path).read()
    out = {}
    for p in re.split(r'\n## (?!#)', txt)[1:]:
        out[p.split('\n',1)[0].strip()] = p
    return out

def blocks(sec):
    return re.split(r'\n#### ', sec)[1:] if sec else []

def field(b, name):
    m = re.search(r'\*\*'+name+r':\*\*\s*(.+)', b)
    return re.sub(r'\s+', ' ', m.group(1)).strip() if m else ""

def status_of(b):
    m = re.search(r'\*\*Status:\*\*\s*([^\n·]+)', b)
    return m.group(1).strip() if m else ""

def date_of(b):
    m = re.search(r'\*\*Edição:\*\*\s*\[?(\d{4})-(\d{2})-(\d{2})', b)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else (0,0,0)

def proc_of(header):
    m = re.search(r'N\.?\s*([0-9./-]+)', header) or re.search(r'\b([A-Z@]{2,4}\s?\d{2}/\d{5,})', header)
    return m.group(1).strip() if m else ""

# emoji do status -> classe de pill
def pill_cls(status):
    s = status
    if s.startswith('🔴'): return 'red'
    if s.startswith('⬛'): return 'tce'
    if s.startswith('🟠'): return 'amber'
    if s.startswith('🟢'): return 'green'
    if s.startswith('🟡'): return 'yel'
    return 'gray'

MP_OUT = {
    'em apuração':'Em investigação', 'arquivado':'Arquivado',
    'recomendação cumprida':'Recomendação cumprida', 'ACNP firmado':'Acordo de devolução (ANPC)',
    'TAC firmado':'Acordo de correção (TAC)', 'ACP ajuizada':'Virou ação na Justiça',
    'ACP em curso':'Ação na Justiça em curso', 'prescrito':'Prescrito', 'status indef.':'Em tramitação',
}

def clean(t, n=None):
    # normaliza espaços; não trunca — o dossiê deve trazer a informação completa,
    # sem reticências cortando o título ou os detalhes do caso.
    return re.sub(r'\s+', ' ', t or '').strip()

def cap(t):
    return t[:1].upper() + t[1:] if t else t

def mp_case(b):
    header = b.split('\n',1)[0].strip()
    star = header[0] if header else '·'
    status = status_of(b); ymd = date_of(b)
    if not keep_mp_case(status, star, field(b,'Partes'), field(b,'Objeto'), field(b,'Decisão/Conclusão')):
        return None
    partes_raw = field(b, 'Partes')
    parts = re.split(r'Conclus[ãa]o:', partes_raw, 1)
    if len(parts) > 1:
        partes = parts[0].strip(' .'); concl = parts[1].strip()
    else:
        # caso ainda aberto: o assunto real está em Objeto, não em Partes
        partes = partes_raw.strip(' .')
        concl = field(b, 'Objeto') or field(b, 'Decisão/Conclusão') or partes_raw
    pm = re.search(r'apurar\s+(.+?)(?:\.\s|\. |$)', concl, re.I)
    purpose = pm.group(1) if pm else concl
    title = cap(clean(purpose)) or clean(concl) or "Caso do Ministério Público"
    plain = None
    for k,v in MP_OUT.items():
        if k in status: plain = v; break
    line = []
    if partes: line.append(f"<b>Partes:</b> {esc(clean(partes))}")
    if plain: line.append(esc(plain))
    return {"ymd":ymd, "status":status, "cls":pill_cls(status),
            "title":esc(title), "line":" · ".join(line), "ref":esc(proc_of(header)), "src":"MP"}

def tce_case(b):
    header = b.split('\n',1)[0].strip()
    star = header[0] if header else '·'
    status = status_of(b); ymd = date_of(b)
    assunto = field(b,'Assunto'); ug = field(b,'Unidade gestora'); val = field(b,'Valores citados')
    if not keep_tce_case(status, star, assunto):
        return None
    title = cap(clean(assunto)) or clean(ug) or "Processo do Tribunal de Contas"
    line = []
    if ug:  line.append(f"<b>{esc(clean(ug))}</b>")
    if val: line.append("Valores: " + esc(clean(val)))
    hm = re.match(r'([A-Z@]{2,4}\s?\d{2}/\d{5,})', header)
    return {"ymd":ymd, "status":status, "cls":pill_cls(status),
            "title":esc(title), "line":" · ".join(line), "ref":esc(hm.group(1) if hm else ''), "src":"TCE"}

def card(c, color):
    y,m,d = c["ymd"]
    dm = f"{d:02d} {MESES_PT.get(m,'')}" if m else ""
    src_badge = f'<span class="src {c["src"].lower()}">{c["src"]}</span>'
    return f'''<div class="case">
      <div class="rail" style="--rc:{color}"><div class="yr">{y or ''}</div><div class="dm">{dm}</div></div>
      <div class="body">
        <div class="pl"><span class="pill {c['cls']}">{esc(c['status'])}</span>{src_badge}</div>
        <h3>{c['title']}</h3>
        <div class="ln">{c['line']}</div>
        <div class="ref">{c['ref']}</div>
      </div></div>'''

def city_block(city, mp_secs, tce_secs):
    color = CITY_COLOR[city]; fin = FINANCAS.get(city, {})
    imgs = IMGS.get(city, {})
    flag = imgs.get("bandeira"); bras = imgs.get("brasao")
    flag_html = f'<img class="c-flag" src="{flag}">' if flag else ''
    bras_html = f'<img class="c-bras" src="{bras}">' if bras else ''
    cs = [c for c in (mp_case(b) for b in blocks(mp_secs.get(city,""))) if c] + \
         [c for c in (tce_case(b) for b in blocks(tce_secs.get(city,""))) if c]
    cs.sort(key=lambda c: c["ymd"], reverse=True)
    n_mp = sum(1 for c in cs if c["src"]=="MP"); n_tce = len(cs)-n_mp
    info = f'''<div class="cinfo">
        <div class="ci"><span class="cl">População</span><b>{fmt_pop(fin.get("pop",0))}</b><span class="cu">Censo 2022</span></div>
        <div class="ci"><span class="cl">Arrecadou 2025</span><b>{fmt_brl(fin.get("rec",0))}</b><span class="cu">receita realizada</span></div>
        <div class="ci"><span class="cl">Gastou 2025</span><b>{fmt_brl(fin.get("desp",0))}</b><span class="cu">despesa empenhada</span></div>
      </div>''' if fin else ''
    cards = "\n".join(card(c, color) for c in cs)
    html = f'''<section class="cityblock" style="--city:{color}">
      <div class="cityhead">
        <div class="h-t"><div class="small">Região Carbonífera · AMREC</div><div class="big">{esc(city)}</div></div>
        <img class="h-logo" src="{ASSETS}/logo-preto.png">
      </div>
      <div class="csymbols">{flag_html}{bras_html}{info}</div>
      <div class="ccount">{len(cs)} casos selecionados · {n_mp} do Ministério Público · {n_tce} do Tribunal de Contas</div>
      {cards}
    </section>'''
    return html, len(cs)

CSS = open(os.path.join(os.path.dirname(__file__),"amrec_full_css.css")).read()

def build():
    mp = sections(MP_MD); tce = sections(TCE_MD)
    cover = open(os.path.join(os.path.dirname(__file__),"amrec_cover.html")).read()
    cta   = open(os.path.join(os.path.dirname(__file__),"amrec_cta.html")).read()
    raw_total = sum(len(blocks(mp.get(c,"")))+len(blocks(tce.get(c,""))) for c in ORDEM)
    kept_total = 0
    parts = []
    for c in ORDEM:
        html_c, n_kept = city_block(c, mp, tce)
        parts.append(html_c)
        kept_total += n_kept
    body = "\n".join(parts)
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>{cover}<div class="doc">{body}</div>{cta}</body></html>""", raw_total, kept_total

if __name__ == "__main__":
    out, raw_total, kept_total = build()
    open(os.path.join(os.path.dirname(__file__),"amrec_full.html"),"w").write(out)
    pct = 100*kept_total/raw_total if raw_total else 0
    print(f"amrec_full.html gerado: {len(out)} bytes · {kept_total}/{raw_total} casos mantidos ({pct:.0f}%) · 12 cidades")
