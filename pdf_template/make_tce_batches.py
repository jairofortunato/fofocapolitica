#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta lotes de reescrita dos cards do TCE que afirmam desfecho sem fonte.

Os extratos do DOTC-e capturados pelo scrape trazem o objeto do processo, os
responsáveis e o número do acórdão — mas não o dispositivo da decisão. A
curadoria leu esse extrato e, influenciada pelo selo do classificador, escreveu
manchetes do tipo "TCE aplica multa a X" que a fonte não sustenta. Aqui saem os
cards a reescrever.

Uso: python3 make_tce_batches.py amesc amrec --out <dir>
"""
import argparse
import json
import os
import re

import regiao_config as rc

AFIRMA = re.compile(r"multa|julg\w* irregular|rejeit|reprov|condena|aplicou|"
                    r"manteve a condena|irregularidade\s+(?:foi|ficou)", re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("regioes", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--tamanho", type=int, default=30)
    ap.add_argument("--todos", action="store_true",
                    help="inclui todo card publicado do TCE, não só os que afirmam desfecho")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    for sigla in args.regioes:
        reg = rc.get(sigla)
        raw_dir = os.path.join(reg.dir, "_curated_data", "raw")
        cur_dir = os.path.join(reg.dir, "_curated_data", "curated")
        pend = []
        for city in reg.ordem:
            slug = rc.slugify(city)
            raw = json.load(open(os.path.join(raw_dir, f"{slug}.json")))
            cur = json.load(open(os.path.join(cur_dir, f"{slug}.json")))
            for i, it in enumerate(cur["tce"]):
                if not it.get("keep"):
                    continue
                if not args.todos and not AFIRMA.search(
                        it.get("title", "") + " " + it.get("description", "")):
                    continue
                r = raw["tce"][i]
                pend.append({
                    "cidade": city, "slug": slug, "i": i,
                    "processo": r.get("ref", ""),
                    "status_atual": it.get("status", r.get("status", "")),
                    "titulo_atual": it.get("title", ""),
                    "descricao_atual": it.get("description", ""),
                    "texto_origem": {k: r[k] for k in
                                     ("assunto", "unidade_gestora", "responsaveis",
                                      "ato", "valores", "relator", "header", "partes")
                                     if r.get(k)},
                    # o que o tribunal decidiu, recuperado no re-scrape; ausente
                    # quando o diário não publicou o dispositivo desse processo
                    "decisao": r.get("dispositivo"),
                })
        for n, s in enumerate(range(0, len(pend), args.tamanho)):
            path = os.path.join(args.out, f"{sigla}_tce__{n}.json")
            json.dump({"regiao": sigla, "casos": pend[s:s + args.tamanho]},
                      open(path, "w"), ensure_ascii=False, indent=1)
            print(f"  {os.path.basename(path)}  n={len(pend[s:s+args.tamanho])}")
        print(f"{sigla}: {len(pend)} cards a reescrever")


if __name__ == "__main__":
    main()
