#!/usr/bin/env python3
"""Parser linha-a-linha do DOTC-e (Diário Oficial do TCE/SC).

Identifica blocos delimitados por linhas "PROCESSO Nº:..." e extrai:
- numero processo + tipo (REP, DEN, PPA, RLA, RLI, APE, CON, REC, ADM, TCE, ACO, LEV, ...)
- unidade gestora
- responsáveis / interessados
- assunto
- tipo do ato (DECISÃO SINGULAR, ACÓRDÃO, PARECER PRÉVIO, EDITAL DE CITAÇÃO, ...)
- relator (quando aparece)
- cidade (linha imediatamente anterior ao header, ou inferida da unidade gestora)
- valores de multa (R$ x,xx)
- corpo (texto após o cabeçalho, truncado)
- score político (palavras-chave + tipo de processo + se for prefeitura)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Tipos de processo (prefixo padrão do TCE)
PROCESSO_RE = re.compile(
    r"^\s*PROCESSO\s*(?:N[ºO\.]?\s*)?:?\s*"
    r"([A-Z@]{2,6})\s*([0-9]{2}/[0-9]{6,})", re.IGNORECASE | re.MULTILINE
)

# Tipos de processo conhecidos no TCE/SC
TIPOS_PROCESSO = {
    "REP": "Representação",
    "DEN": "Denúncia",
    "RLA": "Relatório de Auditoria",
    "RLI": "Relatório de Inspeção",
    "REC": "Recurso",
    "APE": "Aposentadoria/Pensão",
    "PPA": "Parecer Prévio (Contas Anuais)",
    "PCA": "Prestação de Contas do Administrador",
    "PCP": "Prestação de Contas do Prefeito",
    "PCR": "Prestação de Contas do Responsável",
    "PNO": "Processo Normativo",
    "PMO": "Processo de Monitoramento",
    "PAP": "Processo de Apuração",
    "CON": "Consulta",
    "TCE": "Processo do TCE",
    "ADM": "Administrativo",
    "LEV": "Levantamento",
    "LCC": "Licitações e Contratos",
    "MCO": "Medida Cautelar",
    "REV": "Revisão",
    "ACO": "Ação Civil",
    "SPE": "Especial",
    "@CON": "Consulta (eletrônica)",
    "@ANP": "Análise (eletrônica)",
    "@REP": "Representação (eletrônica)",
}

# Cabeçalhos de ato dentro de um bloco
TIPO_ATO_RE = re.compile(
    r"^\s*(DECIS[ÃA]O SINGULAR|AC[ÓO]RD[ÃA]O|PARECER PR[ÉE]VIO|"
    r"EDITAL DE CITA[ÇC][ÃA]O|EDITAL DE AUDI[ÊE]NCIA|RESOLU[ÇC][ÃA]O|"
    r"ATA DA SESS[ÃA]O|VOTO|RELAT[ÓO]RIO)\b[^\n]*",
    re.IGNORECASE | re.MULTILINE,
)

# Campos de cabeçalho dentro do bloco
FIELD_RE = re.compile(
    r"^\s*(UNIDADE GESTORA|RESPONS[ÁA]VEIS?|INTERESSADO[AS]?|"
    r"ASSUNTO|REPRESENTANTE|REPRESENTADO[AS]?|DENUNCIANTE|"
    r"PROCURADOR(?:ES)?|RELATOR[A]?|MINIST[ÉE]RIO P[ÚU]BLICO|"
    r"PROCESSO|PROCURADORIA|GERENTE|SECRET[ÁA]RIO)"
    r"\s*[:.]\s*(.*)$",
    re.IGNORECASE | re.MULTILINE,
)

FIELD_NORMALIZE = {
    "UNIDADE GESTORA": "unidade_gestora",
    "RESPONSAVEL": "responsaveis",
    "RESPONSÁVEL": "responsaveis",
    "RESPONSAVEIS": "responsaveis",
    "RESPONSÁVEIS": "responsaveis",
    "INTERESSADO": "interessados",
    "INTERESSADA": "interessados",
    "INTERESSADOS": "interessados",
    "INTERESSADAS": "interessados",
    "ASSUNTO": "assunto",
    "REPRESENTANTE": "representante",
    "REPRESENTADO": "representado",
    "REPRESENTADA": "representado",
    "REPRESENTADOS": "representado",
    "REPRESENTADAS": "representado",
    "DENUNCIANTE": "denunciante",
    "PROCURADOR": "procurador",
    "PROCURADORES": "procurador",
    "PROCURADORIA": "procuradoria",
    "RELATOR": "relator",
    "RELATORA": "relator",
    "MINISTÉRIO PÚBLICO": "ministerio_publico",
    "MINISTERIO PUBLICO": "ministerio_publico",
    "GERENTE": "gerente",
    "SECRETÁRIO": "secretario",
    "SECRETARIO": "secretario",
}

# Footer / cabeçalhos de página a ignorar
FOOTER_RE = re.compile(
    r"Tribunal de Contas de Santa Catarina\s*-\s*Diário Oficial Eletrônico.*?Pág\.\s*\d+",
    re.IGNORECASE,
)

# Conselheiros conhecidos (para detecção de relator quando não vier prefixado)
CONSELHEIROS = [
    "Herneus João De Nadal", "José Nei Alberton Ascari",
    "Adircélio de Moraes Ferreira Júnior", "Wilson Rogério Wan-Dall",
    "Luiz Roberto Herbst", "Luiz Eduardo Cherem", "Aderson Flores",
    "Gerson dos Santos Sicca", "Cleber Muniz Gavi", "Sabrina Nunes Iocken",
]

# Palavras-chave para score político (de relevância para vídeo / denúncia)
KEYWORDS = {
    "irregularidade": 4,
    "irregular": 3,
    "fraude": 8,
    "sobrepreço": 8,
    "superfaturamento": 8,
    "direcionamento": 6,
    "licitação": 4,
    "pregão": 3,
    "dispensa de licitação": 6,
    "inexigibilidade": 5,
    "convênio": 3,
    "multa": 4,
    "ressarcimento": 4,
    "dano ao erário": 7,
    "improbidade": 8,
    "rejeição": 5,
    "rejeitar": 4,
    "contas rejeitadas": 7,
    "contas irregulares": 6,
    "parecer pela rejeição": 7,
    "ato ilegal": 5,
    "nepotismo": 6,
    "publicidade institucional": 4,
    "promoção pessoal": 5,
    "concessão": 3,
    "permissão": 2,
    "cautelar": 4,
    "sustação": 5,
    "suspensão do certame": 5,
    "tomada de contas especial": 6,
    "transparência": 3,
    "lai": 3,
    "lei de acesso à informação": 4,
    "prefeito": 5,
    "ex-prefeito": 6,
    "vice-prefeito": 4,
    "vereador": 4,
    "secretário municipal": 3,
    "câmara municipal": 3,
    "câmara de vereadores": 3,
    "obra pública": 4,
    "saúde": 1,
    "educação": 1,
    "concurso público": 3,
    "cargo em comissão": 3,
}

# Score extra por tipo de processo
SCORE_TIPO_PROC = {
    "DEN": 5, "REP": 4, "RLA": 5, "RLI": 4,
    "PPA": 5, "PCA": 4, "PCP": 6, "PCR": 3,
    "TCE": 2, "REV": 3, "REC": 1, "APE": 0,
    "CON": 0, "ADM": 1, "ACO": 4, "LCC": 4,
    "MCO": 4, "LEV": 2,
}

VALOR_RE = re.compile(r"R\$\s*([\d.,]+)")


def clean_text(text: str) -> str:
    text = FOOTER_RE.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def find_city_above(lines: list[str], idx: int) -> str | None:
    """Procura, nas linhas acima do header PROCESSO, uma linha curta
    isolada (provável nome de cidade — formato 'Cidade' em linha solta)."""
    for j in range(idx - 1, max(idx - 10, -1), -1):
        line = lines[j].strip()
        if not line:
            continue
        # Cidade: linha curta, capitalizada, sem dois-pontos
        if (
            2 < len(line) < 50
            and ":" not in line
            and not line.isupper()  # cabeçalhos institucionais costumam ser MAIÚSCULAS
            and re.match(r"^[A-ZÁ-Ú][\w\sÁ-úà-ú\-']+$", line)
            and "Tribunal" not in line
            and "Página" not in line
            and "Sumário" not in line
        ):
            return line
        # Para se encontrar marca de header de seção
        if "Administração Pública" in line or "PODER " in line.upper():
            return None
    return None


def infer_city_from_ug(unidade_gestora: str) -> str | None:
    if not unidade_gestora:
        return None
    m = re.search(
        r"(?:Prefeitura Municipal|Câmara Municipal|Município|Instituto.+?de|"
        r"Fundo.+?de|Fundação.+?de|SAMAE|SAAE)\s+(?:de\s+)?([A-ZÁ-Ú][\wÁ-úà-ú\s\-']+?)(?:[/,]|$)",
        unidade_gestora,
    )
    if m:
        return m.group(1).strip().rstrip(".")
    return None


# Abertura da parte decisória. Separado dos itens numerados de propósito: num
# acórdão o dispositivo é uma lista ("1. Julgar irregulares / 2. Aplicar multa /
# 3. Dar ciência"), e ancorar no último item começaria o recorte em "Dar
# ciência", jogando fora exatamente a condenação que interessa.
ABERTURA_RE = re.compile(
    r"(ACORDAM\s+os\s+(?:Conselheiros|Membros)|"
    r"(?:Diante|Ante|Em face)\s+do\s+exposto|"
    r"decid[eo]\s*:|DECIDE\s*:|RESOLVE\s*:)",
    re.IGNORECASE,
)

# usado só quando não há abertura explícita (decisões singulares curtas)
ITEM_RE = re.compile(
    r"^\s*\d+(?:\.\d+)?\.?\s*(?:Julgar|Conhecer|Considerar|Aplicar|Determinar|"
    r"Dar\s+ci[êe]ncia|Homologar|Arquivar|Sustar|Deferir|Indeferir|Negar)",
    re.IGNORECASE | re.MULTILINE,
)

# o que caracteriza uma decisão de mérito de fato tomada
MERITO_RE = re.compile(
    r"julgar?\s+(?:as\s+contas\s+)?irregular|julgar?\s+regular|"
    r"aplicar?\s+(?:a\s+)?multa|multa\s+no\s+valor|imputar\s+d[ée]bito|"
    r"parecer\s+pr[ée]vio\s+(?:pela|recomendando)|"
    r"sustar|medida\s+cautelar|suspend|arquivar|dar\s+provimento|negar\s+provimento",
    re.IGNORECASE,
)


def extract_dispositivo(block_text: str, limite: int = 3000) -> str | None:
    """Recorta a parte decisória do bloco.

    Ancora na ÚLTIMA abertura ("Acordam os Conselheiros...", "Diante do
    exposto"): o relatório de um acórdão costuma citar decisões anteriores, e a
    primeira ocorrência traria a decisão de outro processo como se fosse desta.
    A partir da abertura o recorte segue até o fim, preservando a lista inteira
    de itens decididos.
    """
    marks = list(ABERTURA_RE.finditer(block_text))
    if not marks:
        marks = list(ITEM_RE.finditer(block_text))
        if not marks:
            return None
    # PRIMEIRA abertura, não a última. A segmentação por número de processo às
    # vezes estende o bloco até o ato seguinte da mesma página do Diário, e aí a
    # última abertura é a decisão do vizinho — foi assim que decisões de Garopaba
    # e Florianópolis apareceram em cards de Forquilhinha e Criciúma. "Acordam os
    # Conselheiros" praticamente só ocorre na parte dispositiva, então a primeira
    # ocorrência é a deste processo.
    return re.sub(r"\s+", " ", block_text[marks[0].start():][:limite]).strip()


def parse_blocks(text: str) -> list[dict]:
    """Localiza cada PROCESSO e extrai o bloco até o próximo PROCESSO."""
    text = clean_text(text)
    matches = list(PROCESSO_RE.finditer(text))
    lines = text.split("\n")

    # mapear cada linha para sua posição cumulativa (para localizar lines around match)
    line_offsets = [0]
    for line in lines:
        line_offsets.append(line_offsets[-1] + len(line) + 1)

    def char_to_lineidx(pos: int) -> int:
        # busca binária
        lo, hi = 0, len(line_offsets) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if line_offsets[mid] <= pos < line_offsets[mid + 1]:
                return mid
            if line_offsets[mid] < pos:
                lo = mid + 1
            else:
                hi = mid
        return lo

    blocks = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block_text = text[start:end]
        line_idx = char_to_lineidx(start)

        prefixo = m.group(1).upper().strip("@")
        numero = f"{prefixo} {m.group(2)}"

        # Tenta achar a cidade acima
        city = find_city_above(lines, line_idx)

        rec = {
            "numero_processo": numero,
            "tipo_processo": TIPOS_PROCESSO.get(prefixo, prefixo),
            "tipo_processo_sigla": prefixo,
            "cidade_acima": city,
        }

        # Captura campos do bloco
        for fm in FIELD_RE.finditer(block_text):
            label = fm.group(1).upper().strip()
            value = fm.group(2).strip()
            key = FIELD_NORMALIZE.get(label, label.lower().replace(" ", "_"))
            if key in rec and rec[key]:
                # já existe — concatena se for diferente
                if value not in rec[key]:
                    rec[key] = rec[key] + " | " + value
            else:
                rec[key] = value

        # Tipo de ato
        ato_m = TIPO_ATO_RE.search(block_text)
        if ato_m:
            rec["tipo_ato"] = re.sub(r"\s+", " ", ato_m.group(0)).strip()

        # Cidade inferida da unidade gestora se acima não funcionou
        if not city:
            inf = infer_city_from_ug(rec.get("unidade_gestora", ""))
            if inf:
                rec["cidade_inferida"] = inf

        # Valores monetários (multas ou contratos)
        valores = list({m.group(0) for m in VALOR_RE.finditer(block_text)})
        if valores:
            rec["valores_mencionados"] = valores[:10]

        # Corpo (truncado para score / análise)
        rec["_corpo_curto"] = re.sub(r"\s+", " ", block_text[:2500]).strip()

        # Dispositivo — o que o tribunal DECIDIU.
        # Sem isto o dado só continha o objeto do processo ("apurar supostas
        # irregularidades em X") e o número do acórdão, e qualquer afirmação de
        # desfecho no produto final virava inferência: um processo que terminou
        # regular ficava indistinguível de um que terminou em multa.
        # O dispositivo vem no FIM do bloco, então truncar o começo (como o
        # _corpo_curto faz) justamente o descarta.
        disp = extract_dispositivo(block_text)
        if disp:
            rec["dispositivo"] = disp

        # Score
        blob = rec["_corpo_curto"].lower()
        for k in ("unidade_gestora", "assunto", "interessados", "responsaveis",
                 "representado", "representante"):
            if rec.get(k):
                blob += " " + rec[k].lower()
        score = SCORE_TIPO_PROC.get(prefixo, 0)
        hits = []
        for kw, w in KEYWORDS.items():
            if kw in blob:
                score += w
                hits.append(kw)
        # bônus: prefeitura como UG ou alvo
        if "prefeitura" in (rec.get("unidade_gestora", "") or "").lower():
            score += 3
            hits.append("prefeitura-ug")
        if re.search(r"câmara municipal|câmara de vereadores",
                     (rec.get("unidade_gestora", "") or "").lower()):
            score += 3
            hits.append("camara-ug")
        rec["score"] = score
        rec["keywords"] = hits

        blocks.append(rec)
    return blocks


def process_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    blocks = parse_blocks(text)
    return {
        "arquivo": path.name,
        "total_blocos": len(blocks),
        "blocos": blocks,
    }


def main():
    if len(sys.argv) < 2:
        print("uso: parse_tcesc.py <txt-file> [<txt-file>...]", file=sys.stderr)
        sys.exit(1)
    for arg in sys.argv[1:]:
        result = process_file(Path(arg))
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
