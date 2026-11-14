#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aplica os cards do TCE reescritos de volta na curadoria.

Além de gravar, faz a checagem que motivou a reescrita: nenhum card do TCE pode
sair afirmando multa/condenação/rejeição sem que o extrato de origem contenha o
dispositivo. Se um card reescrito ainda afirmar, isso falha aqui em vez de virar
manchete.

Uso: python3 apply_tce.py amesc amrec --reescritos <dir>
"""
import argparse
import glob
import json
import os
import re
import sys

import regiao_config as rc

AFIRMA = re.compile(r"\bmultou?\b|\bmulta\b|julg\w* irregular|rejeit|reprov|condena|"
                    r"puni|aplicou multa", re.I)
TEM_DISPOSITIVO = re.compile(r"julgar irregular|julgou irregular|aplicar multa|"
                             r"aplicada multa|multa no valor|condenar|imputar d[ée]bito|"
                             r"parecer pr[ée]vio pela", re.I)

# selos que afirmam mérito — só podem sobreviver se a origem trouxer o dispositivo
MERITO = {
    "⬛ julgado irregular", "⬛ julgado irregular + multa", "🔴 multa aplicada",
    "🔴 apontou irregularidade", "🔴 parecer pela rejeição", "🟢 julgado regular",
    "🟢 parecer pela aprovação", "🟠 cautelar / sustação",
}

# um card que declara explicitamente não saber o desfecho não está afirmando
# nada — é justamente a redação que queremos. Sem esta exceção a trava barra o
# texto correto ("o extrato não informa o teor do parecer") por conter a palavra
# "rejeitar" na explicação de como o processo funciona.
NEGA_DESFECHO = re.compile(
    r"n[ãa]o informa|n[ãa]o consta|n[ãa]o aparece|n[ãa]o traz|teor n[ãa]o|"
    r"n[ãa]o é poss[íi]vel|desfecho n[ãa]o|sem informar|n[ãa]o divulga|"
    r"n[ãa]o de processo por irregularidade", re.I)

normalizados = [0]


def origem(r):
    return " ".join(str(r[k]) for k in
                    ("assunto", "unidade_gestora", "responsaveis", "ato", "valores",
                     "header", "partes") if r.get(k))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("regioes", nargs="+")
    ap.add_argument("--reescritos", required=True)
    args = ap.parse_args()

    erros = []
    for sigla in args.regioes:
        reg = rc.get(sigla)
        raw_dir = os.path.join(reg.dir, "_curated_data", "raw")
        cur_dir = os.path.join(reg.dir, "_curated_data", "curated")

        novos = []
        for f in sorted(glob.glob(os.path.join(args.reescritos, f"{sigla}_tce__*.json"))):
            novos += json.load(open(f))

        por_cidade = {}
        for c in novos:
            por_cidade.setdefault(c["slug"], []).append(c)

        aplicados = 0
        for slug, itens in por_cidade.items():
            cur_path = os.path.join(cur_dir, f"{slug}.json")
            raw = json.load(open(os.path.join(raw_dir, f"{slug}.json")))
            data = json.load(open(cur_path))
            for c in itens:
                texto = c["title"] + " " + c["description"]
                if (AFIRMA.search(texto) and not NEGA_DESFECHO.search(texto)
                        and not TEM_DISPOSITIVO.search(origem(raw["tce"][c["i"]]))):
                    erros.append(f"{sigla}/{slug} tce[{c['i']}]: ainda afirma desfecho "
                                 f"sem dispositivo na origem — {c['title'][:70]}")
                    continue
                data["tce"][c["i"]]["title"] = c["title"]
                data["tce"][c["i"]]["description"] = c["description"]
                aplicados += 1

            # o mesmo critério vale para o selo, e não só para os acusatórios que
            # foram conferidos um a um: um card do TCE cujo extrato não traz o
            # dispositivo não pode ostentar selo de mérito nenhum — nem de
            # condenação, nem de aprovação de contas. Vira "em tramitação".
            for i, it in enumerate(data["tce"]):
                if not it.get("keep"):
                    continue
                selo = it.get("status", "")
                if selo in MERITO and not TEM_DISPOSITIVO.search(origem(raw["tce"][i])):
                    it["status"] = "❔ em tramitação"
                    normalizados[0] += 1
            json.dump(data, open(cur_path, "w"), ensure_ascii=False, indent=1)
        print(f"{sigla}: {aplicados} cards do TCE reescritos · "
              f"{normalizados[0]} selos de mérito rebaixados a 'em tramitação'")
        normalizados[0] = 0

    if erros:
        print(f"\n=== {len(erros)} CARDS AINDA AFIRMAM DESFECHO SEM FONTE ===", file=sys.stderr)
        for e in erros:
            print("  " + e, file=sys.stderr)
        sys.exit(1)
    print("nenhum card do TCE afirma desfecho sem respaldo na origem")


if __name__ == "__main__":
    main()
