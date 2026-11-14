#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Baixa bandeira e brasão de cada cidade de uma região, da Wikipédia PT.

Duas regiões seguidas gastaram um agente inteiro redescobrindo as mesmas três
armadilhas, então elas estão resolvidas aqui:

1. `urllib` toma HTTP 429 sistemático de upload.wikimedia.org mesmo com
   User-Agent de navegador; a mesma URL via `curl` com Referer e Accept-Language
   responde 200 na hora. Por isso o fetch é `curl`, não `urllib`.
2. O parâmetro da infobox às vezes vem colado num comentário HTML na mesma linha
   (`<!-- Dados gerais -->| brasão = X.png`), o que escapa de um regex ancorado
   em início de linha. Os comentários são removidos antes da busca.
3. Nem todo arquivo é PNG/JPG: SVG e GIF precisam da renderização `thumburl`, e
   há caso (Benedito Novo) em que a Wikimedia devolve o próprio GIF no thumb —
   aí a conversão tem que ser local, senão o arquivo mente sobre a extensão.

O parâmetro da infobox é a fonte da verdade do nome do arquivo. Nunca filtre por
palavra-chave no nome: isso já perdeu bandeira salva como "Band_x.jpg".

Uso:
    python3 dl_assets.py ammvi            # todas as cidades da região
    python3 dl_assets.py ammvi --só-faltando
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse

import regiao_config as rc

API = "https://pt.wikipedia.org/w/api.php"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
# Accept sem image/webp de propósito: com webp na lista a Wikimedia devolve WebP,
# que o gerador de PDF não renderiza.
HDRS = ["-A", UA,
        "-H", "Accept: image/png,image/jpeg,*/*;q=0.5",
        "-H", "Referer: https://pt.wikipedia.org/",
        "-H", "Accept-Language: pt-BR,pt;q=0.9,en;q=0.8"]
OK_EXT = ("png", "jpg", "jpeg")
MAX_LARGURA = 1000  # bandeira de 8700px vira PDF de 13 MB


def fetch(url, tries=8):
    for i in range(tries):
        tf = tempfile.NamedTemporaryFile(delete=False)
        tf.close()
        r = subprocess.run(["curl", "-sS", "-L", "--max-time", "90",
                            "-o", tf.name, "-w", "%{http_code}"] + HDRS + [url],
                           capture_output=True, text=True)
        code = (r.stdout or "").strip()
        if code == "200":
            data = open(tf.name, "rb").read()
            os.unlink(tf.name)
            return data
        os.unlink(tf.name)
        espera = 4 * (i + 1)
        print(f"    HTTP {code or r.stderr.strip()}, aguardando {espera}s...", flush=True)
        time.sleep(espera)
    raise RuntimeError("falhou: " + url)


def wikitext(title):
    q = {"action": "query", "titles": title, "prop": "revisions",
         "rvprop": "content", "rvslots": "main", "format": "json"}
    pages = json.loads(fetch(API + "?" + urllib.parse.urlencode(q)))["query"]["pages"]
    for pid, p in pages.items():
        if pid == "-1" or "revisions" not in p:
            return None
        return p["revisions"][0]["slots"]["main"]["*"]
    return None


def param(txt, nomes):
    limpo = re.sub(r"<!--.*?-->", "\n", txt, flags=re.S)
    for n in nomes:
        m = re.search(r"\|\s*" + n + r"\s*=\s*([^\n|]+)", limpo)
        if not m:
            continue
        v = m.group(1).strip()
        v = re.sub(r"^\[\[\s*(Ficheiro|Arquivo|File|Image|Imagem)\s*:\s*", "", v, flags=re.I)
        v = v.split("|")[0].replace("]]", "").strip()
        if v:
            return v
    return None


def imageinfo(fname):
    q = {"action": "query", "titles": "Ficheiro:" + fname, "prop": "imageinfo",
         "iiprop": "url", "iiurlwidth": "1000", "format": "json"}
    pages = json.loads(fetch(API + "?" + urllib.parse.urlencode(q)))["query"]["pages"]
    for _, p in pages.items():
        ii = p.get("imageinfo")
        if not ii:
            return None, None
        return ii[0].get("url"), ii[0].get("thumburl")
    return None, None


def normaliza(path):
    """Garante PNG/JPEG real e largura <= MAX_LARGURA.

    O `file` do sistema não basta: já veio GIF salvo sob nome .png, e nesse caso
    o PDF sai sem a imagem sem nenhum erro visível.
    """
    from PIL import Image
    im = Image.open(path)
    fmt, larg = im.format, im.width
    precisa = fmt not in ("PNG", "JPEG") or larg > MAX_LARGURA
    if not precisa:
        return f"{fmt} {im.width}x{im.height}"
    if larg > MAX_LARGURA:
        alt = round(im.height * MAX_LARGURA / larg)
        im = im.resize((MAX_LARGURA, alt), Image.LANCZOS)
    destino = os.path.splitext(path)[0] + ".png"
    im.convert("RGBA").save(destino, optimize=True)
    if destino != path:
        os.remove(path)
    return f"{fmt} {larg}px -> PNG {im.width}x{im.height}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("regiao")
    ap.add_argument("--so-faltando", action="store_true",
                    help="pula cidade que já tem bandeira e brasão no disco")
    ap.add_argument("--cidade", action="append",
                    help="baixa só esta(s) cidade(s) em vez da região inteira")
    args = ap.parse_args()

    reg = rc.get(args.regiao)
    out = os.path.join(reg.dir, "assets", "cidades")
    os.makedirs(out, exist_ok=True)

    # numa região aberta cidade a cidade, varrer as 28 são 56 requisições à
    # Wikipédia para buscar duas imagens.
    alvo = args.cidade or reg.ordem
    desconhecidas = [c for c in alvo if c not in reg.ordem]
    if desconhecidas:
        ap.error(f"fora da ordem de {reg.sigla}: {', '.join(desconhecidas)}")

    lacunas = []
    for cidade in alvo:
        slug = rc.asset_slug(cidade)
        if args.so_faltando and set(reg.imgs(cidade)) == {"bandeira", "brasao"}:
            continue
        print(f"== {cidade}", flush=True)

        txt = None
        for t in (f"{cidade} (Santa Catarina)", cidade):
            txt = wikitext(t)
            if txt and "Santa Catarina" in txt:
                print(f"   página: {t}", flush=True)
                break
            txt = None
        if not txt:
            lacunas.append(f"{cidade}: página não encontrada")
            continue

        # Parte das cidades (Mafra, p. ex.) não tem a infobox no corpo do artigo:
        # o artigo só transclui `{{Info/Município do Brasil/<página>}}`, e os
        # parâmetros ficam na subpágina de predefinição. Sem seguir a
        # transclusão, o `param()` não acha nada e a cidade vira lacuna — mesmo
        # com bandeira e brasão publicados na Wikipédia.
        sub = re.search(r"\{\{\s*Info/Munic[íi]pio do Brasil/([^}|\n]+)\}\}", txt)
        if sub and not param(txt, ["bandeira"]):
            tmpl = wikitext("Predefinição:Info/Município do Brasil/" + sub.group(1).strip())
            if tmpl:
                print(f"   infobox transcluída: {sub.group(1).strip()}", flush=True)
                txt = tmpl

        for kind, chaves in (("b", ["bandeira"]), ("e", [r"bras[ãa]o"])):
            fname = param(txt, chaves)
            if not fname:
                lacunas.append(f"{cidade}: sem {'bandeira' if kind == 'b' else 'brasão'} na infobox")
                continue
            url, thumb = imageinfo(fname)
            if not url:
                lacunas.append(f"{cidade}: ficheiro {fname} não resolvido")
                continue
            ext = os.path.splitext(url)[1].lower().lstrip(".")
            if ext not in OK_EXT:
                if not thumb:
                    lacunas.append(f"{cidade}: sem thumb para {fname}")
                    continue
                url = thumb
                ext = os.path.splitext(url)[1].lower().lstrip(".") or "png"
                if ext not in OK_EXT:
                    ext = "png"
            dest = os.path.join(out, f"{slug}-{kind}.{ext}")
            open(dest, "wb").write(fetch(url))
            print(f"   {kind}: {fname} -> {normaliza(dest)}", flush=True)
            time.sleep(0.4)
        time.sleep(0.4)

    faltando = [c for c in alvo if set(reg.imgs(c)) != {"bandeira", "brasao"}]
    print(f"\n{len(alvo) - len(faltando)}/{len(alvo)} cidades com bandeira e brasão")
    for l in lacunas:
        print("  lacuna:", l)
    if faltando:
        print("  sem par completo no disco:", ", ".join(faltando))
        sys.exit(1)


if __name__ == "__main__":
    main()
