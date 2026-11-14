#!/usr/bin/env python3
"""Coleta, para UMA cidade, o que saiu nos diários oficiais e fontes públicas.

Fontes:
  municipal  Diário do município (próprio, como o de Criciúma, ou DOM/SC via CIGA)
  doe        Diário Oficial do Estado de SC (busca de texto do portal DOE)
  dou        Diário Oficial da União (busca do in.gov.br)
  djen       Diário de Justiça Eletrônico Nacional, TJSC (partes = município)
  pncp       Portal Nacional de Contratações Públicas (compras no município)
  mpsc       Diário Oficial do MPSC (PDF; trechos que citam a cidade)
  tcesc      Diário Oficial do TCE-SC (PDF; trechos que citam a cidade)

Uso:
  python3 -I diarios/coletar.py criciuma                 # últimos 7 dias, todas as fontes
  python3 -I diarios/coletar.py criciuma --dias 30
  python3 -I diarios/coletar.py criciuma --fontes dou,doe
  python3 -I diarios/coletar.py icara --inicio 2026-10-01 --fim 2026-10-31

A cidade vem de diarios/cidades.json. Saída em diarios/dados/<cidade>/<fim>/.
Só usa a biblioteca padrão do Python e o `pdftotext` (poppler).
"""
import argparse
import datetime as dt
import html
import io
import json
import re
import subprocess
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
CACHE = RAIZ / "cache"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"


# ---------------------------------------------------------------- utilidades

def http(url, data=None, headers=None, timeout=90, tentativas=4):
    h = {"User-Agent": UA, "Accept": "*/*"}
    h.update(headers or {})
    if isinstance(data, (dict, list)):
        data = json.dumps(data).encode()
        h["Content-Type"] = "application/json"
    erro = None
    for i in range(tentativas):
        try:
            req = urllib.request.Request(url, data=data, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (404, 400, 401, 403):
                raise
            erro = e
            if e.code == 429:  # limite de requisições (PNCP): espera mais
                time.sleep(15 * (i + 1))
                continue
        except Exception as e:  # timeout, conexão
            erro = e
        time.sleep(2 * (i + 1))
    raise erro


def http_json(url, **kw):
    return json.loads(http(url, **kw).decode("utf-8"))


def baixar(url, destino):
    """Baixa para o cache (se ainda não existe). Devolve o caminho ou None em 404."""
    destino = Path(destino)
    if destino.exists() and destino.stat().st_size > 0:
        return destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    try:
        corpo = http(url, timeout=180)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    destino.write_bytes(corpo)
    return destino


def pdf_texto(pdf):
    txt = Path(pdf).with_suffix(".txt")
    if not txt.exists():
        subprocess.run(["pdftotext", "-layout", str(pdf), str(txt)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return txt.read_text(encoding="utf-8", errors="replace")


def sem_html(s):
    s = re.sub(r"(?is)<(script|style|head)\b.*?</\1>", " ", s or "")
    s = re.sub(r"(?i)<br\s*/?>|</p>|</tr>|</div>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n", s).strip()


def dobrar(s):
    """minúsculas sem acento, preservando o comprimento (para casar posições)."""
    return "".join((unicodedata.normalize("NFKD", c)[:1] or c).lower() for c in s)


def trechos(texto, termos, raio=350, maximo=50):
    """Janelas de texto em volta de cada menção, fundindo as sobrepostas."""
    base = dobrar(texto)
    pos = sorted(m.start() for t in termos
                 for m in re.finditer(r"\b" + re.escape(dobrar(t)) + r"\b", base))
    janelas = []
    for p in pos:
        a, b = max(0, p - raio), min(len(texto), p + raio)
        if janelas and a <= janelas[-1][1]:
            janelas[-1][1] = b
        else:
            janelas.append([a, b])
    return [re.sub(r"\s+", " ", texto[a:b]).strip() for a, b in janelas[:maximo]]


def titulo_trecho(t, termos, raio=80):
    base = dobrar(t)
    m = min((x.start() for k in termos for x in re.finditer(re.escape(dobrar(k)), base)), default=0)
    a = max(0, m - raio)
    a = t.find(" ", a) + 1 if a else 0
    return ("…" if a else "") + t[a:m + raio].strip() + "…"


def menciona(texto, termos):
    base = dobrar(texto or "")
    return any(re.search(r"\b" + re.escape(dobrar(t)) + r"\b", base) for t in termos)


def dias(inicio, fim):
    d = inicio
    while d <= fim:
        yield d
        d += dt.timedelta(days=1)


def meses(inicio, fim):
    vistos = []
    for d in dias(inicio, fim):
        if (d.year, d.month) not in vistos:
            vistos.append((d.year, d.month))
    return vistos


def item(fonte, data, titulo, url, orgao="", categoria="", trecho="", **extra):
    return {"fonte": fonte, "data": str(data)[:10], "titulo": (titulo or "").strip(),
            "orgao": (orgao or "").strip(), "categoria": (categoria or "").strip(),
            "url": url, "trecho": (trecho or "").strip()[:1500], **extra}


# ---------------------------------------------------------------- fontes

TITULO_ATO = re.compile(
    r"^\s*((?:DECRETO|PORTARIA|LEI(?: COMPLEMENTAR)?|RESOLU[ÇC][ÃA]O|EXTRATO|AVISO|EDITAL|"
    r"TERMO|CONTRATO|ATA|ERRATA|INSTRU[ÇC][ÃA]O NORMATIVA|RETIFICA[ÇC][ÃA]O|DESPACHO|"
    r"HOMOLOGA[ÇC][ÃA]O|ADJUDICA[ÇC][ÃA]O|DISPENSA|INEXIGIBILIDADE|RATIFICA[ÇC][ÃA]O)"
    r"\b[^\n]{0,160})$", re.M)


def f_municipal(cid, ini, fim):
    cfg = cid.get("diario_municipal") or {}
    if cfg.get("tipo") == "criciuma":
        return municipal_criciuma(cid, ini, fim)
    if cfg.get("tipo") == "domsc":
        return municipal_domsc(cid, cfg.get("municipio") or cid["nome"], ini, fim)
    return []


def municipal_criciuma(cid, ini, fim):
    """Diário Oficial Eletrônico de Criciúma: um PDF por dia em criciuma.sc.gov.br/does.php."""
    urls = set()
    for ano, mes in meses(ini, fim):
        pag = http(f"https://www.criciuma.sc.gov.br/does.php?ano={ano}&mes={mes:02d}").decode("utf-8", "replace")
        urls |= set(re.findall(r"https://apoio\.criciuma\.sc\.gov\.br/files/[^\"'\s]+\.pdf", pag))
    saida = []
    for url in sorted(urls):
        m = re.search(r"/files/(\d{4}-\d{2}-\d{2})-", url)
        if not m or not (ini.isoformat() <= m.group(1) <= fim.isoformat()):
            continue
        data = m.group(1)
        pdf = baixar(url, CACHE / "criciuma" / Path(url).name)
        if not pdf:
            continue
        texto = pdf_texto(pdf)
        atos = [re.sub(r"\s+", " ", t).strip() for t in TITULO_ATO.findall(texto)]
        vistos = []
        for a in atos:
            if a not in vistos:
                vistos.append(a)
        saida.append(item("municipal", data, f"Diário Oficial de Criciúma de {data}", url,
                          orgao="Prefeitura de Criciúma", categoria="edição",
                          trecho=texto[:800], atos=vistos, texto_local=str(pdf.with_suffix(".txt"))))
    return saida


def municipal_domsc(cid, municipio, ini, fim):
    """DOM/SC: dados abertos do CIGA (um ZIP por turno, com JSON de cada ato)."""
    api = "https://dados.ciga.sc.gov.br/api/3/action/package_show?id="
    alvo = dobrar(municipio)
    saida = []
    for ano, mes in meses(ini, fim):
        try:
            pac = http_json(api + f"domsc-publicacoes-de-{mes:02d}-{ano}")["result"]
        except urllib.error.HTTPError:
            continue
        for rec in pac["resources"]:
            m = re.search(r"_(\d{4})_(\d{2})_(\d{2})_\d{4}_\d{4}\.zip$", rec["url"])
            if not m:
                continue
            data = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
            if not (ini.isoformat() <= data <= fim.isoformat()):
                continue
            z = baixar(rec["url"], CACHE / "domsc" / Path(rec["url"]).name)
            if not z:
                continue
            with zipfile.ZipFile(z) as zf:
                for nome in zf.namelist():
                    if not nome.endswith(".json"):
                        continue
                    d = json.loads(zf.read(nome).decode("utf-8"))
                    atos = list(d.get("autopublicacoes") or [])
                    eo = d.get("edicao_ordinaria")
                    if isinstance(eo, dict):
                        atos += eo.get("atos") or []
                    for a in atos:
                        if dobrar(a.get("municipio") or "") != alvo:
                            continue
                        saida.append(item("municipal", a.get("data"), a.get("titulo"), a.get("link"),
                                          orgao=a.get("entidade"), categoria=a.get("categoria"),
                                          trecho=sem_html(a.get("texto"))[:1500], codigo=a.get("codigo")))
    return saida


def f_doe(cid, ini, fim):
    """DOE-SC: busca de texto (mesma API da tela 'Buscar matéria' do portal)."""
    url = "https://portal.doe.sea.sc.gov.br/apis/busca-materia"
    vistos, saida = set(), []
    for termo in cid["termos"]:
        de = 0
        while True:
            corpo = {"busca": termo, "dtIni": ini.isoformat(), "dtFim": fim.isoformat(), "tipoBusca": 1,
                     "pagination": {"from": de, "size": 50}, "resumo": False}
            r = http_json(url, data=corpo)
            mats = r.get("materias") or []
            novos = [m for m in mats if m["id"] not in vistos]
            for m in novos:
                vistos.add(m["id"])
                texto = ""
                try:
                    texto = sem_html(http(m["preview"]).decode("utf-8", "replace"))
                except Exception:
                    pass
                tre = " … ".join(trechos(texto, cid["termos"], maximo=3)) or m.get("resumo", "")
                saida.append(item("doe", m["publicacao"], (m.get("resumo") or "")[:140],
                                  f"https://portal.doe.sea.sc.gov.br/#/portal/edicao/{m['cdJornal']}/materia/{m['id']}",
                                  orgao=m.get("categoria"), categoria=m.get("assunto"), trecho=tre,
                                  edicao=m.get("nrJornal"), da_prefeitura=dobrar(m.get("categoria") or "") == dobrar(cid["nome"])))
            de += 50
            if not mats or de >= (r.get("total") or 0):
                break
    return saida


def f_dou(cid, ini, fim):
    """DOU: busca do in.gov.br (JSON embutido na página de resultados)."""
    saida, vistos = [], set()
    for termo in cid["termos"]:
        for pagina in range(1, 21):
            q = urllib.parse.urlencode({
                "q": f'"{termo}"', "s": "todos", "exactDate": "personalizado",
                "publishFrom": ini.strftime("%d-%m-%Y"), "publishTo": fim.strftime("%d-%m-%Y"),
                "sortType": "0", "delta": "50", "currentPage": str(pagina), "newPage": str(pagina)})
            pag = http("https://www.in.gov.br/consulta/-/buscar/dou?" + q).decode("utf-8", "replace")
            m = re.search(r'BuscaDouPortlet_params"[^>]*>(.*?)</script>', pag, re.S)
            lista = json.loads(m.group(1)).get("jsonArray", []) if m else []
            novos = [x for x in lista if x["urlTitle"] not in vistos]
            for x in novos:
                vistos.add(x["urlTitle"])
                d, mth, a = x["pubDate"].split("/")
                saida.append(item("dou", f"{a}-{mth}-{d}", x.get("title"),
                                  "https://www.in.gov.br/web/dou/-/" + x["urlTitle"],
                                  orgao=x.get("hierarchyStr"), categoria=x.get("artType"),
                                  trecho=sem_html(x.get("content")), secao=x.get("pubName")))
            if len(lista) < 50 or not novos:
                break
            time.sleep(1)
    return saida


# Classes que interessam à fiscalização; o resto (execução fiscal, RPV etc.) é rotina.
DESTAQUE_DJEN = re.compile(r"improbidade|civil p[úu]blica|a[çc][ãa]o popular|mandado de seguran|penal|crim|"
                           r"inqu[ée]rito|den[úu]ncia|cautelar|tutela", re.I)
ROTINA_DJEN = re.compile(r"execu[çc][ãa]o fiscal|cumprimento de senten|juizado especial da fazenda|"
                         r"usucapi|invent[áa]rio|retifica[çc][ãa]o de registro|recurso inominado", re.I)


def f_djen(cid, ini, fim):
    """DJEN (CNJ): comunicações do TJSC em que o município é parte."""
    api = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"
    saida, vistos = [], set()
    for parte in cid.get("partes_djen") or []:
        for pagina in range(1, 51):
            q = urllib.parse.urlencode({"siglaTribunal": "TJSC", "nomeParte": parte,
                                        "dataDisponibilizacaoInicio": ini.isoformat(),
                                        "dataDisponibilizacaoFim": fim.isoformat(),
                                        "itensPorPagina": 100, "pagina": pagina})
            r = http_json(f"{api}?{q}")
            itens = r.get("items") or []
            for x in itens:
                if x["id"] in vistos:
                    continue
                vistos.add(x["id"])
                classe = x.get("nomeClasse") or ""
                texto = sem_html(x.get("texto"))
                partes = [p.get("nome") for p in x.get("destinatarios") or []]
                saida.append(item("djen", x.get("data_disponibilizacao"),
                                  f"{classe} {x.get('numeroprocessocommascara') or ''}".strip(),
                                  x.get("link") or f"https://comunica.pje.jus.br/consulta?numeroProcesso={x.get('numero_processo')}",
                                  orgao=x.get("nomeOrgao"), categoria=x.get("tipoComunicacao"),
                                  trecho=texto[:1200], processo=x.get("numeroprocessocommascara"), partes=partes,
                                  classe=classe, rotina=bool(ROTINA_DJEN.search(classe)),
                                  destaque=bool(DESTAQUE_DJEN.search(classe) or re.search(r"(?i)improbidade", texto))))
            if len(itens) < 100:
                break
            time.sleep(1)
    return saida


MODALIDADES = {1: "Leilão eletrônico", 2: "Diálogo competitivo", 3: "Concurso", 4: "Concorrência eletrônica",
               5: "Concorrência presencial", 6: "Pregão eletrônico", 7: "Pregão presencial", 8: "Dispensa",
               9: "Inexigibilidade", 10: "Manifestação de interesse", 11: "Pré-qualificação",
               12: "Credenciamento", 13: "Leilão presencial"}


def f_pncp(cid, ini, fim):
    """PNCP: contratações publicadas por órgãos sediados no município (todas as esferas)."""
    api = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
    saida = []
    for cod, nome in MODALIDADES.items():
        for pagina in range(1, 21):
            q = urllib.parse.urlencode({"dataInicial": ini.strftime("%Y%m%d"), "dataFinal": fim.strftime("%Y%m%d"),
                                        "codigoModalidadeContratacao": cod, "codigoMunicipioIbge": cid["ibge"],
                                        "pagina": pagina, "tamanhoPagina": 50})
            try:
                corpo = http(f"{api}?{q}")
            except urllib.error.HTTPError as e:
                if e.code in (400, 404):
                    break
                raise
            if not corpo.strip():
                break
            r = json.loads(corpo)
            for x in r.get("data") or []:
                org, uni = x.get("orgaoEntidade") or {}, x.get("unidadeOrgao") or {}
                url = f"https://pncp.gov.br/app/editais/{org.get('cnpj')}/{x.get('anoCompra')}/{x.get('sequencialCompra')}"
                valor = x.get("valorTotalHomologado") or x.get("valorTotalEstimado")
                saida.append(item("pncp", x.get("dataPublicacaoPncp"), x.get("objetoCompra"), url,
                                  orgao=f"{org.get('razaoSocial')} / {uni.get('nomeUnidade')}",
                                  categoria=x.get("modalidadeNome") or nome,
                                  trecho=x.get("informacaoComplementar") or "",
                                  valor=valor, esfera=org.get("esferaId"), cnpj_orgao=org.get("cnpj"),
                                  processo=x.get("processo"), situacao=x.get("situacaoCompraNome"),
                                  amparo=(x.get("amparoLegal") or {}).get("nome")))
            if pagina >= (r.get("totalPaginas") or 1):
                break
            time.sleep(1)
        time.sleep(1)
    return saida


def _pdf_por_dia(fonte, nome_cache, urls_por_dia, cid, ini, fim):
    saida = []
    for data, url in urls_por_dia:
        pdf = baixar(url, CACHE / nome_cache / (Path(urllib.parse.urlparse(url).path).name.removesuffix(".pdf") + ".pdf"))
        if not pdf:
            continue
        texto = pdf_texto(pdf)
        for t in trechos(texto, cid["termos"]):
            # escalas, plantões e listas de lotação: várias matrículas (000.000-0) no mesmo trecho
            if len(re.findall(r"\b\d{3}\.\d{3}-\d\b", t)) >= 2:
                continue
            saida.append(item(fonte, data, titulo_trecho(t, cid["termos"]), url, trecho=t))
    return saida


def f_mpsc(cid, ini, fim):
    idx = http("https://intranet.mpsc.mp.br/spo/diariooficial/index?" + urllib.parse.urlencode(
        {"dt_inicio": ini.isoformat(), "dt_fim": fim.isoformat(), "orgao": -1, "tipo": -1, "q": ""}),
        timeout=120).decode("utf-8", "replace")
    urls = sorted(set(re.findall(r"https://www\.mpsc\.mp\.br/documents/d/guest/do_mpsc_[A-Za-z0-9._-]+", idx)))
    pares = []
    for u in urls:
        m = re.search(r"(\d{4}-\d{2}-\d{2})", u)
        if m:
            pares.append((m.group(1), u))
    return _pdf_por_dia("mpsc", "mpsc", pares, cid, ini, fim)


def f_tcesc(cid, ini, fim):
    pares = []
    for d in dias(ini, fim):
        if d.weekday() < 5:
            for suf in ("", "-E"):
                pares.append((d.isoformat(), f"https://consulta.tce.sc.gov.br/Diario/dotc-e{d.isoformat()}{suf}.pdf"))
    return _pdf_por_dia("tcesc", "tcesc", pares, cid, ini, fim)


FONTES = {"municipal": f_municipal, "doe": f_doe, "dou": f_dou, "djen": f_djen,
          "pncp": f_pncp, "mpsc": f_mpsc, "tcesc": f_tcesc}
NOMES = {"municipal": "Diário do município", "doe": "DOE-SC", "dou": "DOU", "djen": "DJEN / TJSC",
         "pncp": "PNCP (compras)", "mpsc": "Diário do MPSC", "tcesc": "Diário do TCE-SC"}


# ---------------------------------------------------------------- resumo

def brl(v):
    try:
        return "R$ " + f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return ""


def resumo_md(cid, ini, fim, resultados, erros):
    L = [f"# {cid['nome']}/{cid['uf']}: diários de {ini:%d/%m/%Y} a {fim:%d/%m/%Y}", "",
         f"Gerado em {dt.datetime.now():%d/%m/%Y %H:%M}. Material bruto: confira na fonte antes de publicar.", "",
         "| Fonte | Itens |", "|---|---|"]
    for f in FONTES:
        if f in resultados or f in erros:
            L.append(f"| {NOMES[f]} | {('ERRO: ' + erros[f]) if f in erros else len(resultados[f])} |")
    for f, itens in resultados.items():
        L += ["", f"## {NOMES[f]} ({len(itens)})", ""]
        if f == "djen":
            cont = {}
            for x in itens:
                cont[x.get("classe") or "?"] = cont.get(x.get("classe") or "?", 0) + 1
            L += ["| Classe | Qtd |", "|---|---|"] + [f"| {k} | {v} |" for k, v in sorted(cont.items(), key=lambda kv: -kv[1])]
            rotina = sum(1 for x in itens if x.get("rotina") and not x.get("destaque"))
            L += ["", f"Abaixo só o que não é rotina ({rotina} de rotina ficam no djen.json).", ""]
            itens = sorted([x for x in itens if x.get("destaque") or not x.get("rotina")],
                           key=lambda x: not x.get("destaque"))
        for x in itens[:200]:
            if f == "municipal" and x.get("atos") is not None:
                L.append(f"- **{x['data']}** [{x['titulo']}]({x['url']}): {len(x['atos'])} atos")
                L += [f"  - {a}" for a in x["atos"][:60]]
                continue
            extra = []
            if x.get("valor"):
                extra.append(brl(x["valor"]))
            if x.get("destaque"):
                extra.append("**destaque**")
            if x.get("da_prefeitura"):
                extra.append("publicação da prefeitura")
            cab = " · ".join(p for p in [x["categoria"], x["orgao"], *extra] if p)
            L.append(f"- **{x['data']}** [{x['titulo'] or '(sem título)'}]({x['url']})" + (f": {cab}" if cab else ""))
            if x["trecho"] and f in ("mpsc", "tcesc", "dou", "doe"):
                L.append(f"  > {x['trecho'][:500]}")
        if len(itens) > 200:
            L.append(f"- … mais {len(itens) - 200} no JSON")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cidade", help="chave em diarios/cidades.json (ex.: criciuma)")
    ap.add_argument("--dias", type=int, default=7, help="janela até hoje (padrão 7)")
    ap.add_argument("--inicio")
    ap.add_argument("--fim")
    ap.add_argument("--fontes", default=",".join(FONTES), help="lista separada por vírgula")
    a = ap.parse_args()

    cidades = json.loads((RAIZ / "cidades.json").read_text(encoding="utf-8"))
    if a.cidade not in cidades:
        sys.exit(f"cidade '{a.cidade}' não está em cidades.json ({', '.join(cidades)})")
    cid = cidades[a.cidade]
    fim = dt.date.fromisoformat(a.fim) if a.fim else dt.date.today()
    ini = dt.date.fromisoformat(a.inicio) if a.inicio else fim - dt.timedelta(days=a.dias)

    out = RAIZ / "dados" / a.cidade / fim.isoformat()
    out.mkdir(parents=True, exist_ok=True)
    resultados, erros = {}, {}
    for f in [x.strip() for x in a.fontes.split(",") if x.strip()]:
        if f not in FONTES:
            sys.exit(f"fonte desconhecida: {f}")
        t0 = time.time()
        print(f"{NOMES[f]:<22}", end=" ", flush=True)
        try:
            itens = FONTES[f](cid, ini, fim)
            itens.sort(key=lambda x: x["data"], reverse=True)
            resultados[f] = itens
            (out / f"{f}.json").write_text(json.dumps(itens, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"{len(itens):>5} itens  ({time.time() - t0:.0f}s)")
        except Exception as e:
            erros[f] = f"{type(e).__name__}: {e}"[:200]
            print(f"ERRO {erros[f]}")
    (out / "resumo.md").write_text(resumo_md(cid, ini, fim, resultados, erros), encoding="utf-8")
    print(f"\nSaída: {out}/resumo.md")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
