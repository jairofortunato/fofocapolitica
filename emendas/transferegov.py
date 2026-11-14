#!/usr/bin/env python3
"""Lado federal das emendas Pix (transferências especiais) de um parlamentar.

Para cada plano de ação no Transferegov junta: objeto e executor, metas, empenho,
documento hábil, ordem bancária (data em que o dinheiro saiu) e relatórios de gestão
(quanto o município declarou como executado).

Uso:
  python3 -I emendas/transferegov.py "Daniel Freitas"
  python3 -I emendas/transferegov.py "Daniel Freitas" --beneficiario CRICIUMA

Saída: emendas/dados/<parlamentar>/planos.json e resumo.csv
API: https://api.transferegov.gestao.gov.br/transferenciasespeciais (PostgREST, aberta)
"""
import argparse
import csv
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.transferegov.gestao.gov.br/transferenciasespeciais"
RAIZ = Path(__file__).resolve().parent


def get(tabela, **filtros):
    q = urllib.parse.urlencode(filtros)
    for i in range(4):
        try:
            req = urllib.request.Request(f"{API}/{tabela}?{q}", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read())
        except Exception:
            if i == 3:
                raise
            time.sleep(3 * (i + 1))


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


EMPRESA = re.compile(r"(?i)(?:empresa\s+(?:contratada|vencedora)[^:]{0,40}:?|contratad[ao]\s*:)\s*([A-ZÀ-Ú0-9][A-ZÀ-Ú0-9 .&\-/]{3,80}?(?:LTDA|EIRELI|S\.?A\.?|ME|EPP)\b)")


def empresas(relatorios):
    vistos = []
    for r in relatorios:
        for m in EMPRESA.finditer(r.get("parecer_relatorio_gestao") or ""):
            e = re.sub(r"\s+", " ", m.group(1)).strip().upper()
            if e not in vistos:
                vistos.append(e)
    return vistos


def detalha(p):
    pid = p["id_plano_acao"]
    p["executores"] = get("executor_especial", id_plano_acao=f"eq.{pid}")
    for ex in p["executores"]:
        ex["metas"] = get("meta_especial", id_executor=f"eq.{ex['id_executor']}")
    p["plano_trabalho"] = get("plano_trabalho_especial", id_plano_acao=f"eq.{pid}")
    p["empenhos"] = get("empenho_especial", id_plano_acao=f"eq.{pid}")
    p["pagamentos"] = []
    for e in p["empenhos"]:
        for dh in get("documento_habil_especial", id_empenho=f"eq.{e['id_empenho']}"):
            obs = get("ordem_pagamento_ordem_bancaria_especial", id_dh=f"eq.{dh['id_dh']}")
            for ob in obs or [{}]:
                p["pagamentos"].append({"empenho": e["numero_empenho"], "dh": dh["numero_documento_habil"],
                                        "valor": dh["valor_dh"], "ob": ob.get("numero_ordem_bancaria"),
                                        "data_ob": ob.get("data_emissao_ob"), "situacao": ob.get("descricao_situacao_op")})
    p["relatorios"] = (get("relatorio_gestao_novo_especial", id_plano_acao=f"eq.{pid}")
                       + get("relatorio_gestao_especial", id_plano_acao=f"eq.{pid}"))
    return p


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("parlamentar")
    ap.add_argument("--beneficiario", help="filtra pelo nome do beneficiário (ex.: CRICIUMA)")
    ap.add_argument("--cache", action="store_true", help="reusa planos.json já baixado (só refaz o CSV)")
    a = ap.parse_args()

    out = RAIZ / "dados" / slug(a.parlamentar)
    if a.cache and (out / "planos.json").exists():
        planos = json.loads((out / "planos.json").read_text(encoding="utf-8"))
    else:
        planos = get("plano_acao_especial", nome_parlamentar_emenda_plano_acao=f"ilike.*{a.parlamentar}*",
                     order="ano_plano_acao.desc")
        if a.beneficiario:
            planos = [p for p in planos if a.beneficiario.upper() in p["nome_beneficiario_plano_acao"].upper()]
        print(f"{len(planos)} planos de ação")
        for i, p in enumerate(planos, 1):
            detalha(p)
            print(f"  {i:>3}/{len(planos)} {p['ano_plano_acao']} {p['numero_emenda_parlamentar_plano_acao']} "
                  f"{p['nome_beneficiario_plano_acao'][:40]}")

    out.mkdir(parents=True, exist_ok=True)
    (out / "planos.json").write_text(json.dumps(planos, ensure_ascii=False, indent=1), encoding="utf-8")

    with open(out / "resumo.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ano", "emenda", "plano", "beneficiario", "uf", "valor", "situacao_plano", "area",
                    "objeto", "n_metas", "data_pagamento", "valor_pago_uniao", "situacao_pt",
                    "fim_execucao", "ultimo_relatorio", "tipo_relatorio", "executado_declarado",
                    "pendente_declarado", "n_relatorios_antigos", "empresas_citadas", "relatorio_antigo"])
        for p in planos:
            valor = (p["valor_custeio_plano_acao"] or 0) + (p["valor_investimento_plano_acao"] or 0)
            objeto = " | ".join(re.sub(r"\s+", " ", ex.get("objeto_executor") or "").strip() for ex in p["executores"])
            pt = (p["plano_trabalho"] or [{}])[0]
            pags = [x for x in p["pagamentos"] if x.get("data_ob")]
            antigos = [x for x in p["relatorios"] if "id_relatorio_gestao" in x]
            texto_antigo = re.sub(r"\s+", " ", max((x.get("parecer_relatorio_gestao") or "" for x in antigos), key=len, default=""))
            rels = sorted([x for x in p["relatorios"] if "id_relatorio_gestao_novo" in x],
                          key=lambda r: r.get("data_e_hora_relatorio_gestao_novo") or "")
            r = rels[-1] if rels else {}
            w.writerow([p["ano_plano_acao"], p["numero_emenda_parlamentar_plano_acao"], p["codigo_plano_acao"],
                        p["nome_beneficiario_plano_acao"], p["uf_beneficiario_plano_acao"], valor,
                        p["situacao_plano_acao"], p["codigo_descricao_areas_politicas_publicas_plano_acao"],
                        objeto[:1000], sum(len(ex["metas"]) for ex in p["executores"]),
                        ";".join(sorted({x["data_ob"] for x in pags})), sum(x["valor"] or 0 for x in pags),
                        pt.get("situacao_plano_trabalho"), (pt.get("data_fim_execucao_plano_trabalho") or "")[:10],
                        (r.get("data_e_hora_relatorio_gestao_novo") or "")[:10], r.get("tipo_relatorio_gestao_novo"),
                        r.get("valor_executado_relatorio_gestao_novo"), r.get("valor_pendente_relatorio_gestao_novo"),
                        len(antigos), "; ".join(empresas(antigos)), texto_antigo[:1500]])
    print(f"Saída: {out}/resumo.csv")


if __name__ == "__main__":
    sys.exit(main())
