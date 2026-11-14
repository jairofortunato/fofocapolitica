#!/usr/bin/env python3
"""Compara saídas de teste com o padrão-ouro do rodeio__0."""
import json, glob, os, re
D = os.path.dirname(os.path.abspath(__file__))
gold = json.load(open(f'{D}/gold_rodeio__0.json'))
bruto = json.load(open(f'{D}/../_lotes/rodeio__0.json'))['casos']
txt = open(f'{D}/../../CURADORIA.md').read()
SELOS = {m.group(1).strip() for m in re.finditer(r'`([^`]{3,60})`', txt)
         if any(m.group(1).lstrip().startswith(e) for e in '🟡🟢🟠🔴⚫❔⬛')}
gk = {c['i'] for c in gold if c.get('keep')}
print(f"padrão-ouro: {len(gold)} casos, {len(gk)} publicados\n")
print(f"{'modelo':34} {'align':>6} {'selos':>6} {'iguais':>7} {'falsos+':>8} {'falsos-':>8}")
for p in sorted(glob.glob(f'{D}/teste_*.json')):
    nome = os.path.basename(p)[6:-5]
    try: c = json.load(open(p))
    except Exception: print(f'{nome:34}  JSON INVÁLIDO'); continue
    align = len(c) == len(bruto) and all(x['i'] == y.get('i') and x['tipo'] == y.get('tipo')
                                         for x, y in zip(bruto, c))
    if not align: print(f'{nome:34} {"QUEBRADO":>6}'); continue
    bad = sum(1 for y in c if y.get('keep') and y.get('status') not in SELOS)
    k = {y['i'] for y in c if y.get('keep')}
    print(f'{nome:34} {"ok":>6} {bad:6} {len(k & gk):7} {len(k - gk):8} {len(gk - k):8}')
print("\nfalsos+ = publicou o que o ouro cortou (risco de publicar sem fonte)")
print("falsos- = cortou o que o ouro publicou (perda de conteúdo)")
