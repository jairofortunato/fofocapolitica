#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o HTML do dossiê AMREC (12 cidades) — modelo Transparência Radical.
Conteúdo dos casos = tradução curada (linguagem simples). Identidade e imagens
das cidades preenchidas por IDENTIDADE/IMGS (vindas de pesquisa web)."""
import html, os

ASSETS = "./assets"

# cor distinta por cidade
CITY_COLOR = {
    "Criciúma": "#C4161C", "Içara": "#1F7A44", "Urussanga": "#0B6E99",
    "Forquilhinha": "#B5480E", "Cocal do Sul": "#6B3FA0", "Nova Veneza": "#087A6C",
    "Siderópolis": "#8A6D0F", "Orleans": "#A61E4D", "Morro da Fumaça": "#444B54",
    "Balneário Rincão": "#0F7BA8", "Treviso": "#7A5C1E", "Lauro Müller": "#2D6A4F",
}

# Identidade (prefeito/vice/vereadores) — preenchido depois da pesquisa.
# Criciúma já conhecido.
IDENTIDADE = {
    "Criciúma":         {"prefeito": "Vagner Espíndola (Vaguinho)", "vice": "Salésio Lima",      "vereadores": 17},
    "Içara":            {"prefeito": "Dalvania Cardoso",   "vice": "Alex Michels",       "vereadores": 13},
    "Urussanga":        {"prefeito": "Stela Talamini",     "vice": "Renato Bez Fontana", "vereadores": 9},
    "Forquilhinha":     {"prefeito": "José Cláudio Gonçalves (Neguinho)", "vice": "Érico D'Amorim", "vereadores": 9},
    "Cocal do Sul":     {"prefeito": "Ademir Magagnin",    "vice": "Nega Cittadin",      "vereadores": 9},
    "Nova Veneza":      {"prefeito": "Ângela Ghislandi",   "vice": "Edésio Spilere",     "vereadores": 9},
    "Siderópolis":      {"prefeito": "Franqui Salvaro",    "vice": "Rafael Frello",      "vereadores": 9},
    "Orleans":          {"prefeito": "Fernando Cruzetta",  "vice": "Leonete Librelato",  "vereadores": 11},
    "Morro da Fumaça":  {"prefeito": "Eduardo Guollo",     "vice": "Davi Pellegrin",     "vereadores": 9},
    "Balneário Rincão": {"prefeito": "Luiz Laurindo",      "vice": "Carlito Darolt",     "vereadores": 9},
    "Treviso":          {"prefeito": "Luciano Miotelli",   "vice": "Gé Gamba",           "vereadores": 9},
    "Lauro Müller":     {"prefeito": "Valdir Fontanella",  "vice": "Serraninho",         "vereadores": 9},
}

# arquivos de imagem por cidade
_C = f"{ASSETS}/cidades"
IMGS = {
    "Criciúma":         {"bandeira": f"{_C}/criciuma-b.png",       "brasao": f"{_C}/criciuma-e.png"},
    "Içara":            {"bandeira": f"{_C}/icara-b.png",          "brasao": f"{_C}/icara-e.png"},
    "Urussanga":        {"bandeira": f"{_C}/urussanga-b.png",      "brasao": f"{_C}/urussanga-e.png"},
    "Forquilhinha":     {"bandeira": f"{_C}/forquilhinha-b.png",   "brasao": f"{_C}/forquilhinha-e.png"},
    "Cocal do Sul":     {"bandeira": f"{_C}/cocaldosul-b.png",     "brasao": f"{_C}/cocaldosul-e.png"},
    "Nova Veneza":      {"bandeira": f"{_C}/novaveneza-b.png",     "brasao": f"{_C}/novaveneza-e.jpg"},
    "Siderópolis":      {"bandeira": f"{_C}/sideropolis-b.png",    "brasao": f"{_C}/sideropolis-e.png"},
    "Orleans":          {"bandeira": f"{_C}/orleans-b.png",        "brasao": f"{_C}/orleans-e.png"},
    "Morro da Fumaça":  {"bandeira": f"{_C}/morrodafumaca-b.jpg",  "brasao": f"{_C}/morrodafumaca-e.jpg"},
    "Balneário Rincão": {"bandeira": f"{_C}/balneariorincao-b.jpg","brasao": f"{_C}/balneariorincao-e.jpg"},
    "Treviso":          {"bandeira": f"{_C}/treviso-b.png",        "brasao": f"{_C}/treviso-e.png"},
    "Lauro Müller":     {"bandeira": f"{_C}/lauromuller-b.png",    "brasao": f"{_C}/lauromuller-e.png"},
}

# Finanças 2025 (SICONFI/Tesouro) + população (Censo IBGE 2022)
FINANCAS = {
    "Criciúma":         {"pop": 214493, "rec": 1427002895, "desp": 1389857551},
    "Içara":            {"pop": 59035,  "rec": 419660467,  "desp": 393734487},
    "Urussanga":        {"pop": 20919,  "rec": 147679209,  "desp": 138481725},
    "Forquilhinha":     {"pop": 31431,  "rec": 279164047,  "desp": 250509081},
    "Cocal do Sul":     {"pop": 17240,  "rec": 139282281,  "desp": 124240370},
    "Nova Veneza":      {"pop": 13664,  "rec": 120756472,  "desp": 91634072},
    "Siderópolis":      {"pop": 13714,  "rec": 103308522,  "desp": 100994921},
    "Orleans":          {"pop": 23661,  "rec": 170915184,  "desp": 156926059},
    "Morro da Fumaça":  {"pop": 18537,  "rec": 147708369,  "desp": 122809503},
    "Balneário Rincão": {"pop": 15981,  "rec": 126625815,  "desp": 123771377},
    "Treviso":          {"pop": 3782,   "rec": 49525832,   "desp": 48495999},
    "Lauro Müller":     {"pop": 14381,  "rec": 107909673,  "desp": 101932531},
}
MES = {"JAN":1,"FEV":2,"MAR":3,"ABR":4,"MAI":5,"JUN":6,"JUL":7,"AGO":8,"SET":9,"OUT":10,"NOV":11,"DEZ":12}

def fmt_brl(v):
    if v >= 1_000_000_000: return f"R$ {v/1_000_000_000:.2f} bi".replace(".", ",")
    if v >= 1_000_000:     return f"R$ {v/1_000_000:.0f} mi"
    return f"R$ {v:,.0f}".replace(",", ".")

def fmt_pop(v):
    return f"{v:,}".replace(",", ".")

# tag -> classe css
TAGS = {
    "irregular": ("🔴 Irregularidade encontrada", "red"),
    "arquivado": ("🟢 Investigado e arquivado", "green"),
    "tce": ("⬛ TCE — decisão / multa", "tce"),
    "cautelar": ("🟠 TCE suspendeu (cautelar)", "amber"),
    "acordo": ("🟠 Irregularidade + acordo de devolução", "amber"),
}

# ---- CONTEÚDO CURADO (linguagem simples) ----
# cada caso: (ano, dia-mês, tag, título, [(rótulo, texto)...], "ref")
CIDADES = {
 "Criciúma": [
   ("2024","30 JUL","tce","Prefeitura julgada irregular pelo TCE",
     [("O que aconteceu","O Tribunal de Contas julgou IRREGULAR uma tomada de contas da Prefeitura de Criciúma e aplicou multa."),
      ("Quem","Entre os responsáveis, o ex-prefeito Clésio Salvaro."),
      ("Em que pé está","Já tem decisão do TCE, com multa aplicada.")], "TCE 23/80030191"),
   ("2025","13 JAN","tce","Contas do prefeito de 2023 com parecer pela REJEIÇÃO",
     [("O que aconteceu","O TCE analisou as contas de 2023 do prefeito e emitiu parecer pela REJEIÇÃO — o passo antes de a Câmara julgar."),
      ("Valores apontados","Mais de R$ 1,9 milhão em apontamentos."),
      ("Em que pé está","Parecer prévio emitido; vai à Câmara de Vereadores.")], "PCP 24/00388860"),
   ("2025","07 AGO","tce","R$ 5,1 milhões investidos sob suspeita no fundo dos servidores",
     [("O que aconteceu","Inspeção do TCE apontou irregularidade nos investimentos do CriciúmaPrev (fundo de aposentadoria dos servidores) entre 2020 e 2024, com multa."),
      ("Quem","Dirigentes do instituto e a consultoria financeira contratada."),
      ("Em que pé está","Multa aplicada.")], "RLI 24/80048912"),
 ],
 "Içara": [
   ("2026","31 MAR","tce","Prefeitura multada por acordo judicial sem lei que autorizasse",
     [("O que aconteceu","O TCE apontou irregularidade e multou por um acordo judicial firmado pela Prefeitura de Içara sem lei que o autorizasse."),
      ("Valor","Cerca de R$ 378 mil."),
      ("Em que pé está","Multa aplicada.")], "REP 22/80094562"),
   ("2025","16 JUL","tce","Câmara de Vereadores de Içara multada",
     [("O que aconteceu","Auditoria do controle interno achou irregularidades na Câmara de Içara; o TCE aplicou multas."),
      ("Quem","Ex-dirigentes da Câmara."),
      ("Em que pé está","Multa aplicada.")], "REP 20/00498951"),
   ("2025","07 ABR","irregular","Suspeita de irregularidade em pregão de 2025",
     [("O que aconteceu","O TCE apontou possíveis irregularidades no Pregão Eletrônico 16/2025 da Prefeitura de Içara."),
      ("Em que pé está","Irregularidade apontada; em análise.")], "REP 25/00058594"),
 ],
 "Urussanga": [
   ("2023","11 DEZ","tce","Contas do prefeito rejeitadas — dois anos seguidos",
     [("O que aconteceu","O TCE emitiu parecer pela REJEIÇÃO das contas do prefeito de Urussanga referentes a 2021 e a 2022."),
      ("Em que pé está","Pareceres pela rejeição; vão à Câmara.")], "PCP 22/00103748 e 23/00233635"),
   ("2025","04 AGO","irregular","Pregão de R$ 2,5 milhões sob suspeita",
     [("O que aconteceu","O TCE apontou possíveis irregularidades no Pregão Eletrônico 27/2025 da Prefeitura de Urussanga."),
      ("Valor","Cerca de R$ 2,5 milhões."),
      ("Em que pé está","Irregularidade apontada.")], "REP 25/00140924"),
   ("2026","19 JAN","irregular","MP investigou falhas em concurso público",
     [("O que aconteceu","O MP apurou falhas na aplicação das provas do concurso 01/2023 (candidatos liberados sem lacre, início antecipado em uma sala)."),
      ("Em que pé está","Falhas formais; sem prejuízo comprovado à lisura.")], "IC 06.2024.00003519-0"),
 ],
 "Forquilhinha": [
   ("2024","19 NOV","tce","Contrato de advogados de até R$ 33 milhões (royalties) questionado",
     [("O que aconteceu","O TCE analisou a contratação direta (sem licitação) de serviços advocatícios ligados a royalties, com valores que chegam a R$ 33 milhões."),
      ("Em que pé está","Irregularidade apontada; em fase de recurso.")], "REC 24/00582240"),
   ("2022","25 JAN","tce","Pregão julgado irregular + multa",
     [("O que aconteceu","O TCE julgou irregular o Pregão 13/2021 da Prefeitura de Forquilhinha e aplicou multa."),
      ("Em que pé está","Decisão com multa.")], "REP 21/00102235"),
   ("2024","02 ABR","irregular","Agentes sanitários contratados sem concurso",
     [("O que aconteceu","O MP apurou aumento de carga horária e contratação de agentes sanitários sem concurso, com base em norma considerada inconstitucional."),
      ("Em que pé está","Ação judicial em curso para regularizar.")], "NF 01.2023.00048356-6"),
 ],
 "Cocal do Sul": [
   ("2025","07 AGO","tce","Suspeita de superfaturamento na compra de terreno da área industrial",
     [("O que aconteceu","O TCE apontou possível superfaturamento na compra de um terreno para a 5ª área industrial do município."),
      ("Valor","R$ 2,6 milhões."),
      ("Em que pé está","Decisão singular; irregularidade em análise.")], "REP 24/00605550"),
   ("2025","16 OUT","irregular","Denúncia sobre professores temporários demais",
     [("O que aconteceu","O TCE apurou desproporção entre professores temporários e efetivos na rede municipal."),
      ("Em que pé está","Irregularidade apontada.")], "DEN 24/80074247"),
   ("2026","14 JAN","irregular","MP investigou a desapropriação da área industrial",
     [("O que aconteceu","O MP apurou suposto sobrepreço na desapropriação de imóveis para a 5ª área industrial."),
      ("Em que pé está","Investigação concluída; escolha da área tida como legal.")], "IC 06.2025.00000358-0"),
 ],
 "Nova Veneza": [
   ("2026","27 JAN","acordo","Cestas de Natal dos servidores compradas de forma irregular",
     [("O que aconteceu","O MP concluiu que houve improbidade na compra de cestas natalinas para servidores em 2021."),
      ("Quem","Isauro Kirchner."),
      ("Em que pé está","Irregularidade confirmada; firmado acordo de devolução (ANPC).")], "IC 06.2022.00001845-0"),
   ("2023","31 AGO","irregular","Fábrica de adubos sob suspeita de contaminar rios",
     [("O que aconteceu","O MP investigou a indústria de adubos NIORG por possível contaminação de cursos d'água na cidade."),
      ("Em que pé está","Ação civil em curso.")], "IC 06.2023.00001462-5"),
 ],
 "Siderópolis": [
   ("2024","17 MAI","tce","Prefeitura julgada irregular + multa",
     [("O que aconteceu","O TCE julgou irregular a falta de informações obrigatórias no Portal e aplicou multa à Prefeitura de Siderópolis."),
      ("Em que pé está","Decisão com multa.")], "RLI 22/00654620"),
   ("2026","16 JAN","irregular","MP questiona convênio da prefeitura com a UNESC",
     [("O que aconteceu","O MP apontou ilegalidade num convênio entre o município e a UNESC, com indícios de desvio do objeto e subcontratação irregular."),
      ("Em que pé está","Ação civil ajuizada.")], "IC 06.2024.00004820-8"),
 ],
 "Orleans": [
   ("2023","04 MAI","tce","Prefeitura julgada irregular + multa (tomada de contas)",
     [("O que aconteceu","O TCE julgou irregular uma tomada de contas da Prefeitura de Orleans e aplicou multa."),
      ("Quem","Vários responsáveis nominados no acórdão."),
      ("Em que pé está","Decisão com multa.")], "TCE 15/00537036"),
   ("2022","02 MAI","tce","Contratação de fundação julgada irregular + multa",
     [("O que aconteceu","O TCE julgou irregular a contratação de uma fundação de apoio ao ensino e aplicou multa."),
      ("Valor","Contrato de R$ 683 mil."),
      ("Em que pé está","Decisão com multa.")], "REP 20/00217960"),
   ("2025","28 NOV","acordo","Servidor usou carro oficial e se acidentou — devolveu o dano",
     [("O que aconteceu","O MP apurou uso indevido de veículo oficial, com acidente e indícios de embriaguez."),
      ("Em que pé está","Servidor punido e ressarciu integralmente o dano ao município.")], "IC 06.2021.00004267-9"),
 ],
 "Morro da Fumaça": [
   ("2026","02 FEV","cautelar","TCE suspendeu pregão de software da Saúde",
     [("O que aconteceu","O TCE viu possíveis irregularidades e suspendeu (cautelar) o Pregão 9/2025 do Fundo Municipal de Saúde."),
      ("Valor","R$ 345 mil."),
      ("Em que pé está","Pregão suspenso enquanto o TCE analisa.")], "REP 26/00007444"),
   ("2024","12 NOV","irregular","Contratação sem licitação sob suspeita",
     [("O que aconteceu","O TCE apontou irregularidade numa inexigibilidade de licitação (contrato de serviços) da prefeitura."),
      ("Em que pé está","Irregularidade apontada.")], "LCC 24/00578138"),
   ("2025","15 MAI","arquivado","MP questionou contratação de leilão online e prefeitura corrigiu",
     [("O que aconteceu","O MP apurou a contratação de uma plataforma de leilão em desacordo com a lei."),
      ("Em que pé está","Prefeitura acatou a recomendação e corrigiu. Arquivado.")], "IC 06.2024.00001605-0"),
 ],
 "Balneário Rincão": [
   ("2025","19 MAI","tce","Prefeitura julgada irregular + multa por permuta de imóveis",
     [("O que aconteceu","O TCE julgou irregular uma permuta (troca) de imóveis do município e aplicou multa."),
      ("Em que pé está","Decisão com multa.")], "DEN 23/80021958"),
   ("2025","12 AGO","irregular","Denúncia sobre a folha de pagamento dos vereadores",
     [("O que aconteceu","O TCE apurou possíveis irregularidades na folha de pagamento dos vereadores da Câmara."),
      ("Em que pé está","Irregularidade apontada.")], "DEN 25/00095872"),
   ("2023","05 MAI","acordo","Câmara contratou sem concurso e assinou acordo",
     [("O que aconteceu","O MP apurou contratação de servidores pela Câmara sem concurso público."),
      ("Em que pé está","Firmado acordo (TAC) para corrigir.")], "IC 06.2019.00005890-1"),
 ],
 "Treviso": [
   ("2025","25 FEV","acordo","Superfaturamento na reforma da Câmara — confirmado",
     [("O que aconteceu","O MP concluiu que houve improbidade e prejuízo público em superfaturamento na reforma da sede da Câmara de Treviso."),
      ("Quem","Sidnei Viola e a construtora contratada."),
      ("Em que pé está","Irregularidade confirmada; acordo de devolução (ANPC).")], "IC 06.2018.00005772-0"),
   ("2022","21 JUL","tce","Prefeitura multada pelo TCE",
     [("O que aconteceu","O TCE apontou irregularidades e aplicou multa envolvendo a Prefeitura de Treviso."),
      ("Valor","Apontamentos de R$ 243 mil."),
      ("Em que pé está","Multa aplicada.")], "REP 19/00389859"),
   ("2022","25 JUL","acordo","Nepotismo na prefeitura — recomendação acatada",
     [("O que aconteceu","O MP apurou nepotismo no município e recomendou exonerar contratados sem concurso."),
      ("Em que pé está","Recomendação acatada pelo prefeito.")], "IC 06.2017.00005247-6"),
 ],
 "Lauro Müller": [
   ("2022","16 AGO","tce","Prefeitura julgada irregular + multa",
     [("O que aconteceu","O TCE manteve, em recurso, decisão que julgou irregular e aplicou multa envolvendo a Prefeitura de Lauro Müller."),
      ("Em que pé está","Decisão com multa.")], "REC 20/00161809"),
   ("2022","04 AGO","irregular","Água imprópria distribuída por sistema paralelo à CASAN",
     [("O que aconteceu","O MP apurou distribuição de água não tratada por um sistema paralelo ao da CASAN em três bairros."),
      ("Em que pé está","Ação civil ajuizada.")], "IC 06.2019.00004983-5"),
   ("2022","01 ABR","cautelar","TCE suspendeu pregão de R$ 787 mil",
     [("O que aconteceu","O TCE viu possíveis irregularidades e suspendeu (cautelar) o Pregão 44/2022 da prefeitura."),
      ("Valor","R$ 787 mil."),
      ("Em que pé está","Pregão suspenso para análise.")], "PAP 22/80014801"),
 ],
}

ORDEM = ["Criciúma","Içara","Urussanga","Forquilhinha","Cocal do Sul","Nova Veneza",
         "Siderópolis","Orleans","Morro da Fumaça","Balneário Rincão","Treviso","Lauro Müller"]

def esc(s): return html.escape(str(s))

def city_section(city):
    color = CITY_COLOR[city]
    fin = FINANCAS.get(city, {})
    imgs = IMGS.get(city, {})
    flag = imgs.get("bandeira"); bras = imgs.get("brasao")
    flag_html = f'<img class="c-flag" src="{flag}" alt="">' if flag else '<div class="c-flag c-flag-ph"></div>'
    bras_html = f'<img class="c-bras" src="{bras}" alt="">' if bras else ''

    # casos ordenados do mais recente para o mais antigo
    cases = sorted(CIDADES[city], key=lambda c: (int(c[0]), MES.get(c[1].split()[1], 0), int(c[1].split()[0])), reverse=True)
    cards = []
    for (yr, dm, tag, title, rows, ref) in cases:
        label, cls = TAGS[tag]
        rows_html = "".join(
            f'<div class="rowline"><div class="k">{esc(k)}</div><div class="v">{esc(v)}</div></div>'
            for k, v in rows)
        arq = " arq" if tag == "arquivado" else ""
        cards.append(f'''
      <div class="case{arq}">
        <div class="rail" style="--rc:{color}"><div class="yr">{yr}</div><div class="dm">{dm}</div></div>
        <div class="body">
          <span class="pill {cls}">{esc(label)}</span>
          <h3>{esc(title)}</h3>
          {rows_html}
          <div class="ref">{esc(ref)}</div>
        </div>
      </div>''')

    info = f'''
      <div class="cinfo">
        <div class="ci"><span class="cl">População</span><b>{fmt_pop(fin.get("pop",0))}</b><span class="cu">habitantes (Censo 2022)</span></div>
        <div class="ci"><span class="cl">Arrecadou em 2025</span><b>{fmt_brl(fin.get("rec",0))}</b><span class="cu">receita realizada</span></div>
        <div class="ci"><span class="cl">Gastou em 2025</span><b>{fmt_brl(fin.get("desp",0))}</b><span class="cu">despesa empenhada</span></div>
      </div>''' if fin else ''

    return f'''
  <section class="page" style="--city:{color}">
    <div class="pad">
      <div class="cityhead">
        <div class="h-t">
          <div class="small">Região Carbonífera · AMREC</div>
          <div class="big">{esc(city)}</div>
        </div>
        <img class="h-logo" src="{ASSETS}/logo-preto.png" alt="JAIRO">
      </div>
      <div class="csymbols">
        {flag_html}
        {bras_html}
        {info}
      </div>
      {''.join(cards)}
    </div>
  </section>'''

# CSS reaproveitado do modelo + estilos compactos por cidade
CSS = open(os.path.join(os.path.dirname(__file__), "amrec_css.css")).read()

def build():
    cover = open(os.path.join(os.path.dirname(__file__), "amrec_cover.html")).read()
    body = "\n".join(city_section(c) for c in ORDEM)
    cta = open(os.path.join(os.path.dirname(__file__), "amrec_cta.html")).read()
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>{cover}{body}{cta}</body></html>"""

if __name__ == "__main__":
    out = build()
    open(os.path.join(os.path.dirname(__file__), "amrec.html"), "w").write(out)
    print("amrec.html gerado:", len(out), "bytes ·", len(ORDEM), "cidades")
