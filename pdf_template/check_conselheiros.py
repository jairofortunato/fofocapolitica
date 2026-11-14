#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Trava de segurança: conselheiro do TCE citado como se fosse investigado.

O parser do DOTC-e às vezes joga o relator (ou uma diretoria interna do próprio
tribunal) dentro do campo `responsaveis`. Já apareceu num card publicado dizendo
que Aderson Flores — conselheiro do TCE — fora multado como responsável da
Prefeitura de Lauro Müller: um julgador descrito como condenado pelo próprio
tribunal que preside o julgamento.

Como o nome do conselheiro é legítimo num card quando aparece como relator, o
critério aqui é o texto do card **atribuir conduta** a ele, não a mera citação.

Uso: python3 check_conselheiros.py amesc amrec
"""
import argparse
import json
import os
import re
import sys

import regiao_config as rc

# conselheiros e auditores do TCE/SC — nomes que nunca são "responsáveis" de uma
# prefeitura nos processos que o próprio tribunal julga
CONSELHEIROS = [
    "Aderson Flores", "César Filomeno Fontes", "Wilson Rogério Wan-Dall",
    "José Nei Alberton Ascari", "Adircélio de Moraes Ferreira",
    "Diogo Roberto Ringenberg", "Luiz Eduardo Cherem", "Herneus de Nadal",
    "Gerson dos Santos Sicca", "Sabrina Nunes Iocken", "Cleber Muniz Gavi",
]
# O Ministério Público de Contas NÃO entra aqui: ele é parte legítima e recorrente
# (é quem representa contra as prefeituras). Incluí-lo só gerava falso positivo.
ORGAOS_TCE = ["Diretoria de Contas de Gestão", "Diretoria de Gestão de Pessoas"]

# atribuição de conduta perto do nome: "X é responsável", "multa a X", "contra X"
ATRIBUI = re.compile(r"respons[áa]ve|multa|condena|investigad|apontad|acusad|"
                     r"contra\b|gestor|prefeit", re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("regioes", nargs="+")
    args = ap.parse_args()

    achados = []
    for sigla in args.regioes:
        reg = rc.get(sigla)
        cur_dir = os.path.join(reg.dir, "_curated_data", "curated")
        for city in reg.ordem:
            slug = rc.slugify(city)
            cur_path = os.path.join(cur_dir, f"{slug}.json")
            # Regiões abertas cidade a cidade só têm o curado das pedidas.
            if not os.path.exists(cur_path):
                continue
            data = json.load(open(cur_path))
            for tipo in ("mp", "tce"):
                for i, it in enumerate(data[tipo]):
                    if not it.get("keep"):
                        continue
                    texto = f"{it.get('title','')} {it.get('description','')}"
                    for nome in CONSELHEIROS + ORGAOS_TCE:
                        if nome not in texto:
                            continue
                        # o card que nomeia o papel ("relator", "conselheiro")
                        # está justamente desfazendo a confusão, não cometendo-a
                        if re.search(r"relator|conselheir|procurador", texto, re.I):
                            continue
                        if ATRIBUI.search(texto):
                            achados.append(f"{sigla}/{slug} {tipo}[{i}]: '{nome}' "
                                           f"citado sem papel de relator — {it['title'][:70]}")
    if achados:
        print(f"=== {len(achados)} CARDS CITAM CONSELHEIRO/ÓRGÃO DO TCE COMO PARTE ===",
              file=sys.stderr)
        for a in achados:
            print("  " + a, file=sys.stderr)
        sys.exit(1)
    print("nenhum conselheiro ou órgão do TCE citado como investigado")


if __name__ == "__main__":
    main()
