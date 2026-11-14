#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta lotes de conferência de selo de status.

Só os casos que serão publicados e cujo selo bruto acusa alguém (ACP ajuizada,
multa aplicada, julgado irregular, improbidade, rejeição). Esses são os que, se
o classificador do scrape errou, colocam um selo de culpa sobre uma manchete que
diz que ninguém foi responsabilizado. O caminho inverso (selo brando sobre caso
grave) não é conferido aqui — erra a favor de quem é citado, e a descrição
carrega o desfecho correto de qualquer modo.

Uso: python3 make_status_batches.py amesc amrec --out <dir>
"""
import argparse
import json
import os
import re

import regiao_config as rc

ACUSATORIO = re.compile(
    r"acp ajuizada|acp em curso|a[çc][ãa]o civil|multa aplicada|julgado irregular|"
    r"improbidade|rejei|apontou irregularidade", re.I)


def texto_origem(r):
    """O raw da AMREC tem esquema mais detalhado que o da AMESC (que vem do MD),
    e o TCE não tem 'partes' — junta o que existir, sem assumir formato."""
    campos = ("partes", "objeto", "decisao", "assunto", "unidade_gestora",
              "responsaveis", "ato", "valores", "header")
    return " · ".join(str(r[k]) for k in campos if r.get(k))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("regioes", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--tamanho", type=int, default=45)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    total = 0
    for sigla in args.regioes:
        reg = rc.get(sigla)
        raw_dir = os.path.join(reg.dir, "_curated_data", "raw")
        cur_dir = os.path.join(reg.dir, "_curated_data", "curated")
        pend = []
        for city in reg.ordem:
            slug = rc.slugify(city)
            raw = json.load(open(os.path.join(raw_dir, f"{slug}.json")))
            cur = json.load(open(os.path.join(cur_dir, f"{slug}.json")))
            for tipo in ("mp", "tce"):
                for i, it in enumerate(cur[tipo]):
                    if not it.get("keep") or it.get("status"):
                        continue
                    st = raw[tipo][i]["status"]
                    if not ACUSATORIO.search(st):
                        continue
                    pend.append({
                        "cidade": city, "slug": slug, "tipo": tipo, "i": i,
                        "selo_bruto": st,
                        "titulo_editorial": it.get("title", ""),
                        "descricao_editorial": it.get("description", ""),
                        "texto_origem": texto_origem(raw[tipo][i]),
                    })
        for n, s in enumerate(range(0, len(pend), args.tamanho)):
            path = os.path.join(args.out, f"{sigla}_status__{n}.json")
            json.dump({"regiao": sigla, "casos": pend[s:s + args.tamanho]},
                      open(path, "w"), ensure_ascii=False, indent=1)
            print(f"  {os.path.basename(path)}  n={len(pend[s:s+args.tamanho])}")
        print(f"{sigla}: {len(pend)} casos a conferir")
        total += len(pend)
    print(f"\ntotal: {total}")


if __name__ == "__main__":
    main()
