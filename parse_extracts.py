#!/usr/bin/env python3
"""Parser linha-a-linha (rápido, sem backtracking) do Diário Oficial do MPSC."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RELEVANT_HEADERS = [
    "EXTRATO DE INSTAURAÇÃO DO INQUÉRITO CIVIL",
    "EXTRATO DE INSTAURAÇÃO DE INQUÉRITO CIVIL",
    "EXTRATO DE CONCLUSÃO DO INQUÉRITO CIVIL",
    "EXTRATO DE CONCLUSÃO DE INQUÉRITO CIVIL",
    "EXTRATO DE INSTAURAÇÃO DO PROCEDIMENTO PREPARATÓRIO",
    "EXTRATO DE INSTAURAÇÃO DE PROCEDIMENTO PREPARATÓRIO",
    "EXTRATO DE CONCLUSÃO DO PROCEDIMENTO PREPARATÓRIO",
    "EXTRATO DE CONCLUSÃO DE PROCEDIMENTO PREPARATÓRIO",
    "EXTRATO DE CONVERSÃO",
    "EXTRATO DE INSTAURAÇÃO DO PROCEDIMENTO ADMINISTRATIVO",
    "EXTRATO DE INSTAURAÇÃO DE PROCEDIMENTO ADMINISTRATIVO",
    "EXTRATO DE CONCLUSÃO DO PROCEDIMENTO ADMINISTRATIVO",
    "EXTRATO DE CONCLUSÃO DE PROCEDIMENTO ADMINISTRATIVO",
    "EXTRATO DE INSTAURAÇÃO DA NOTÍCIA DE FATO",
    "EXTRATO DE INSTAURAÇÃO DE NOTÍCIA DE FATO",
    "EXTRATO DE CONCLUSÃO DA NOTÍCIA DE FATO",
    "EXTRATO DE CONCLUSÃO DE NOTÍCIA DE FATO",
    "RECOMENDAÇÃO N.",
]
RELEVANT_PREFIXES = tuple(RELEVANT_HEADERS)

# Prefixos que marcam início de QUALQUER bloco do MP — usado para detectar fim.
ANY_BLOCK_PREFIXES = (
    "EXTRATO DE",
    "EXTRATO DA DECISÃO",
    "EDITAL DE",
    "PORTARIA N.",
    "ATO N.",
    "RECOMENDAÇÃO N.",
    "TERMO DE COMPROMISSO",
    "TERMO DE AJUSTAMENTO",
    "PROCURADORIA-GERAL DE JUSTIÇA",
    "PROMOTORIAS DE JUSTIÇA",
    "CONSELHO SUPERIOR DO",
    "COLÉGIO DE PROCURADORES",
    "CORREGEDORIA-GERAL DO",
    "CENTRO DE ESTUDOS",
    "COMISSÃO DE CONCURSO",
    "SECRETARIA-GERAL DO",
    "CONTRATO N.",
    "CONVÊNIO N.",
    "ERRATA",
)

FOOTER_MARKER = "Diário Oficial Eletrônico do Ministério Público"
PAGE_HEADER_MARKER_RE = re.compile(r"^Divulgação:.*Publicação:.*Ano \d+\|n\. \d+\|Pág\.\d+")

KEYWORDS_POLITICAL = {
    "improbidade administrativa": 10,
    "improbidade": 8,
    "desvio de finalidade": 6,
    "desvio de função": 5,
    "desvio": 4,
    "fraude": 6,
    "fraudulent": 5,
    "licitação": 5,
    "contrato administrativo": 4,
    "dispensa de licitação": 7,
    "superfaturamento": 8,
    "sobrepreço": 7,
    "prefeito": 6,
    "ex-prefeito": 6,
    "vice-prefeito": 5,
    "vereador": 5,
    "secretário municipal": 5,
    "câmara municipal": 5,
    "câmara de vereadores": 5,
    "nepotismo": 8,
    "enriquecimento ilícito": 9,
    "publicidade institucional": 5,
    "eleitoral": 3,
    "candidato": 3,
    "obra pública": 4,
    "obras públicas": 4,
    "merenda": 4,
    "convênio": 3,
    "subsídio": 3,
    "patrimônio público": 4,
    "uso de bens públicos": 4,
    "acumulação ilegal": 5,
    "acumulação irregular": 5,
    "acumulação indevida": 5,
    "ponto eletrônico": 4,
    "transparência": 3,
    "concurso público": 3,
    "cargo em comissão": 3,
    "cessão irregular": 4,
    "saúde pública": 2,
    "educação": 1,
    "meio ambiente": 2,
    "desmatamento": 4,
    "poluição": 3,
    "ambiental": 2,
    "loteamento irregular": 4,
    "loteamento clandestino": 4,
    "área de preservação": 3,
    "irregularidade": 2,
    "ato ilegal": 4,
    "abuso de poder": 6,
    "abuso de autoridade": 6,
    "assédio moral": 3,
    "assédio sexual": 4,
    "violação": 2,
}
MUNICIPIO_RE = re.compile(r"munic[íi]pio de\s+[A-Za-zÀ-ÿ]")
PREFEITURA_RE = re.compile(r"prefeitur[ao] municipal")
NUMERO_RE = re.compile(r"N\.\s*([\d./-]+)")
FIELD_RE = re.compile(
    r"^(COMARCA|ÓRGÃO DO MINISTÉRIO PÚBLICO|Partes|Parte|Investigados|Investigado|"
    r"Objeto|Membro do Ministério Público|Data|EXTRATO DA DECISÃO|PESSOA CIENTIFICADA|"
    r"PESSOAS CIENTIFICADAS|Promotor de Justiça|MEMBRO DO MINISTÉRIO PÚBLICO)\s*:\s*(.*)$"
)
FIELD_NORMALIZE = {
    "COMARCA": "comarca",
    "ÓRGÃO DO MINISTÉRIO PÚBLICO": "orgao",
    "Partes": "partes",
    "Parte": "partes",
    "Investigados": "investigados",
    "Investigado": "investigados",
    "Objeto": "objeto",
    "Membro do Ministério Público": "membro",
    "MEMBRO DO MINISTÉRIO PÚBLICO": "membro",
    "Promotor de Justiça": "membro",
    "Data": "data",
    "EXTRATO DA DECISÃO": "decisao",
    "PESSOA CIENTIFICADA": "pessoa_cientificada",
    "PESSOAS CIENTIFICADAS": "pessoa_cientificada",
}


def is_relevant_header(line: str) -> bool:
    return line.startswith(RELEVANT_PREFIXES)


def is_any_block_start(line: str) -> bool:
    return line.startswith(ANY_BLOCK_PREFIXES)


def clean_lines(text: str):
    """Itera por linhas, removendo footers e cabeçalhos de página."""
    skip_next = 0
    for line in text.split("\n"):
        stripped = line.strip()
        if skip_next > 0:
            skip_next -= 1
            continue
        if FOOTER_MARKER in stripped:
            skip_next = 4  # pula o footer multilinha
            continue
        if PAGE_HEADER_MARKER_RE.match(stripped):
            continue
        yield stripped


def parse_blocks(text: str):
    lines = list(clean_lines(text))
    blocks = []
    current = None
    for line in lines:
        if not line:
            if current:
                current["_raw"].append("")
            continue
        if is_relevant_header(line):
            if current:
                blocks.append(current)
            current = {"header": line, "_raw": []}
            continue
        if current is not None and is_any_block_start(line):
            blocks.append(current)
            current = None
            continue
        if current is not None:
            current["_raw"].append(line)
    if current:
        blocks.append(current)
    return blocks


def extract_fields(block: dict) -> dict:
    header = block["header"]
    rec = {"header": header}
    num = NUMERO_RE.search(header)
    if num:
        rec["numero"] = num.group(1)

    current_field = None
    buffers: dict[str, list[str]] = {}

    for line in block["_raw"]:
        if not line:
            current_field = None
            continue
        m = FIELD_RE.match(line)
        if m:
            label = m.group(1)
            value_start = m.group(2)
            field_key = FIELD_NORMALIZE.get(label, label.lower().replace(" ", "_"))
            current_field = field_key
            buffers.setdefault(field_key, [])
            if value_start:
                buffers[field_key].append(value_start)
        else:
            if current_field:
                buffers[current_field].append(line)

    for k, parts in buffers.items():
        rec[k] = re.sub(r"\s+", " ", " ".join(parts)).strip()

    return rec


def score_political(rec: dict):
    text_parts = []
    for key in ("objeto", "decisao", "partes", "investigados", "header"):
        if rec.get(key):
            text_parts.append(rec[key].lower())
    blob = " ".join(text_parts)
    score = 0
    hits = []
    for kw, weight in KEYWORDS_POLITICAL.items():
        if kw in blob:
            score += weight
            hits.append(kw)
    if MUNICIPIO_RE.search(blob):
        score += 4
        hits.append("município-parte")
    if PREFEITURA_RE.search(blob):
        score += 4
        hits.append("prefeitura")
    return score, hits


def process_file(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    raw_blocks = parse_blocks(raw)
    records = []
    for b in raw_blocks:
        rec = extract_fields(b)
        rec["score_politico"], rec["keywords"] = score_political(rec)
        records.append(rec)
    return {
        "arquivo": path.name,
        "total_blocos_relevantes": len(records),
        "blocos": records,
    }


def main():
    if len(sys.argv) < 2:
        print("uso: parse_extracts.py <txt-file> [txt-file ...]", file=sys.stderr)
        sys.exit(1)
    for arg in sys.argv[1:]:
        result = process_file(Path(arg))
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
