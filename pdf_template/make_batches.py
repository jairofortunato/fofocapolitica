#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quebra os casos brutos de uma região em lotes para a revisão editorial.

Cada lote vira um arquivo JSON que um agente Claude lê e devolve curado. O campo
`i` é o índice do caso dentro da lista (mp ou tce) da sua cidade e é o que
permite remontar na ordem certa depois — o gerador casa raw e curado por
posição.

Uso: python3 make_batches.py amesc --out <dir> [--tamanho 120]
"""
import argparse
import json
import os

import regiao_config as rc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("regiao")
    ap.add_argument("--out", required=True)
    ap.add_argument("--tamanho", type=int, default=120)
    args = ap.parse_args()

    reg = rc.get(args.regiao)
    os.makedirs(args.out, exist_ok=True)
    raw_dir = os.path.join(reg.dir, "_curated_data", "raw")

    manifest = []
    for city in reg.ordem:
        slug = rc.slugify(city)
        raw_path = os.path.join(raw_dir, f"{slug}.json")
        # Regiões abertas cidade a cidade: só lotea o que foi extraído.
        if not os.path.exists(raw_path):
            continue
        raw = json.load(open(raw_path))
        casos = []
        for tipo in ("mp", "tce"):
            for i, r in enumerate(raw[tipo]):
                y, m, d = r["ymd"]
                caso = {
                    "i": i, "tipo": tipo, "ref": r["ref"],
                    "header": r["header"], "status": r["status"],
                    "data": f"{d:02d}/{m:02d}/{y}" if y else "",
                    "texto": r["partes"],
                }
                # O que o tribunal decidiu, quando o re-scrape recuperou.
                # Sem este campo o agente cura o TCE às cegas: o `texto` traz só
                # o objeto do processo, e o desfecho acaba saindo por inferência
                # — que foi a origem de 287 cards afirmando condenação sem fonte.
                if r.get("dispositivo"):
                    caso["decisao"] = r["dispositivo"]
                casos.append(caso)
        for n, start in enumerate(range(0, len(casos), args.tamanho)):
            chunk = casos[start:start + args.tamanho]
            path = os.path.join(args.out, f"{slug}__{n}.json")
            json.dump({"cidade": city, "casos": chunk}, open(path, "w"),
                      ensure_ascii=False, indent=1)
            manifest.append({"cidade": city, "slug": slug, "lote": n,
                             "arquivo": path, "n": len(chunk)})

    json.dump(manifest, open(os.path.join(args.out, "_manifest.json"), "w"),
              ensure_ascii=False, indent=1)
    print(f"{len(manifest)} lotes · {sum(m['n'] for m in manifest)} casos")
    for m in manifest:
        print(f"  {m['cidade']:28} lote {m['lote']}  n={m['n']:4}")


if __name__ == "__main__":
    main()
