#!/usr/bin/env python3
"""Gera markdown por região com os casos do TCE/SC (DOTC-e) por cidade.

Espelha o build_regioes.py (que faz o MP), mas lê tcesc/parsed/*.json e usa
a lógica de status própria do TCE (acórdão / julgar irregular / multa / parecer).
Reusa a mesma configuração de REGIOES do build_regioes.py — ao adicionar novas
regiões lá, este script passa a cobri-las automaticamente.

Uso: python3 build_regioes_tce.py
Saída: tcesc/resumos/regioes/regiao-<sigla>-tce.md
"""
from __future__ import annotations

import json
import glob
import re
from collections import defaultdict
from pathlib import Path

from build_regioes import REGIOES, TODAS_CIDADES


def regiao_slug(regiao: str) -> str:
    """'Carbonífera / AMREC' -> 'amrec'; 'Oeste / AMOSC (Chapecó)' -> 'amosc'."""
    part = regiao.split("/")[-1].strip()
    part = re.sub(r"\(.*?\)", "", part).strip()
    return part.lower().replace(" ", "-")


def make_patterns() -> dict:
    """Dois padrões por cidade:
    - strong: nome puro (token inteiro) — usado em campos que já identificam a UG
    - prep:   'de/do/da/em <Cidade>' — usado em campos-texto (assunto/partes) para
              evitar falso positivo quando o corpo cita outra cidade de passagem
    """
    pats = {}
    for c in TODAS_CIDADES:
        esc = re.escape(c)
        strong = re.compile(
            r"(?<![A-Za-zÀ-ÿ])" + esc + r"(?![A-Za-zÀ-ÿ])", re.IGNORECASE
        )
        prep = re.compile(
            r"(?:de|do|da|em)\s+" + esc + r"(?![A-Za-zÀ-ÿ])", re.IGNORECASE
        )
        pats[c] = (strong, prep)
    return pats


# Campos que identificam DE QUEM são as contas. A unidade gestora é o sinal mais
# forte; cidade_acima/cidade_inferida vêm do próprio parser (match por nome puro).
STRONG_FIELDS = ("unidade_gestora", "cidade_acima", "cidade_inferida")
# Campos-texto: só contam com a preposição "de <Cidade>" para reduzir ruído.
PREP_FIELDS = ("assunto", "responsaveis", "representado", "interessados")


def tce_status(rec: dict) -> str:
    """Classifica com base no tipo de ato e no texto da decisão."""
    ato = (rec.get("tipo_ato") or "").lower()
    corpo = (rec.get("_corpo_curto") or "").lower()
    assunto = (rec.get("assunto") or "").lower()
    txt = f"{ato} {corpo} {assunto}"
    tem_multa = "multa" in txt

    if "acórdão" in ato or "acordao" in ato:
        if re.search(r"julgar.{0,25}irregular|contas.{0,12}irregular|irregularidade", txt):
            return "⬛ julgado irregular + multa" if tem_multa else "⬛ julgado irregular"
        if "rejei" in txt:
            return "🔴 contas rejeitadas"
        if "ressalva" in txt:
            return "🟡 regular c/ ressalvas"
        if re.search(r"julgar.{0,15}regular|regularidade", txt):
            return "🟢 julgado regular"
        return "⬛ acórdão (decisão)"
    if "parecer prévio" in ato or "parecer previo" in ato:
        if "rejei" in txt:
            return "🔴 parecer pela rejeição"
        if "aprova" in txt:
            return "🟢 parecer pela aprovação"
        return "⬛ parecer prévio"
    if "decisão singular" in ato or "decisao singular" in ato:
        if re.search(r"cautelar|sustaç|sustar|suspens", txt):
            return "🟠 cautelar / sustação"
        if "irregular" in txt:
            return "🔴 apontou irregularidade"
        return "⬛ decisão singular"
    if re.search(r"cita[çc]|audi[êe]ncia", ato):
        return "🟡 em instrução (citação/audiência)"
    if re.search(r"cautelar|sustaç|sustar", txt):
        return "🟠 cautelar / sustação"
    if tem_multa:
        return "🔴 multa aplicada"
    return "❔ em tramitação"


def _sq(s, limit=None) -> str:
    """Colapsa espaços em branco e trunca."""
    out = re.sub(r"\s+", " ", str(s)).strip()
    if limit and len(out) > limit:
        out = out[: limit - 1] + "…"
    return out


def _fmt_valores(rec: dict):
    vs = rec.get("valores_mencionados")
    if not vs:
        return None
    return ", ".join(vs[:5])


def case_md(rec: dict, edicao: str) -> str:
    score = rec.get("score", 0)
    star = "⭐" if score >= 12 else ("•" if score >= 6 else "·")
    status = tce_status(rec)
    header = f"{rec.get('numero_processo', 'PROCESSO')} — {rec.get('tipo_processo', '')}".strip()

    lines = [f"#### {star} {header}"]
    meta = [f"**Edição:** {edicao}", f"**Status:** {status}"]
    if rec.get("tipo_ato"):
        meta.append(f"**Ato:** {rec['tipo_ato']}")
    if rec.get("relator"):
        meta.append(f"**Relator(a):** {_sq(rec['relator'], 80)}")
    lines.append(" · ".join(meta))
    lines.append("")

    if rec.get("unidade_gestora"):
        lines.append(f"**Unidade gestora:** {_sq(rec['unidade_gestora'], 200)}")
    resp = rec.get("responsaveis") or rec.get("interessados") or rec.get("representado")
    if resp:
        lines.append(f"**Responsáveis/Partes:** {_sq(resp, 400)}")
    if rec.get("assunto"):
        lines.append(f"**Assunto:** {_sq(rec['assunto'], 500)}")
    val = _fmt_valores(rec)
    if val:
        lines.append(f"**Valores citados:** {val}")
    lines.append("")
    return "\n".join(lines)


def build_cidade_section(cidade: str, blocks: list) -> str:
    if not blocks:
        return f"## {cidade}\n\n_Sem casos do TCE no período._\n\n---\n"

    blocks_sorted = sorted(
        blocks, key=lambda b: (-b.get("score", 0), b.get("_edicao", ""))
    )
    n = len(blocks_sorted)
    n_top = sum(1 for b in blocks_sorted if b.get("score", 0) >= 10)
    n_multa = sum(1 for b in blocks_sorted if "multa" in (b.get("_corpo_curto") or "").lower())

    lines = [f"## {cidade}", ""]
    lines.append(f"_{n} casos do TCE no período · {n_top} com score ≥10 · {n_multa} citam multa_")
    lines.append("")

    if n_top:
        lines.append(f"### 🎬 Destaques ({n_top} casos)")
        lines.append("")
        for b in blocks_sorted[:n_top]:
            lines.append(case_md(b, b["_edicao"]))
            lines.append("---")
            lines.append("")
        rest = blocks_sorted[n_top:]
    else:
        rest = blocks_sorted

    if rest:
        lines.append(f"### 📂 Demais casos ({len(rest)})")
        lines.append("")
        for b in rest:
            lines.append(case_md(b, b["_edicao"]))
            lines.append("---")
            lines.append("")
    return "\n".join(lines)


def _br(d: str) -> str:
    y, m, day = d.split("-")
    return f"{day}/{m}/{y}"


def main():
    out_dir = Path("tcesc/resumos/regioes")
    out_dir.mkdir(parents=True, exist_ok=True)

    patterns = make_patterns()

    by_city = defaultdict(list)
    seen = defaultdict(set)
    edicoes = set()

    for f in sorted(glob.glob("tcesc/parsed/*.json")):
        d = json.loads(Path(f).read_text())
        m = re.search(r"(\d{4}-\d{2}-\d{2})", d.get("arquivo", Path(f).name))
        ed = m.group(1) if m else Path(f).stem
        edicoes.add(ed)
        for b in d.get("blocos", []):
            b["_edicao"] = ed
            strong_blob = " ".join(str(b.get(k, "") or "") for k in STRONG_FIELDS)
            prep_blob = " ".join(str(b.get(k, "") or "") for k in PREP_FIELDS)
            matched = {
                c for c, (strong, prep) in patterns.items()
                if strong.search(strong_blob) or prep.search(prep_blob)
            }
            for city in matched:
                key = (b.get("numero_processo", ""), ed)
                if key not in seen[city]:
                    seen[city].add(key)
                    by_city[city].append(b)

    edic = sorted(edicoes)
    periodo = (
        f"{_br(edic[0])} a {_br(edic[-1])} ({len(edic)} edições do DOTC-e)"
        if edic else "(sem edições)"
    )

    counts = {}
    for regiao, cidades in REGIOES.items():
        total = sum(len(by_city[c]) for c in cidades)
        counts[regiao] = total
        out_lines = [
            f"# TCE/SC — {regiao}",
            "",
            f"**Período coberto:** {periodo}",
            "",
            f"**Cidades nesta região:** {len(cidades)} ({', '.join(cidades)})",
            "",
            f"**Total de casos do TCE na região:** {total}",
            "",
            "| Cidade | Casos TCE |",
            "|--------|-----------|",
        ]
        for c in cidades:
            out_lines.append(f"| {c} | {len(by_city[c])} |")
        out_lines += [
            "",
            "---",
            "",
            "> **Status TCE:** ⬛ julgado irregular / decisão · 🔴 rejeição / multa / irregularidade",
            "> · 🟠 cautelar / sustação · 🟡 em instrução ou c/ ressalvas · 🟢 regular / aprovado · ❔ em tramitação",
            "",
            "> ℹ O TCE **julga contas e aplica multa/ressarcimento** — quando há Acórdão \"julgar irregular\", já é decisão.",
            "",
            "---",
            "",
        ]
        for c in cidades:
            out_lines.append(build_cidade_section(c, by_city[c]))

        out_path = out_dir / f"regiao-{regiao_slug(regiao)}-tce.md"
        out_path.write_text("\n".join(out_lines))
        print(f"{out_path}: {total} casos ({len(cidades)} cidades)")

    return counts, by_city


if __name__ == "__main__":
    main()
