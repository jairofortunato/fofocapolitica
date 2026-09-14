#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tira o fundo chapado de logos e brasões, deixando o PNG com alfa.

O `logo-branco.png` é a marca sobre um retângulo preto e o `logo-preto.png` é a
mesma marca sobre um retângulo branco. Na capa, que é escura mas não é preta, e
no cabeçalho, que é branco mas tem fio e cor de cidade em volta, esse retângulo
aparece como uma plaquinha em torno da marca. O mesmo vale para o brasão baixado
da Wikipédia quando o arquivo veio achatado em fundo branco.

Não dá para resolver por "toda cor clara vira transparente": o dente e o focinho
da onça do logo são brancos, e o brasão tem branco dentro do escudo. O que
distingue fundo de desenho aqui não é a cor, é estar **ligado à borda** — por
isso a remoção é por preenchimento a partir das bordas, e o branco cercado de
desenho fica.

Idempotente: imagem que já tem borda transparente sai intacta.

Uso:
    python3 despinta_fundo.py assets/logo-preto.png amarp/assets/cidades/videira-e.png
    python3 despinta_fundo.py --checar <arquivos>   # só relata, não grava
"""
from __future__ import annotations

import argparse
import sys
from collections import deque

from PIL import Image

# 70 numa escala de 0-255 por canal: pega a rampa de antisserrilhado em volta da
# letra sem atravessar para o desenho. Abaixo de ~50 sobra um halo cinza; acima
# de ~90 o preto do contorno da onça começa a ser comido pelo fundo preto.
TOL = 70
# Segunda faixa, mais larga: o que está entre TOL e TOL_SUAVE de distância do
# fundo e encosta no que saiu é a rampa de antisserrilhado. Vira alfa parcial em
# vez de opaco, senão fica um contorno duro de 1px com a cor do fundo antigo.
TOL_SUAVE = 150


def _dist(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2]))


def despinta(path, tol=TOL, gravar=True):
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    px = im.load()

    borda = ([(x, 0) for x in range(w)] + [(x, h - 1) for x in range(w)]
             + [(0, y) for y in range(h)] + [(w - 1, y) for y in range(h)])

    # brasão vindo de SVG já chega recortado. Alguns têm um punhado de pixels
    # opacos na borda (um galho do ramo que encosta na moldura), então o teste é
    # de maioria, não de totalidade.
    opacos = [p for p in borda if px[p][3] > 8]
    if len(opacos) < 0.5 * len(borda):
        return "já sem fundo"

    # a cor do fundo é a que domina a borda; usar só o canto (0,0) erra em
    # imagem cujo desenho encosta num canto.
    cont = {}
    for p in opacos:
        r, g, b, _ = px[p]
        cont[(r, g, b)] = cont.get((r, g, b), 0) + 1
    fundo, n = max(cont.items(), key=lambda kv: kv[1])
    if n < 0.5 * len(borda):
        return f"borda sem cor dominante (maior: {fundo} em {n}/{len(borda)}) — nada feito"

    vistos = bytearray(w * h)
    fila = deque()
    for x, y in borda:
        if not vistos[y * w + x] and _dist(px[x, y], fundo) <= tol:
            vistos[y * w + x] = 1
            fila.append((x, y))

    fora = []
    while fila:
        x, y = fila.popleft()
        fora.append((x, y))
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not vistos[ny * w + nx]:
                if _dist(px[nx, ny], fundo) <= tol:
                    vistos[ny * w + nx] = 1
                    fila.append((nx, ny))

    # rampa: vizinho do fundo que ainda puxa para a cor do fundo vira alfa parcial
    rampa = {}
    for x, y in fora:
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not vistos[ny * w + nx]:
                d = _dist(px[nx, ny], fundo)
                if d < TOL_SUAVE:
                    a = round(255 * (d - tol) / (TOL_SUAVE - tol))
                    rampa[(nx, ny)] = min(rampa.get((nx, ny), 255), max(0, a))

    for p in fora:
        px[p] = (0, 0, 0, 0)
    for p, a in rampa.items():
        r, g, b, _ = px[p]
        px[p] = (r, g, b, a)

    if gravar:
        im.save(path, optimize=True)
    pct = 100 * len(fora) / (w * h)
    return f"fundo {fundo} removido — {pct:.0f}% da imagem, {len(rampa)} px de rampa"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivos", nargs="+")
    ap.add_argument("--tol", type=int, default=TOL)
    ap.add_argument("--checar", action="store_true", help="não grava, só relata")
    args = ap.parse_args()
    for f in args.arquivos:
        try:
            print(f"{f}: {despinta(f, args.tol, gravar=not args.checar)}")
        except Exception as e:                       # noqa: BLE001
            print(f"{f}: ERRO {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
