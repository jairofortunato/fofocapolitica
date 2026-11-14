#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remonta os lotes curados em um arquivo por cidade, no formato do gerador.

O gerador casa raw e curado **por posição**, então a checagem que importa aqui é
que cada cidade termine com exatamente um item curado por caso bruto, na ordem
certa. Qualquer buraco vira erro em vez de passar batido — um deslocamento de um
índice faria o PDF publicar a descrição de um caso sob o número de processo de
outro.

Uso: python3 assemble_curated.py amesc --lotes <dir_curados>
"""
import argparse
import glob
import json
import os
import sys

import regiao_config as rc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("regiao")
    ap.add_argument("--lotes", required=True)
    args = ap.parse_args()

    reg = rc.get(args.regiao)
    raw_dir = os.path.join(reg.dir, "_curated_data", "raw")
    out_dir = os.path.join(reg.dir, "_curated_data", "curated")
    os.makedirs(out_dir, exist_ok=True)

    erros = []
    for city in reg.ordem:
        slug = rc.slugify(city)
        raw_path = os.path.join(raw_dir, f"{slug}.json")
        # Regiões abertas cidade a cidade só têm o raw das cidades pedidas.
        if not os.path.exists(raw_path):
            continue
        raw = json.load(open(raw_path))

        itens = []
        for path in sorted(glob.glob(os.path.join(args.lotes, f"{slug}__*.json"))):
            itens += json.load(open(path))

        por_tipo = {"mp": {}, "tce": {}}
        for it in itens:
            tipo = it.get("tipo")
            if tipo not in por_tipo:
                erros.append(f"{city}: item com tipo inválido {tipo!r}")
                continue
            if it["i"] in por_tipo[tipo]:
                erros.append(f"{city}: {tipo} índice {it['i']} duplicado")
            por_tipo[tipo][it["i"]] = it

        saida = {}
        for tipo in ("mp", "tce"):
            n = len(raw[tipo])
            faltando = [i for i in range(n) if i not in por_tipo[tipo]]
            if faltando:
                erros.append(f"{city}: {tipo} sem curadoria nos índices {faltando[:10]}"
                             f"{' ...' if len(faltando) > 10 else ''} ({len(faltando)} de {n})")
            extras = [i for i in por_tipo[tipo] if i >= n]
            if extras:
                erros.append(f"{city}: {tipo} tem índices além do raw: {extras[:10]}")
            saida[tipo] = [por_tipo[tipo].get(i, {"keep": False}) for i in range(n)]

        json.dump(saida, open(os.path.join(out_dir, f"{slug}.json"), "w"),
                  ensure_ascii=False, indent=1)
        kept = sum(1 for t in ("mp", "tce") for x in saida[t] if x.get("keep"))
        alta = sum(1 for t in ("mp", "tce") for x in saida[t]
                   if x.get("keep") and x.get("severity") == "alta")
        print(f"{city:28} {len(raw['mp'])+len(raw['tce']):4} brutos -> {kept:4} publicados ({alta} graves)")

    if erros:
        print("\n=== PROBLEMAS ===", file=sys.stderr)
        for e in erros:
            print("  " + e, file=sys.stderr)
        sys.exit(1)
    print("\nalinhamento ok em todas as cidades")


if __name__ == "__main__":
    main()
