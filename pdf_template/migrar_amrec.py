#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migra a curadoria da AMREC do layout por lote para a convenção por cidade.

A AMREC foi curada numa sessão em que os agentes foram disparados em lotes
ad-hoc (small1_0, icara_mp_1, ...), e `gen_amrec_curated.load_curated_for_city()`
virou um if/elif com esse mapeamento. Aqui esse desembaraço é feito uma vez só e
o resultado gravado em `_curated_data/curated/<slug>.json`, o mesmo formato da
AMESC — daí em diante as duas regiões rodam pelo `gen_dossie.py`.

Cuidado com Criciúma: o curado dela foi feito sobre uma versão anterior do raw
(`criciuma_raw_original.json`, 223 entradas), então o raw migrado precisa ser
essa mesma versão, senão o alinhamento posicional escorrega.
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AMREC = os.path.join(HERE, "amrec")
sys.path.insert(0, AMREC)
os.chdir(AMREC)

import gen_amrec_curated as g  # noqa: E402
from gen_amrec import ORDEM  # noqa: E402

import regiao_config as rc  # noqa: E402

OUT_RAW = os.path.join(AMREC, "_curated_data", "raw")
OUT_CUR = os.path.join(AMREC, "_curated_data", "curated_por_cidade")
os.makedirs(OUT_CUR, exist_ok=True)

erros = []
for city in ORDEM:
    slug = rc.slugify(city)
    raw = g.load_raw(city)              # já aplica o desvio do Criciúma
    mp_cur, tce_cur = g.load_curated_for_city(city)

    if len(raw["mp"]) != len(mp_cur):
        erros.append(f"{city}: MP raw={len(raw['mp'])} curated={len(mp_cur)}")
    if len(raw["tce"]) != len(tce_cur):
        erros.append(f"{city}: TCE raw={len(raw['tce'])} curated={len(tce_cur)}")

    # grava o raw efetivamente usado, para o novo pipeline ficar autossuficiente
    json.dump(raw, open(os.path.join(OUT_RAW, f"{slug}.json"), "w"),
              ensure_ascii=False, indent=1)
    json.dump({"mp": mp_cur, "tce": tce_cur},
              open(os.path.join(OUT_CUR, f"{slug}.json"), "w"),
              ensure_ascii=False, indent=1)
    kept = sum(1 for x in mp_cur + tce_cur if x.get("keep"))
    print(f"{city:22} mp={len(mp_cur):4} tce={len(tce_cur):4} -> {kept:4} publicados")

if erros:
    print("\n=== DESALINHAMENTO ===", file=sys.stderr)
    for e in erros:
        print("  " + e, file=sys.stderr)
    sys.exit(1)

# só troca o diretório de verdade depois que tudo bateu
final = os.path.join(AMREC, "_curated_data", "curated")
shutil.rmtree(final + "_lotes", ignore_errors=True)
os.rename(final, final + "_lotes")
os.rename(OUT_CUR, final)
print("\nmigrado; layout antigo preservado em curated_lotes/")
