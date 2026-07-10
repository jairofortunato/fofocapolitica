#!/usr/bin/env python3
"""Gera um arquivo Markdown por edição com os blocos parseados."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def short(txt: str | None, limit: int = 600) -> str:
    if not txt:
        return ""
    txt = re.sub(r"\s+", " ", txt).strip()
    if len(txt) > limit:
        txt = txt[: limit - 1] + "…"
    return txt


def block_md(b: dict, idx: int) -> str:
    header = b.get("header", "EXTRATO")
    score = b.get("score_politico", 0)
    star = "⭐" if score >= 10 else ("•" if score >= 6 else "·")
    lines = [f"### {star} {idx}. {header}"]
    info = []
    if b.get("comarca"):
        info.append(f"**Comarca:** {b['comarca']}")
    if b.get("orgao"):
        info.append(f"**Órgão:** {b['orgao']}")
    if b.get("membro"):
        info.append(f"**Promotor:** {b['membro']}")
    if b.get("data"):
        info.append(f"**Data:** {b['data']}")
    if info:
        lines.append(" · ".join(info))
        lines.append("")
    partes = b.get("partes") or b.get("parte") or b.get("investigados")
    if partes:
        lines.append(f"**Partes:** {short(partes, 400)}")
    if b.get("objeto"):
        lines.append(f"**Objeto:** {short(b['objeto'], 900)}")
    if b.get("decisao"):
        lines.append(f"**Decisão:** {short(b['decisao'], 900)}")
    if b.get("keywords"):
        lines.append(f"_palavras-chave: {', '.join(b['keywords'])} · score {score}_")
    lines.append("")
    return "\n".join(lines)


def build(json_path: Path, out_dir: Path):
    data = json.loads(json_path.read_text())
    arquivo = data["arquivo"]
    edicao = arquivo.replace("do_mpsc_", "").replace(".txt", "")
    blocks = data["blocos"]
    blocks.sort(key=lambda x: (-x.get("score_politico", 0), x.get("comarca", "")))

    out_lines = [
        f"# Diário Oficial MPSC — {edicao}",
        "",
        f"Arquivo de origem: `pdfs/{arquivo.replace('.txt', '.pdf')}`  ",
        f"Total de procedimentos cíveis/administrativos relevantes: **{len(blocks)}**",
        "",
        "> ⭐ = score político ≥ 10 · • = score 6-9 · · = score < 6  ",
        "> Score baseado em palavras-chave (improbidade, fraude, prefeitura, "
        "licitação, ambiental, prefeito etc.).",
        "",
        "---",
        "",
    ]
    for i, b in enumerate(blocks, 1):
        out_lines.append(block_md(b, i))
        out_lines.append("---")
        out_lines.append("")

    out_path = out_dir / f"{edicao}.md"
    out_path.write_text("\n".join(out_lines))
    return out_path, len(blocks), sum(1 for b in blocks if b.get("score_politico", 0) >= 10)


def main():
    if len(sys.argv) < 3:
        print("uso: build_markdown.py <parsed-dir> <out-dir>", file=sys.stderr)
        sys.exit(1)
    parsed_dir = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    for jf in sorted(parsed_dir.glob("do_mpsc_*.json")):
        out_path, total, top = build(jf, out_dir)
        print(f"{out_path.name}: {total} blocos ({top} ⭐ top)")


if __name__ == "__main__":
    main()
