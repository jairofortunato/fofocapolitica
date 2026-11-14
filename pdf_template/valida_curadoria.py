#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Trava mecânica sobre a curadoria, antes de remontar e gerar PDF.

Três modelos diferentes (Kimi K3, gpt-5.4-mini, gpt-5.4-nano) publicaram card do
TCE afirmando "parecer pela aprovação" em processo cujo dispositivo não foi
capturado — ou seja, o selo saiu do rótulo bruto, que vem de um classificador por
palavra-chave e erra. Um deles chegou a escrever "não houve ressalva sancionatória
no trecho exibido", admitindo que inferia de texto parcial. Instrução no prompt
não resolveu em nenhum dos três, então a regra passa a ser verificada aqui.

Isto NÃO julga conteúdo — só recusa afirmação sem fonte e desalinhamento, que são
verificáveis mecanicamente.

Uso:
    python3 valida_curadoria.py amunesc              # só reporta, sai != 0 se houver erro
    python3 valida_curadoria.py amunesc --corrigir   # corta os cards sem fonte
"""
import argparse
import glob
import json
import os
import re
import sys

import regiao_config as rc

HERE = os.path.dirname(os.path.abspath(__file__))


def selos_validos():
    txt = open(os.path.join(HERE, "CURADORIA.md")).read()
    return {m.group(1).strip() for m in re.finditer(r"`([^`]{3,60})`", txt)
            if any(m.group(1).lstrip().startswith(e) for e in "🟡🟢🟠🔴⚫❔⬛")}


def num_processo(ref):
    """'PAP 22/80059813' e 'REP 22/80059813' são fases do MESMO processo."""
    m = re.search(r"(\d{2}/\d+)", ref or "")
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("regiao")
    ap.add_argument("--corrigir", action="store_true",
                    help="aplica keep=false nos cards sem fonte (não mexe em duplicata)")
    args = ap.parse_args()

    reg = rc.get(args.regiao)
    selos = selos_validos()
    lotes_dir = os.path.join(reg.dir, "_lotes")
    cur_dir = os.path.join(reg.dir, "_lotes_curados")

    erros, avisos, cortados = [], [], 0
    vistos = {}  # (cidade, numero) -> ref já publicado

    for p in sorted(glob.glob(os.path.join(lotes_dir, "*__*.json"))):
        nome = os.path.basename(p)
        alvo = os.path.join(cur_dir, nome)
        if not os.path.exists(alvo):
            avisos.append(f"{nome}: sem curadoria ainda")
            continue
        bruto = json.load(open(p))["casos"]
        cidade = nome.split("__")[0]
        try:
            cur = json.load(open(alvo))
        except Exception as e:
            erros.append(f"{nome}: JSON inválido ({e})")
            continue

        if len(cur) != len(bruto):
            erros.append(f"{nome}: tamanho {len(cur)} != {len(bruto)} do bruto")
            continue
        mudou = False
        # `tipo` omitido pelo modelo é recuperável quando todo `i` casa por posição:
        # o campo é cópia do bruto, não julgamento. Sem essa distinção, um lote
        # inteiro válido seria descartado e recurado à toa.
        if all(b["i"] == c.get("i") for b, c in zip(bruto, cur)) and \
                any(c.get("tipo") is None for c in cur):
            faltando = sum(1 for c in cur if c.get("tipo") is None)
            if args.corrigir:
                for b, c in zip(bruto, cur):
                    if c.get("tipo") is None:
                        c["tipo"] = b["tipo"]
                mudou = True
                print(f"{nome}: campo 'tipo' preenchido a partir do bruto em {faltando} itens")
            else:
                erros.append(f"{nome}: {faltando} itens sem o campo 'tipo' "
                             f"(recuperável com --corrigir)")

        if any(b["i"] != c.get("i") or b["tipo"] != c.get("tipo")
               for b, c in zip(bruto, cur)):
            erros.append(f"{nome}: DESALINHADO — curadoria não casa posicionalmente")
            continue
        for b, c in zip(bruto, cur):
            if not c.get("keep"):
                continue
            if c.get("status") not in selos:
                # emoji trocado num selo cujo texto existe na tabela ("🟢 TAC firmado"
                # em vez de "🟠 TAC firmado"): a cor da pílula sai do emoji, então o
                # card renderiza verde num acordo que é laranja. Texto casa -> corrige.
                texto = re.sub(r"^\W+\s*", "", c.get("status") or "").strip()
                igual = [s for s in selos if re.sub(r"^\W+\s*", "", s).strip() == texto]
                if len(igual) == 1 and args.corrigir:
                    print(f"{nome} i={b['i']}: selo {c['status']!r} -> {igual[0]!r}")
                    c["status"] = igual[0]
                    mudou = True
                else:
                    erros.append(f"{nome} i={b['i']}: selo fora da tabela: {c.get('status')!r}")
            if b["tipo"] == "tce" and not str(b.get("decisao", "")).strip():
                if args.corrigir:
                    c.update(keep=False, title="", description="", status="",
                             severity="media")
                    cortados += 1
                    mudou = True
                else:
                    erros.append(f"{nome} i={b['i']} {b.get('ref')}: "
                                 f"card do TCE sem dispositivo afirmando {c.get('status')!r}")
            n = num_processo(b.get("ref"))
            if n and c.get("keep"):
                chave = (cidade, n)
                if chave in vistos:
                    avisos.append(f"{nome} i={b['i']} {b.get('ref')}: mesmo processo "
                                  f"já publicado como {vistos[chave]} — provável fase repetida")
                else:
                    vistos[chave] = b.get("ref")
        if mudou:
            json.dump(cur, open(alvo, "w"), ensure_ascii=False, indent=1)

    if cortados:
        print(f"corrigidos: {cortados} cards do TCE sem dispositivo viraram keep=false\n")
    for a in avisos:
        print("aviso:", a)
    if erros:
        print("\n=== ERROS ===", file=sys.stderr)
        for e in erros:
            print("  " + e, file=sys.stderr)
        sys.exit(1)
    print("\ncuradoria válida: alinhamento, selos e fonte conferidos")


if __name__ == "__main__":
    main()
