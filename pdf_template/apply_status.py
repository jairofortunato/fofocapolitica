#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aplica os selos conferidos de volta nos arquivos de curadoria.

Grava `status` em cada caso curado. O gerador prefere esse campo ao status do
bruto (ver `build_cards` em gen_dossie.py), então a partir daqui o selo do card
passa a vir da leitura editorial e não do classificador por palavra-chave.

Uso: python3 apply_status.py amesc amrec --conferidos <dir>
"""
import argparse
import glob
import json
import os
import sys

import regiao_config as rc

# vocabulário permitido — evita que um selo inventado entre silenciosamente e
# caia no `pill_cls` como classe "neutral" sem ninguém perceber
SELOS = {
    "🟡 em apuração", "🟢 arquivado", "🟢 recomendação cumprida", "🟠 TAC firmado",
    "🟠 ACNP firmado", "🔴 ACP ajuizada", "⚫ prescrito", "❔ status indef.",
    "⬛ julgado irregular", "⬛ julgado irregular + multa", "🔴 multa aplicada",
    "🔴 apontou irregularidade", "🔴 parecer pela rejeição", "🟢 julgado regular",
    "🟢 parecer pela aprovação", "🟠 cautelar / sustação",
    "🟡 em instrução (citação/audiência)", "❔ em tramitação",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("regioes", nargs="+")
    ap.add_argument("--conferidos", required=True)
    args = ap.parse_args()

    erros = []
    for sigla in args.regioes:
        reg = rc.get(sigla)
        cur_dir = os.path.join(reg.dir, "_curated_data", "curated")

        correcoes = []
        for f in sorted(glob.glob(os.path.join(args.conferidos, f"{sigla}_status__*.json"))):
            correcoes += json.load(open(f))

        por_cidade = {}
        for c in correcoes:
            if c["status"] not in SELOS:
                erros.append(f"{sigla}/{c['slug']}[{c['i']}]: selo fora do vocabulário: {c['status']!r}")
                continue
            por_cidade.setdefault(c["slug"], []).append(c)

        mudados = aplicados = 0
        for slug, itens in por_cidade.items():
            path = os.path.join(cur_dir, f"{slug}.json")
            data = json.load(open(path))
            for c in itens:
                alvo = data[c["tipo"]][c["i"]]
                if not alvo.get("keep"):
                    erros.append(f"{sigla}/{slug}[{c['i']}]: correção em caso não publicado")
                    continue
                alvo["status"] = c["status"]
                aplicados += 1
                if c.get("mudou"):
                    mudados += 1
            json.dump(data, open(path, "w"), ensure_ascii=False, indent=1)
        print(f"{sigla}: {aplicados} selos aplicados · {mudados} corrigidos")

    if erros:
        print("\n=== PROBLEMAS ===", file=sys.stderr)
        for e in erros:
            print("  " + e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
