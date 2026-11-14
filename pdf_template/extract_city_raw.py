#!/usr/bin/env python3
"""Extrai os casos de cada cidade de uma região, a partir dos MDs de região, no
schema que o gerador de PDF consome (`{city, mp[], tce[]}`).

Por que ler o MD e não o `parsed/*.json`: o scrape bruto não existe mais nesta
máquina, então os MDs são a única fonte disponível. O problema é que os MDs no
disco são anteriores à correção de atribuição de cidade em `build_regioes.py` —
um caso que só tramita na comarca de Criciúma aparecia também na seção de
Treviso. Por isso a atribuição é **reaplicada aqui**, com a mesma regra da
origem: menção institucional explícita ("Prefeitura/Município de X") decide; a
comarca só vale quando o texto não cita município nenhum.

Uso:
    python3 extract_city_raw.py amrec --out /tmp/raw_amrec   # validação
    python3 extract_city_raw.py amesc --out <dir>
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from build_regioes import REGIOES, TODAS_CIDADES, build_matchers, regiao_slug  # noqa: E402

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
MP_DIR = os.path.join(REPO, "resumos", "regioes")
TCE_DIR = os.path.join(REPO, "tcesc", "resumos", "regioes")

PREFIXED, BARE, LOWER2CANON = build_matchers()


def slugify(city: str) -> str:
    s = unicodedata.normalize("NFKD", city).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def city_section(md_text: str, city: str) -> str:
    """Recorta a seção '## <Cidade>' até o próximo '## '."""
    pat = re.compile(r"^## " + re.escape(city) + r"\s*$(.*?)(?=^## |\Z)", re.S | re.M)
    m = pat.search(md_text)
    return m.group(1) if m else ""


def parse_blocks(section: str):
    """Cada caso no MD é um bloco que começa em '#### '. Devolve o header e o
    corpo bruto de cada um."""
    parts = re.split(r"^#### ", section, flags=re.M)[1:]
    for p in parts:
        header, _, body = p.partition("\n")
        yield header.strip(), body


def field(body: str, label: str) -> str:
    m = re.search(r"\*\*" + label + r":\*\*\s*(.*?)(?=\n\n|\n\*\*|\Z)", body, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def meta_field(body: str, label: str) -> str:
    """Campos que vivem na linha de metadados separados por ' · '."""
    m = re.search(r"\*\*" + label + r":\*\*\s*([^·\n]+)", body)
    return m.group(1).strip() if m else ""


def edicao_ymd(body: str):
    m = re.search(r"\*\*Edição:\*\*\s*\[?(\d{4})-(\d{2})-(\d{2})", body)
    return [int(m.group(1)), int(m.group(2)), int(m.group(3))] if m else [0, 0, 0]


def attribute(blob: str, comarca: str) -> set:
    """Mesma regra de build_regioes.py: menção explícita ganha da comarca."""
    matched = {LOWER2CANON.get(m.group(1).lower()) for m in PREFIXED.finditer(blob)}
    matched.discard(None)
    if not matched and comarca:
        matched = {LOWER2CANON.get(m.group(1).lower()) for m in BARE.finditer(comarca.lower())}
        matched.discard(None)
    return matched


def extract_mp(section: str, city: str):
    out = []
    for header, body in parse_blocks(section):
        partes = field(body, "Partes")
        comarca = meta_field(body, "Comarca")
        if city not in attribute(f"{partes} {header}", comarca):
            continue
        ref = re.search(r"([0-9]{2}\.[0-9]{4}\.[0-9]{8}-[0-9])", header)
        out.append({
            "ref": ref.group(1) if ref else header,
            "header": header,
            "status": meta_field(body, "Status"),
            "ymd": edicao_ymd(body),
            "partes": partes,
        })
    return out


def extract_tce(section: str, city: str):
    out = []
    for header, body in parse_blocks(section):
        blob = " ".join(field(body, k) for k in ("Unidade gestora", "Assunto", "Responsáveis/Partes"))
        # o TCE não tem comarca; a unidade gestora já nomeia o município
        if city not in attribute(f"{blob} {header}", ""):
            continue
        ref = re.match(r"(?:[⭐•·]\s*)?([A-Z@]{2,5}[\s-]?[\d/]+)", header)
        out.append({
            "ref": (ref.group(1) if ref else header).strip(),
            "header": header,
            "status": meta_field(body, "Status"),
            "ymd": edicao_ymd(body),
            "partes": blob,
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("regiao", help="sigla da região, ex.: amesc")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    sig = args.regiao.lower()
    cities = next((cs for r, cs in REGIOES.items() if regiao_slug(r) == sig), None)
    if not cities:
        sys.exit(f"região desconhecida: {sig}")

    mp_md = open(os.path.join(MP_DIR, f"regiao-{sig}.md")).read()
    tce_path = os.path.join(TCE_DIR, f"regiao-{sig}-tce.md")
    tce_md = open(tce_path).read() if os.path.exists(tce_path) else ""

    os.makedirs(args.out, exist_ok=True)
    for city in cities:
        mp = extract_mp(city_section(mp_md, city), city)
        tce = extract_tce(city_section(tce_md, city), city) if tce_md else []
        path = os.path.join(args.out, f"{slugify(city)}.json")
        json.dump({"city": city, "mp": mp, "tce": tce},
                  open(path, "w"), ensure_ascii=False, indent=1)
        print(f"{city:32} mp={len(mp):4}  tce={len(tce):4}")


if __name__ == "__main__":
    main()
