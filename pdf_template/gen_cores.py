#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deriva a cor de destaque de cada cidade a partir da sua bandeira.

A cor entra no PDF como a régua lateral dos casos e a linha do cabeçalho, então
precisa ser escura o bastante para o texto branco/preto em cima continuar
legível — por isso a saturação/luminosidade são corrigidas, em vez de usar o
pixel dominante cru (bandeiras têm muito branco e amarelo claro).

Uso: python3 gen_cores.py amesc
"""
import argparse
import colorsys
import json
import os
from collections import Counter

from PIL import Image

import regiao_config as rc


def dominant(path):
    im = Image.open(path).convert("RGB").resize((80, 80))
    counts = Counter()
    for px in im.getdata():
        r, g, b = px
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        # ignora branco, preto e cinza — não servem como cor de identidade
        if s < 0.25 or l > 0.88 or l < 0.08:
            continue
        counts[(round(r / 24) * 24, round(g / 24) * 24, round(b / 24) * 24)] += 1
    if not counts:
        return "#C4161C"
    r, g, b = counts.most_common(1)[0][0]
    h, l, s = colorsys.rgb_to_hls(min(r, 255) / 255, min(g, 255) / 255, min(b, 255) / 255)
    s = max(s, 0.55)
    # A cor também é usada como TEXTO sobre fundo branco (linha do cabeçalho),
    # então o critério é contraste percebido, não lightness do HLS: amarelo com
    # l=0.45 passa no HLS e mesmo assim some no branco. Escurece até atingir a
    # razão de contraste mínima do WCAG para texto pequeno (4.5:1).
    for _ in range(40):
        rr, gg, bb = colorsys.hls_to_rgb(h, l, s)
        if contrast_on_white(rr, gg, bb) >= 4.5:
            break
        l -= 0.02
    return "#%02X%02X%02X" % (int(rr * 255), int(gg * 255), int(bb * 255))


def contrast_on_white(r, g, b):
    """Razão de contraste WCAG contra branco."""
    def lin(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    lum = 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
    return 1.05 / (lum + 0.05)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("regiao")
    args = ap.parse_args()
    reg = rc.get(args.regiao)

    cores = {}
    for city in reg.ordem:
        flag = reg.imgs(city).get("bandeira")
        if not flag:
            print(f"  [AVISO] {city}: sem bandeira, usando cor padrão")
            cores[city] = "#C4161C"
            continue
        cores[city] = dominant(os.path.join(reg.dir, flag.lstrip("./")))
        print(f"{city:28} {cores[city]}")

    out = os.path.join(reg.dir, "cores.json")
    json.dump(cores, open(out, "w"), ensure_ascii=False, indent=1)
    print(f"\n-> {out}")


if __name__ == "__main__":
    main()
