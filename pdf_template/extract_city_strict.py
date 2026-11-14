#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extração por cidade com atribuição estrita, para as regiões cujos MDs são
anteriores à correção de atribuição (granfpolis, amurc, amplasc, ...).

O `extract_city_raw.py` decide a cidade por menção institucional no cabeçalho e
nas partes. Isso basta nas regiões já corrigidas, mas nestas os registros do TCE
vêm do parser com dois processos concatenados por ' | ' num só bloco:

    **Unidade gestora:** Prefeitura Municipal de Curitibanos | Câmara de Vereadores de Içara
    **Assunto:** ...kits escolares... | ...servidores comissionados...
    **Decisão:** ...a Câmara de Vereadores de Içara comprovou a extinção do cargo...

Atribuir esse bloco a Curitibanos produz um card afirmando sobre Curitibanos o
que o tribunal decidiu sobre Içara. Duas regras novas evitam isso:

  1. **A decisão manda.** O dispositivo é o texto operativo — o que o tribunal
     de fato decidiu. Se ele nomeia municípios, a cidade tem de estar entre eles.
     Bloco cuja decisão só fala de outra cidade é descartado.
  2. **Segmento certo.** Nos campos com ' | ', só o segmento que menciona a
     cidade é carregado adiante, para a revisão editorial não ler o objeto de um
     processo ao lado do desfecho de outro.

Casos sem decisão no MD saem marcados com `sem_decisao`, para a curadoria saber
que ali não há desfecho a afirmar.

Uso:
    python3 extract_city_strict.py amurc --cidade Curitibanos --out <dir>
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from build_regioes import build_matchers, regiao_slug, REGIOES  # noqa: E402

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
MP_DIR = os.path.join(REPO, "resumos", "regioes")
TCE_DIR = os.path.join(REPO, "tcesc", "resumos", "regioes")

PREFIXED, BARE, LOWER2CANON = build_matchers()


def slugify(city: str) -> str:
    s = unicodedata.normalize("NFKD", city).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def city_section(md_text: str, city: str) -> str:
    pat = re.compile(r"^## " + re.escape(city) + r"\s*$(.*?)(?=^## |\Z)", re.S | re.M)
    m = pat.search(md_text)
    return m.group(1) if m else ""


def parse_blocks(section: str):
    for p in re.split(r"^#### ", section, flags=re.M)[1:]:
        header, _, body = p.partition("\n")
        yield header.strip(), body


def field(body: str, label: str) -> str:
    m = re.search(r"\*\*" + label + r":\*\*\s*(.*?)(?=\n\*\*|\n\n|\Z)", body, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def meta_field(body: str, label: str) -> str:
    m = re.search(r"\*\*" + label + r":\*\*\s*([^·\n]+)", body)
    return m.group(1).strip() if m else ""


def edicao_ymd(body: str):
    m = re.search(r"\*\*Edição:\*\*\s*\[?(\d{4})-(\d{2})-(\d{2})", body)
    return [int(m.group(1)), int(m.group(2)), int(m.group(3))] if m else [0, 0, 0]


# A sede dos dois órgãos. "Florianópolis, 26 de agosto de 2025" fecha quase todo
# dispositivo do TCE, e ler isso como atribuição descartaria metade dos casos
# legítimos de qualquer cidade do interior.
SEDES = {"Florianópolis"}


# O PREFIXED da origem só cobre "município/prefeitura/comarca de X". No
# dispositivo do TCE o sujeito costuma ser outro órgão — foi assim que
# "Câmara de Vereadores de Içara" passou batido dentro de um caso de
# Curitibanos. Aqui a lista de instituições é aberta, mas continua exigindo uma
# âncora institucional antes do nome, que é o que separa o município de Irani do
# conselheiro chamado Irani.
ORGAOS = (r"munic[íi]pio|prefeitura(?:\s+municipal)?|comarca|c[âa]mara(?:\s+municipal|"
          r"\s+de\s+vereadores)?|fundo\s+municipal[^,;|]{0,40}?|instituto[^,;|]{0,40}?|"
          r"autarquia[^,;|]{0,40}?|servi[çc]o\s+aut[ôo]nomo[^,;|]{0,40}?|"
          r"secretaria[^,;|]{0,40}?|hospital[^,;|]{0,40}?|samae|saae")
_ALT = "|".join(re.escape(c) for c in sorted(LOWER2CANON.values(), key=len, reverse=True))
INSTITUCIONAL = re.compile(rf"(?:{ORGAOS})\s+(?:de\s+|do\s+|da\s+)?({_ALT})(?![A-Za-zÀ-ÿ])",
                           re.IGNORECASE)


def cidades_citadas(txt: str, institucional=False) -> set:
    """Municípios nomeados num texto.

    `institucional=True` exige âncora de órgão antes do nome. É o modo certo
    para texto corrido: o matcher de nome nu casa com sobrenome de conselheiro —
    "Conselheiro Relator Irani" virava o município de Irani e derrubava o caso.
    """
    if institucional:
        achadas = {LOWER2CANON.get(m.group(1).lower()) for m in INSTITUCIONAL.finditer(txt)}
    else:
        achadas = {LOWER2CANON.get(m.group(1).lower()) for m in PREFIXED.finditer(txt)}
        achadas |= {LOWER2CANON.get(m.group(1).lower()) for m in BARE.finditer(txt.lower())}
    achadas.discard(None)
    return achadas - SEDES


def segmento_da_cidade(valor: str, city: str) -> str:
    """Dos trechos separados por ' | ', devolve os que citam a cidade.

    Quando nenhum cita (campo genérico, sem nome de município), devolve o valor
    inteiro — cortar aí perderia informação verdadeira."""
    if "|" not in valor:
        return valor
    partes = [p.strip() for p in valor.split("|")]
    da_cidade = [p for p in partes if city in cidades_citadas(p)]
    if da_cidade:
        return " | ".join(da_cidade)
    if any(cidades_citadas(p) for p in partes):
        return ""      # todos os segmentos são de outras cidades
    return valor


def extrai(section: str, city: str, tce: bool):
    mantidos, descartados = [], []
    for header, body in parse_blocks(section):
        if tce:
            campos = {k: field(body, k) for k in
                      ("Unidade gestora", "Responsáveis/Partes", "Assunto",
                       "Valores citados", "Decisão")}
            decisao = campos["Decisão"]
            ident = f'{header} {campos["Unidade gestora"]} {campos["Responsáveis/Partes"]} {campos["Assunto"]}'
        else:
            campos = {k: field(body, k) for k in ("Partes", "Objeto")}
            decisao = ""
            comarca = meta_field(body, "Comarca")
            ident = f'{header} {campos["Partes"]}'
            if not cidades_citadas(ident):
                ident = f"{ident} {comarca}"

        # regra 1: a decisão manda quando nomeia municípios
        nas_decisao = cidades_citadas(decisao, institucional=True) if decisao else set()
        if nas_decisao and city not in nas_decisao:
            descartados.append({"header": header, "motivo": "decisão é de outra cidade",
                                "cidades_na_decisao": sorted(nas_decisao)})
            continue
        if city not in cidades_citadas(ident) and city not in nas_decisao:
            continue

        # regra 2: só o segmento da cidade nos campos concatenados
        limpos, perdeu_tudo = {}, False
        for k, v in campos.items():
            if not v:
                continue
            seg = segmento_da_cidade(v, city)
            if v != seg and not seg:
                perdeu_tudo = True
            limpos[k] = seg
        if perdeu_tudo and not limpos.get("Decisão"):
            descartados.append({"header": header, "motivo": "todos os segmentos são de outra cidade"})
            continue

        if tce:
            m = re.match(r"(?:[⭐•·]\s*)?([A-Z@]{2,5}[\s-]?[\d/]+)", header)
            ref = (m.group(1) if m else header).strip()
            partes = " ".join(filter(None, (limpos.get("Unidade gestora"),
                                            limpos.get("Responsáveis/Partes"),
                                            limpos.get("Assunto"))))
        else:
            m = re.search(r"([0-9]{2}\.[0-9]{4}\.[0-9]{8}-[0-9])", header)
            ref = m.group(1) if m else header
            partes = " ".join(filter(None, (limpos.get("Partes"), limpos.get("Objeto"))))

        rec = {"ref": ref, "header": header,
               "status": meta_field(body, "Status"),
               "ymd": edicao_ymd(body), "partes": partes}
        # campos separados além do `partes` concatenado: a semeadura da
        # curadoria precisa saber o que é objeto do processo e o que é parte,
        # senão o título nasce misturando nome de réu com assunto.
        for k, dest in (("Assunto", "assunto"), ("Objeto", "objeto"),
                        ("Unidade gestora", "unidade"),
                        ("Responsáveis/Partes", "responsaveis"),
                        ("Partes", "partes_nomes")):
            if limpos.get(k):
                rec[dest] = limpos[k]
        if limpos.get("Decisão"):
            rec["dispositivo"] = limpos["Decisão"]
        else:
            rec["sem_decisao"] = True
        if limpos.get("Valores citados"):
            rec["valores"] = limpos["Valores citados"]
        mantidos.append(rec)
    return mantidos, descartados


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("regiao")
    ap.add_argument("--cidade", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    sig = args.regiao.lower()
    city = args.cidade
    mp_md = open(os.path.join(MP_DIR, f"regiao-{sig}.md")).read()
    tce_path = os.path.join(TCE_DIR, f"regiao-{sig}-tce.md")
    tce_md = open(tce_path).read() if os.path.exists(tce_path) else ""

    mp, mp_desc = extrai(city_section(mp_md, city), city, tce=False)
    tce, tce_desc = extrai(city_section(tce_md, city), city, tce=True) if tce_md else ([], [])

    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, f"{slugify(city)}.json")
    json.dump({"city": city, "mp": mp, "tce": tce},
              open(path, "w"), ensure_ascii=False, indent=1)

    com_dec = sum(1 for r in tce if r.get("dispositivo"))
    print(f"{city}: mp={len(mp)} tce={len(tce)} (com decisão: {com_dec})")
    print(f"  descartados por atribuição: mp={len(mp_desc)} tce={len(tce_desc)}")
    for d in (mp_desc + tce_desc)[:8]:
        print(f"    - {d['header'][:70]} :: {d['motivo']}"
              + (f" -> {d.get('cidades_na_decisao')}" if d.get("cidades_na_decisao") else ""))
    json.dump({"mp": mp_desc, "tce": tce_desc},
              open(os.path.join(args.out, f"{slugify(city)}__descartados.json"), "w"),
              ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
