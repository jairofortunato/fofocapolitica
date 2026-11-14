#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Semeia o arquivo de curadoria de uma cidade a partir do raw.

Por que semear em vez de curar tudo de uma vez: o dossiê publicado é o de casos
graves, e **nada entra nele sem revisão editorial contra o texto da decisão**.
A semeadura resolve o resto do arquivo — os casos que existem, contam para o
denominador ("de N levantados") e nunca são renderizados.

Regras da semeadura, todas conservadoras:

  * `severity` sai sempre "media". Grave é decisão editorial e só é atribuída na
    revisão, lendo o dispositivo. Assim o PDF de graves nunca mostra um card que
    ninguém leu.
  * `title` e `description` saem do **objeto do processo** transcrito da fonte
    (Assunto no TCE, Objeto/Partes no MP), nunca do dispositivo. Descrever o
    objeto é reproduzir o que a fonte diz que se apura; descrever o desfecho sem
    ler o dispositivo é inventar condenação — o erro que este pipeline já
    cometeu 287 vezes.
  * `status` fica vazio, para o gerador usar o selo do raw.

Uso:
    python3 seed_curated.py amurc --cidade Curitibanos
"""
from __future__ import annotations

import argparse
import json
import os
import re

import regiao_config as rc


def limpa(t: str) -> str:
    t = re.sub(r"\s+", " ", (t or "")).strip()
    return re.sub(r"\s*\|\s*", " · ", t)


def frase(t: str, limite=150) -> str:
    """Corta no fim de frase antes do limite; não deixa reticências no meio de
    uma palavra nem promete mais texto do que existe."""
    t = limpa(t)
    if len(t) <= limite:
        return t
    corte = t[:limite]
    ponto = max(corte.rfind(". "), corte.rfind("; "))
    if ponto > limite * 0.5:
        return corte[:ponto + 1]
    return corte[:corte.rfind(" ")] + "…"


def titulo_de(rec, city, tipo):
    """Título descritivo do OBJETO, sem afirmar desfecho."""
    base = rec.get("assunto") or rec.get("objeto") or ""
    if not base:
        # sem objeto no MD, o header traz o tipo de processo
        h = re.sub(r"^[⭐•·]\s*", "", rec.get("header", ""))
        h = re.sub(r"^\S+\s+—\s*", "", h).strip()
        base = h or "Processo sem objeto descrito na fonte"
    orgao = "TCE" if tipo == "tce" else "MP"
    return frase(f"{orgao} · {base}", 120)


def descricao_de(rec, city, tipo):
    partes = []
    if rec.get("unidade"):
        partes.append(f"Unidade: {limpa(rec['unidade'])}.")
    obj = rec.get("assunto") or rec.get("objeto")
    if obj:
        partes.append(f"Objeto do processo, conforme a fonte: {frase(obj, 320)}")
    resp = rec.get("responsaveis") or rec.get("partes_nomes")
    if resp:
        partes.append(f"Partes/responsáveis citados: {frase(resp, 160)}")
    if rec.get("sem_decisao"):
        partes.append("A fonte não traz o texto da decisão para esta edição; "
                      "não há desfecho a afirmar aqui.")
    return " ".join(partes) or "Registro sem detalhamento na fonte."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("regiao")
    ap.add_argument("--cidade", required=True)
    ap.add_argument("--forcar", action="store_true",
                    help="sobrescreve a curadoria existente (perde a revisão editorial)")
    args = ap.parse_args()

    reg = rc.get(args.regiao)
    slug = rc.slugify(args.cidade)
    raw = json.load(open(os.path.join(reg.dir, "_curated_data", "raw", f"{slug}.json")))
    dest = os.path.join(reg.dir, "_curated_data", "curated", f"{slug}.json")
    if os.path.exists(dest) and not args.forcar:
        raise SystemExit(f"já existe: {dest} (use --forcar para sobrescrever)")

    out = {}
    for tipo in ("mp", "tce"):
        out[tipo] = [{
            "keep": True,
            "title": titulo_de(r, args.cidade, tipo),
            "description": descricao_de(r, args.cidade, tipo),
            "severity": "media",
            "status": "",
            "_revisado": False,
        } for r in raw[tipo]]

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    json.dump(out, open(dest, "w"), ensure_ascii=False, indent=1)
    print(f"{args.cidade}: semeados mp={len(out['mp'])} tce={len(out['tce'])} -> {dest}")
    print("  todos como severity=media e _revisado=false; "
          "a revisão editorial é que promove a grave.")


if __name__ == "__main__":
    main()
