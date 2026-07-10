#!/usr/bin/env python3
"""Gera arquivos markdown por região do sul de SC com todos os casos por cidade."""
from __future__ import annotations

import json
import glob
import re
from collections import defaultdict
from pathlib import Path

REGIOES = {
    "Carbonífera / AMREC": ["Balneário Rincão", "Cocal do Sul", "Criciúma", "Forquilhinha", "Içara", "Lauro Müller", "Morro da Fumaça", "Nova Veneza", "Orleans", "Siderópolis", "Treviso", "Urussanga"],
    "Extremo Sul / AMESC": ["Araranguá", "Balneário Arroio do Silva", "Balneário Gaivota", "Ermo", "Jacinto Machado", "Maracajá", "Meleiro", "Morro Grande", "Passo de Torres", "Praia Grande", "Santa Rosa do Sul", "São João do Sul", "Sombrio", "Timbé do Sul", "Turvo"],
    "Tubarão-Laguna / AMUREL": ["Armazém", "Braço do Norte", "Capivari de Baixo", "Grão-Pará", "Gravatal", "Imaruí", "Imbituba", "Jaguaruna", "Laguna", "Pescaria Brava", "Rio Fortuna", "Sangão", "Santa Rosa de Lima", "São Ludgero", "São Martinho", "Treze de Maio", "Tubarão", "Pedras Grandes"],
    "Grande Florianópolis / GRANFPOLIS": ["Palhoça", "Florianópolis", "São José", "Biguaçu", "Santo Amaro da Imperatriz", "Águas Mornas", "Antônio Carlos", "Angelina", "Anitápolis", "Alfredo Wagner", "Canelinha", "Garopaba", "Governador Celso Ramos", "Leoberto Leal", "Major Gercino", "Nova Trento", "Paulo Lopes", "Rancho Queimado", "São Bonifácio", "São João Batista", "São Pedro de Alcântara", "Tijucas"],
    "Oeste / AMOSC": ["Chapecó", "Águas de Chapecó", "Águas Frias", "Caxambu do Sul", "Cordilheira Alta", "Coronel Freitas", "Formosa do Sul", "Guatambú", "Irati", "Jardinópolis", "Nova Erechim", "Nova Itaberaba", "Pinhalzinho", "Planalto Alegre", "Quilombo", "Santiago do Sul", "São Carlos", "Serra Alta", "Sul Brasil", "União do Oeste", "Arvoredo", "Paial"],
    "Alto Vale do Itajaí / AMAVI": ["Agrolândia", "Agronômica", "Atalanta", "Aurora", "Braço do Trombudo", "Chapadão do Lageado", "Dona Emma", "Ibirama", "Imbuia", "Ituporanga", "José Boiteux", "Laurentino", "Lontras", "Mirim Doce", "Petrolândia", "Pouso Redondo", "Presidente Getúlio", "Presidente Nereu", "Rio do Campo", "Rio do Oeste", "Rio do Sul", "Salete", "Santa Terezinha", "Taió", "Trombudo Central", "Vidal Ramos", "Vitor Meireles", "Witmarsum"],
    "Alto Vale do Rio do Peixe / AMARP": ["Arroio Trinta", "Caçador", "Calmon", "Fraiburgo", "Ibiam", "Iomerê", "Lebon Régis", "Macieira", "Matos Costa", "Pinheiro Preto", "Rio das Antas", "Salto Veloso", "Tangará", "Timbó Grande", "Videira"],
    "Alto Irani / AMAI": ["Abelardo Luz", "Bom Jesus", "Entre Rios", "Faxinal dos Guedes", "Ipuaçu", "Lajeado Grande", "Marema", "Ouro Verde", "Passos Maia", "Ponte Serrada", "São Domingos", "Vargeão", "Xanxerê", "Xaxim"],
    "Alto Uruguai Catarinense / AMAUC": ["Alto Bela Vista", "Arabutã", "Concórdia", "Ipira", "Ipumirim", "Irani", "Itá", "Jaborá", "Lindóia do Sul", "Peritiba", "Piratuba", "Presidente Castello Branco", "Seara", "Xavantina"],
    "Extremo Oeste / AMEOSC": ["Anchieta", "Bandeirante", "Barra Bonita", "Belmonte", "Descanso", "Dionísio Cerqueira", "Guaraciaba", "Guarujá do Sul", "Iporã do Oeste", "Itapiranga", "Mondaí", "Palma Sola", "Paraíso", "Princesa", "Santa Helena", "São João do Oeste", "São José do Cedro", "São Miguel do Oeste", "Tunápolis"],
    "Entre Rios / AMERIOS": ["Bom Jesus do Oeste", "Caibi", "Campo Erê", "Cunha Porã", "Cunhataí", "Flor do Sertão", "Iraceminha", "Maravilha", "Modelo", "Palmitos", "Riqueza", "Romelândia", "Saltinho", "Santa Terezinha do Progresso", "São Miguel da Boa Vista", "Saudades", "Tigrinhos"],
    "Foz do Rio Itajaí / AMFRI": ["Balneário Camboriú", "Balneário Piçarras", "Bombinhas", "Camboriú", "Ilhota", "Itajaí", "Itapema", "Luiz Alves", "Navegantes", "Penha", "Porto Belo"],
    "Meio Oeste / AMMOC": ["Água Doce", "Capinzal", "Catanduvas", "Erval Velho", "Herval d'Oeste", "Ibicaré", "Joaçaba", "Lacerdópolis", "Luzerna", "Ouro", "Treze Tílias", "Vargem Bonita"],
    "Médio Vale do Itajaí / AMMVI": ["Apiúna", "Ascurra", "Benedito Novo", "Blumenau", "Botuverá", "Brusque", "Doutor Pedrinho", "Gaspar", "Guabiruba", "Indaial", "Pomerode", "Rio dos Cedros", "Rodeio", "Timbó"],
    "Noroeste / AMNOROESTE": ["Coronel Martins", "Galvão", "Jupiá", "Novo Horizonte", "São Bernardino", "São Lourenço do Oeste"],
    "Planalto Norte / AMPLANORTE": ["Bela Vista do Toldo", "Canoinhas", "Irineópolis", "Itaiópolis", "Mafra", "Major Vieira", "Monte Castelo", "Papanduva", "Porto União", "Três Barras"],
    "Planalto Sul / AMPLASC": ["Abdon Batista", "Brunópolis", "Campos Novos", "Celso Ramos", "Monte Carlo", "Vargem", "Zortéa"],
    "Nordeste / AMUNESC": ["Araquari", "Balneário Barra do Sul", "Campo Alegre", "Garuva", "Itapoá", "Joinville", "Rio Negrinho", "São Bento do Sul", "São Francisco do Sul"],
    "Contestado / AMURC": ["Curitibanos", "Frei Rogério", "Ponte Alta do Norte", "Santa Cecília", "São Cristóvão do Sul"],
    "Serra Catarinense / AMURES": ["Anita Garibaldi", "Bocaina do Sul", "Bom Jardim da Serra", "Bom Retiro", "Campo Belo do Sul", "Capão Alto", "Cerro Negro", "Correia Pinto", "Lages", "Otacílio Costa", "Painel", "Palmeira", "Ponte Alta", "Rio Rufino", "São Joaquim", "São José do Cerrito", "Urubici", "Urupema"],
    "Vale do Itapocu / AMVALI": ["Barra Velha", "Corupá", "Guaramirim", "Jaraguá do Sul", "Massaranduba", "São João do Itaperiú", "Schroeder"],
}


def regiao_slug(regiao: str) -> str:
    """'Carbonífera / AMREC' -> 'amrec'; usado para nomear o arquivo de saída."""
    part = regiao.split("/")[-1].strip()
    part = re.sub(r"\(.*?\)", "", part).strip()
    return part.lower().replace(" ", "-")


TODAS_CIDADES = [c for cs in REGIOES.values() for c in cs]


def build_matchers():
    """Uma única regex combinada (alternância de todas as cidades) em vez de
    295 regexes por bloco — evita a explosão O(edições×blocos×cidades).
    Ordena por comprimento desc para 'São João do Sul' casar antes de subnomes.
    Retorna (regex_prefixada, regex_nome_puro, mapa_lower->canônico).
    """
    alt = "|".join(re.escape(c) for c in sorted(TODAS_CIDADES, key=len, reverse=True))
    lower2canon = {c.lower(): c for c in TODAS_CIDADES}
    # "Município de X" / "Prefeitura (Municipal) de X" / "Comarca de X"
    prefixed = re.compile(
        r"(?:munic[íi]pio de|prefeitura(?: municipal)? de|comarca de)\s+("
        + alt + r")(?![A-Za-zÀ-ÿ])",
        re.IGNORECASE,
    )
    # nome puro (para a comarca, que já é um campo de cidade)
    bare = re.compile(r"(?<![A-Za-zÀ-ÿ])(" + alt + r")(?![A-Za-zÀ-ÿ])", re.IGNORECASE)
    return prefixed, bare, lower2canon


def status_from(rec):
    """Classifica o status com base em palavras-chave da decisão/conclusão."""
    text = (rec.get("decisao") or rec.get("partes") or "").lower()
    header = (rec.get("header") or "").lower()
    if "instauraç" in header or "instauração" in header:
        if "arquivamento" in text:
            # caso raro: instauração que já é arquivada (não comum)
            return "🟢 arquivado"
        return "🟡 em apuração"
    if "ação civil pública" in text and "ajuizamento" in text:
        return "🔴 ACP ajuizada"
    if "ação civil pública" in text and ("ajuiz" in text or "propor" in text):
        return "🔴 ACP em curso"
    if "acordo de não persecução" in text or "acnp" in text or "não persecução cível" in text:
        return "🟠 ACNP firmado"
    if "termo de ajustamento" in text or "tac " in text or "ajustamento de conduta" in text:
        return "🟠 TAC firmado"
    if "prescriç" in text:
        return "⚫ prescrito"
    if "arquivamento" in text or "arquivado" in text or "indeferimento" in text:
        return "🟢 arquivado"
    if "recomendação" in text and ("acatad" in text or "acolh" in text or "cumprid" in text):
        return "🟢 recomendação cumprida"
    return "❔ status indef."


def case_md(rec: dict, edicao_link: str) -> str:
    header = rec.get("header", "EXTRATO")
    score = rec.get("score_politico", 0)
    star = "⭐" if score >= 12 else ("•" if score >= 6 else "·")
    status = status_from(rec)
    lines = [f"#### {star} {header}"]
    meta = [f"**Edição:** [{edicao_link}](../edicoes/{edicao_link}.md)", f"**Status:** {status}"]
    if rec.get("comarca"):
        # Limpa "Comarca XÓRGÃO DO..." caso parser tenha pego junto
        comarca = re.split(r"(?:Órgão|ÓRGÃO|Data) ", rec["comarca"], maxsplit=1)[0].strip()
        meta.append(f"**Comarca:** {comarca}")
    if rec.get("orgao"):
        orgao = re.split(r"Data ", rec["orgao"], maxsplit=1)[0].strip()
        meta.append(f"**Órgão:** {orgao}")
    if rec.get("membro"):
        meta.append(f"**Promotor(a):** {rec['membro']}")
    lines.append(" · ".join(meta))
    lines.append("")
    partes = rec.get("partes") or rec.get("investigados")
    if partes:
        p = re.sub(r"\s+", " ", partes).strip()
        if len(p) > 800:
            p = p[:799] + "…"
        lines.append(f"**Partes:** {p}")
    obj = rec.get("objeto")
    if obj:
        o = re.sub(r"\s+", " ", obj).strip()
        if len(o) > 1200:
            o = o[:1199] + "…"
        lines.append(f"**Objeto:** {o}")
    dec = rec.get("decisao")
    if dec:
        d = re.sub(r"\s+", " ", dec).strip()
        if len(d) > 1200:
            d = d[:1199] + "…"
        lines.append(f"**Decisão/Conclusão:** {d}")
    if rec.get("data"):
        lines.append(f"**Data:** {rec['data']}")
    lines.append("")
    return "\n".join(lines)


def build_cidade_section(cidade: str, blocks: list) -> str:
    if not blocks:
        return f"## {cidade}\n\n_Sem casos encontrados no período._\n\n---\n"

    # ordenar por score desc, depois por edição desc
    blocks_sorted = sorted(blocks, key=lambda b: (-b.get("score_politico", 0), b.get("_edicao", "")))

    n = len(blocks_sorted)
    n_top = sum(1 for b in blocks_sorted if b.get("score_politico", 0) >= 10)
    n_apuracao = sum(1 for b in blocks_sorted if status_from(b) == "🟡 em apuração")

    lines = [f"## {cidade}", ""]
    lines.append(
        f"_{n} casos no período · {n_top} com score ≥10 · {n_apuracao} em apuração_"
    )
    lines.append("")

    if n_top:
        lines.append(f"### 🎬 Destaques para vídeo ({n_top} casos)")
        lines.append("")
        for b in blocks_sorted[:n_top]:
            lines.append(case_md(b, b["_edicao"]))
            lines.append("---")
            lines.append("")
        rest = blocks_sorted[n_top:]
    else:
        rest = blocks_sorted

    if rest:
        lines.append(f"### 📂 Demais casos da cidade ({len(rest)})")
        lines.append("")
        for b in rest:
            lines.append(case_md(b, b["_edicao"]))
            lines.append("---")
            lines.append("")

    return "\n".join(lines)


def main():
    out_dir = Path("resumos/regioes")
    out_dir.mkdir(parents=True, exist_ok=True)

    prefixed, bare, lower2canon = build_matchers()

    by_city = defaultdict(list)
    seen = defaultdict(set)  # dedup por (header, edicao, cidade)
    for f in sorted(glob.glob("parsed/do_mpsc_*.json")):
        d = json.loads(Path(f).read_text())
        ed = d["arquivo"].replace("do_mpsc_", "").replace(".txt", "")
        for b in d["blocos"]:
            b["_edicao"] = ed
            blob = " ".join(
                [str(b.get(k, "") or "") for k in ("partes", "objeto", "decisao", "header")]
            )
            comarca_low = (b.get("comarca", "") or "").lower()
            matched = set()
            for m in prefixed.finditer(blob):
                matched.add(lower2canon.get(m.group(1).lower()))
            for m in bare.finditer(comarca_low):
                matched.add(lower2canon.get(m.group(1).lower()))
            matched.discard(None)
            for city in matched:
                key = (b.get("header", ""), ed)
                if key not in seen[city]:
                    seen[city].add(key)
                    by_city[city].append(b)

    # Período coberto, derivado das edições efetivamente parseadas
    edicoes = sorted(
        Path(f).name.replace("do_mpsc_", "").replace(".json", "")[:10]
        for f in glob.glob("parsed/do_mpsc_*.json")
    )

    def _br(d: str) -> str:
        y, m, day = d.split("-")
        return f"{day}/{m}/{y}"

    periodo = (
        f"{_br(edicoes[0])} a {_br(edicoes[-1])} ({len(edicoes)} edições do DO-MPSC)"
        if edicoes
        else "(sem edições)"
    )

    # Build per-region file
    counts = {}
    for regiao, cidades in REGIOES.items():
        out_lines = [
            f"# {regiao}",
            "",
            f"**Período coberto:** {periodo}",
            "",
            f"**Cidades nesta região:** {len(cidades)} ({', '.join(cidades)})",
            "",
        ]
        total = 0
        rows = []
        for c in cidades:
            n = len(by_city[c])
            total += n
            rows.append(f"| [{c}](#{c.lower().replace(' ', '-').replace('ã','a').replace('õ','o').replace('é','e').replace('í','i').replace('ç','c').replace('á','a').replace('ú','u').replace('â','a').replace('ê','e').replace('ó','o')}) | {n} |")

        out_lines.append(f"**Total de casos na região:** {total}")
        out_lines.append("")
        out_lines.append("| Cidade | Casos |")
        out_lines.append("|--------|-------|")
        out_lines.extend(rows)
        out_lines.append("")
        out_lines.append("---")
        out_lines.append("")
        out_lines.append("> ⭐ score político ≥12 · • score 6-11 · · score <6")
        out_lines.append(">")
        out_lines.append("> **Status:**")
        out_lines.append("> 🟡 em apuração · 🟢 arquivado / recomendação cumprida · 🟠 ACNP / TAC firmado")
        out_lines.append("> 🔴 Ação Civil Pública em curso · ⚫ prescrito · ❔ indefinido")
        out_lines.append("")
        out_lines.append("---")
        out_lines.append("")

        counts[regiao] = total

        for c in cidades:
            out_lines.append(build_cidade_section(c, by_city[c]))

        out_path = out_dir / f"regiao-{regiao_slug(regiao)}.md"
        out_path.write_text("\n".join(out_lines))
        print(f"{out_path}: {total} casos ({len(cidades)} cidades)")

    return counts, by_city


if __name__ == "__main__":
    main()
