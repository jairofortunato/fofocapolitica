#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aplica a recuração do TCE (título, descrição, gravidade e selo).

Diferente do `apply_tce.py`, que só sabia rebaixar cards sem fonte, aqui o card
vem da leitura do dispositivo — então pode voltar a afirmar multa e condenação,
desde que a decisão diga isso. A trava correspondente é a do vocabulário de
selos: um selo inventado falharia silenciosamente como pílula sem estilo.

Uso: python3 apply_tce2.py amesc amrec --recurados <dir>
"""
import argparse
import glob
import json
import os
import sys

import regiao_config as rc
from apply_status import SELOS

# selo do MP aceito em card do TCE: a coluna do TCE não tem equivalente para
# "encerrado sem responsabilizar ninguém" nem para prescrição, e dois agentes
# esbarraram nisso de forma independente. Rebaixar esses casos a "em tramitação"
# esconderia justamente a absolvição, que é a informação que protege o citado.
SELOS_OK = SELOS | {"🟢 arquivado", "⚫ prescrito", "🟢 recomendação cumprida"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("regioes", nargs="+")
    ap.add_argument("--recurados", required=True)
    args = ap.parse_args()

    erros = []
    for sigla in args.regioes:
        reg = rc.get(sigla)
        cur_dir = os.path.join(reg.dir, "_curated_data", "curated")

        novos = []
        for f in sorted(glob.glob(os.path.join(args.recurados, f"{sigla}_tce__*.json"))):
            try:
                novos += json.load(open(f))
            except Exception as e:
                erros.append(f"{os.path.basename(f)}: ilegível ({e})")

        por_cidade = {}
        for c in novos:
            por_cidade.setdefault(c["slug"], []).append(c)

        aplicados = 0
        for slug, itens in por_cidade.items():
            path = os.path.join(cur_dir, f"{slug}.json")
            if not os.path.exists(path):
                erros.append(f"{sigla}/{slug}: curadoria inexistente")
                continue
            data = json.load(open(path))
            for c in itens:
                if c.get("status") and c["status"] not in SELOS_OK:
                    erros.append(f"{sigla}/{slug}[{c['i']}]: selo fora do vocabulário: {c['status']!r}")
                    continue
                alvo = data["tce"][c["i"]]
                if not alvo.get("keep"):
                    continue
                alvo["title"] = c["title"]
                alvo["description"] = c["description"]
                if c.get("severity"):
                    alvo["severity"] = c["severity"]
                if c.get("status"):
                    alvo["status"] = c["status"]
                aplicados += 1
            json.dump(data, open(path, "w"), ensure_ascii=False, indent=1)
        print(f"{sigla}: {aplicados} cards do TCE recurados")

    if erros:
        print("\n=== PROBLEMAS ===", file=sys.stderr)
        for e in erros:
            print("  " + e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
