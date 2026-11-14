#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Anexa o dispositivo da decisão aos casos do TCE já extraídos.

Por que enriquecer em vez de re-extrair: a curadoria casa com o bruto **por
posição**. Re-extrair o TCE mudaria a contagem e a ordem dos casos, e todo o
trabalho editorial já feito (títulos, descrições, severidade) passaria a apontar
para o processo errado. Aqui a ordem e a quantidade ficam intactas; só entra um
campo novo, casado pelo número do processo.

Uso: python3 enrich_tce.py amesc amrec amurel
"""
import argparse
import glob
import json
import os
import re
import sys

import regiao_config as rc

PARSED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tcesc", "parsed")


def norm_ref(ref: str) -> str:
    """'⭐ REP 19/00389859 — Representação' -> 'REP 19/00389859'."""
    ref = re.sub(r"^[⭐•·\s]+", "", str(ref)).split(" — ")[0].strip()
    return re.sub(r"\s+", " ", ref).upper().strip("@")


# Atos internos do próprio tribunal (portarias de pessoal, licitações da casa,
# avisos administrativos). A segmentação por número de processo às vezes estende
# o bloco até esse conteúdo, e o recorte do dispositivo acaba pescando ali —
# colando a "decisão" errada num processo de município. Como o texto vira
# manchete sobre pessoas reais, o certo é descartar em vez de arriscar.
# Só marcadores INEQUÍVOCOS de ato interno. Uma primeira versão incluía
# "adicional por tempo de serviço", "promoção por antiguidade" e "férias de
# servidor" — e cortou 5.258 dispositivos, porque esses são justamente os
# assuntos de processos municipais legítimos que o TCE julga. O filtro estava
# descartando o conteúdo que queremos.
# "Resolução n. TC-" e "Portaria n. TC-" NÃO servem de marcador: as decisões
# citam o regimento interno do próprio tribunal como fundamento legal o tempo
# todo (4.692 e 947 ocorrências). Incluí-las descartava o conteúdo legítimo.
LIXO_RE = re.compile(
    r"coffee\s*break|"
    r"servidor(?:es)?\s+d[oe]ste\s+Tribunal|quadro\s+de\s+pessoal\s+d[oe]ste\s+Tribunal|"
    r"Diretoria\s+de\s+Gest[ãa]o\s+de\s+Pessoas\s+d[oe]ste\s+Tribunal", re.I)


# Tentei também descartar o dispositivo que cita outros processos sem citar o
# próprio — não funciona: acórdão legítimo referencia processos relacionados o
# tempo todo e quase nunca repete o próprio número no corpo (ele está no
# cabeçalho). Essa regra derrubou o casamento da AMREC de 97% para 60%, punindo
# o comportamento normal. Ficou só o filtro de ato interno do tribunal, que é
# específico e não gera falso positivo.


def build_index():
    """ref -> dispositivo. Se o mesmo processo aparece em várias edições (fases
    distintas), fica com o dispositivo mais longo: é o que traz a decisão de
    mérito, e não um despacho de andamento."""
    idx = {}
    descartados = 0
    for f in glob.glob(os.path.join(PARSED, "*.json")):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        for b in d.get("blocos", []):
            disp = b.get("dispositivo")
            if not disp:
                continue
            k = norm_ref(b.get("numero_processo", ""))
            if not k:
                continue
            if LIXO_RE.search(disp):
                descartados += 1
                continue
            if len(disp) > len(idx.get(k, "")):
                idx[k] = disp
    print(f"descartados por não pertencerem ao processo: {descartados}")
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("regioes", nargs="+")
    args = ap.parse_args()

    idx = build_index()
    print(f"índice: {len(idx)} processos do TCE com dispositivo\n")

    for sigla in args.regioes:
        reg = rc.get(sigla)
        raw_dir = os.path.join(reg.dir, "_curated_data", "raw")
        tot = casado = 0
        for city in reg.ordem:
            path = os.path.join(raw_dir, f"{rc.slugify(city)}.json")
            # Regiões abertas cidade a cidade (amosc, amplanorte, ameosc) só têm
            # o raw das cidades pedidas; as demais ainda não foram extraídas.
            if not os.path.exists(path):
                continue
            data = json.load(open(path))
            for r in data["tce"]:
                tot += 1
                disp = idx.get(norm_ref(r.get("ref", "")))
                if disp:
                    r["dispositivo"] = disp
                    casado += 1
            json.dump(data, open(path, "w"), ensure_ascii=False, indent=1)
        pct = casado * 100 // max(tot, 1)
        print(f"{sigla}: {casado}/{tot} casos do TCE agora têm a decisão ({pct}%)")


if __name__ == "__main__":
    main()
