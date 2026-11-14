#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Briefing de preparação para a entrevista na Rádio Fundação Marconi (Urussanga).

Documento INTERNO: não leva número de urna nem faixa de propaganda eleitoral,
porque não é peça de campanha — é material de estudo. Os casos vêm da curadoria
já publicada da AMREC (pdf_template/amrec/_curated_data/curated/).
"""
import html as H
import json
import os
import subprocess
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
AMREC = os.path.join(HERE, "amrec")
CUR = os.path.join(AMREC, "_curated_data", "curated")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def esc(s):
    return H.escape(str(s))


def casos(slug):
    d = json.load(open(os.path.join(CUR, f"{slug}.json")))
    mp = [x for x in d["mp"] if x.get("keep")]
    tce = [x for x in d["tce"] if x.get("keep")]
    return d, mp, tce


FIN = json.load(open(os.path.join(AMREC, "financas.json")))

# População do Censo 2010 (IBGE, agregado 1378) — para a taxa de crescimento.
POP2010 = {"Urussanga": 20223, "Orleans": 21393, "Cocal do Sul": 15159,
           "Criciúma": 192308}
# PIB municipal 2023 a preços correntes (IBGE, agregado 5938), em mil reais.
PIB2023 = {"Urussanga": 1222447, "Orleans": 1408944, "Cocal do Sul": 1084930,
           "Criciúma": 12339548}

SLUG = {"Urussanga": "urussanga", "Orleans": "orleans", "Cocal do Sul": "cocal_do_sul"}


def brl(v, casas=0):
    s = f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def milhoes(v):
    return f"R$ {brl(v/1_000_000, 1)} mi"


# ---------------------------------------------------------------- ranking
def ranking():
    linhas = []
    for fn in os.listdir(CUR):
        slug = fn.replace(".json", "")
        d, mp, tce = casos(slug)
        gr = sum(1 for x in mp + tce if x.get("severity") == "alta")
        nome = next((k for k in FIN if isinstance(FIN[k], dict)
                     and _slug(k) == slug), slug)
        pop = FIN.get(nome, {}).get("pop_ibge") or FIN.get(nome, {}).get("populacao")
        if not pop:
            continue
        linhas.append((nome, pop, len(mp) + len(tce), gr, gr / pop * 10000))
    return sorted(linhas, key=lambda r: -r[4])


def _slug(city):
    import re
    import unicodedata
    s = unicodedata.normalize("NFKD", city).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


# ---------------------------------------------------------------- blocos
def card(x, fonte):
    """O selo de gravidade e o selo de desfecho são coisas diferentes: um caso
    grave que já foi arquivado precisa mostrar as duas informações, senão o
    briefing sugere culpa onde o processo terminou sem responsabilizar ninguém."""
    sev = x.get("severity") == "alta"
    tag = '<span class="selo grave">caso grave</span>' if sev else ""
    if x.get("status"):
        tag += f'<span class="selo">{esc(x["status"])}</span>'
    return (f'<div class="caso{" g" if sev else ""}">'
            f'<div class="ct">{tag}<span class="org">{fonte}</span></div>'
            f'<h4>{esc(x["title"])}</h4>'
            f'<p>{esc(x["description"])}</p>'
            f'<div class="ref">Processo nº {esc(x.get("ref",""))} · confira na fonte antes de citar no ar</div>'
            f'</div>')


def bloco_cidade(nome, texto_analise, destaque_ids=None, max_media=0):
    slug = SLUG[nome]
    d, mp, tce = casos(slug)
    f = FIN[nome]
    pop = f.get("pop_ibge") or f["populacao"]
    p10 = POP2010.get(nome)
    pib = PIB2023.get(nome, 0) * 1000
    gr_mp = [x for x in mp if x.get("severity") == "alta"]
    gr_tce = [x for x in tce if x.get("severity") == "alta"]
    graves = gr_mp + gr_tce
    cresc = (pop / p10 - 1) * 100 if p10 else None

    nums = [
        ("População (Censo 2022)", brl(pop)),
        ("Crescimento 2010→2022",
         (f"{cresc:+.1f}%".replace(".", ",")) if cresc is not None else "—"),
        ("PIB 2023", f"R$ {brl(pib/1_000_000_000, 3)} bi"),
        ("PIB por habitante", f"R$ {brl(pib/pop)}"),
        ("Receita líquida 2025", milhoes(f["receita_liquida"])),
        ("Despesa 2025", milhoes(f["despesa"])),
        ("Receita por habitante", f"R$ {brl(f['receita_liquida']/pop)}"),
        ("Casos levantados", f"{len(d['mp'])+len(d['tce'])} brutos · {len(mp)+len(tce)} publicáveis"),
        ("Casos graves", f"{len(graves)}"),
        ("Graves por 10 mil hab.", f"{len(graves)/pop*10000:.1f}"),
    ]
    grid = "".join(f'<div class="n"><span class="nl">{esc(l)}</span>'
                   f'<span class="nv">{esc(v)}</span></div>' for l, v in nums)

    cards = "".join(card(x, "MP") for x in gr_mp) + "".join(card(x, "TCE") for x in gr_tce)
    extras = ""
    if max_media:
        md = [x for x in mp if x.get("severity") != "alta"][:max_media]
        if md:
            extras = ('<h3 class="sub">Outros casos que dão pano para manga</h3>'
                      '<ul class="lista">'
                      + "".join(f"<li>{esc(x['title'])}</li>" for x in md)
                      + "</ul>")

    return (f'<section class="page"><h2>{esc(nome)}</h2>'
            f'<div class="grid">{grid}</div>'
            f'<div class="analise">{texto_analise}</div>'
            f'<h3 class="sub">Casos graves — {len(graves)}</h3>{cards}{extras}</section>')


CSS = """
@font-face{font-family:'Anton';src:url('./assets/anton.woff2') format('woff2');font-weight:400}
@font-face{font-family:'Archivo';src:url('./assets/archivo-400.woff2') format('woff2');font-weight:400}
@font-face{font-family:'Archivo';src:url('./assets/archivo-700.woff2') format('woff2');font-weight:700}
@font-face{font-family:'Archivo';src:url('./assets/archivo-800.woff2') format('woff2');font-weight:800}
:root{--gold:#FDBD27;--ink:#111;--red:#C4161C;--muted:#6b6b6b;--line:#e2e2e2;--bg:#f7f7f5}
*{margin:0;padding:0;box-sizing:border-box}
@page{size:A4;margin:15mm 14mm 16mm}
html,body{font-family:'Archivo',sans-serif;color:var(--ink);font-size:9.6pt;line-height:1.45;
  -webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{page-break-before:always}
.page:first-child{page-break-before:auto}
h1{font-family:'Anton';font-size:33pt;line-height:.98;text-transform:uppercase;letter-spacing:.3px}
h2{font-family:'Anton';font-size:19pt;text-transform:uppercase;letter-spacing:.4px;
  border-bottom:3px solid var(--gold);padding-bottom:4px;margin-bottom:11px}
h3.sub{font-family:'Archivo';font-weight:800;font-size:10.5pt;text-transform:uppercase;
  letter-spacing:.6px;color:var(--red);margin:15px 0 7px}
h4{font-size:10.4pt;font-weight:800;line-height:1.25;margin-bottom:3px}
p{margin-bottom:6px}
.cover{height:262mm;display:flex;flex-direction:column;justify-content:space-between}
.eyebrow{font-weight:800;font-size:8.5pt;letter-spacing:2.5px;text-transform:uppercase;color:var(--red)}
.cover .meta{font-size:10pt;border-top:3px solid var(--ink);padding-top:9px}
.cover .meta b{font-weight:800}
.warn{background:#fff6d9;border-left:5px solid var(--gold);padding:9px 12px;margin:9px 0;font-size:9.2pt}
.warn b{font-weight:800}
.danger{background:#fdeceb;border-left:5px solid var(--red);padding:9px 12px;margin:9px 0;font-size:9.2pt}
.grid{display:grid;grid-template-columns:repeat(5,1fr);gap:5px;margin-bottom:11px}
.n{background:var(--bg);border-top:2px solid var(--ink);padding:6px 7px}
.nl{display:block;font-size:6.9pt;text-transform:uppercase;letter-spacing:.4px;color:var(--muted);
  font-weight:700;line-height:1.2;min-height:17px}
.nv{display:block;font-family:'Anton';font-size:12.5pt;line-height:1.1;margin-top:2px}
.analise{font-size:9.5pt;margin-bottom:4px}
.analise p{margin-bottom:6px}
.caso{border-left:3px solid var(--line);padding:0 0 0 9px;margin-bottom:9px;break-inside:avoid}
.caso.g{border-left-color:var(--red)}
.ct{display:flex;gap:6px;align-items:center;margin-bottom:2px}
.selo{font-size:7pt;font-weight:800;text-transform:uppercase;letter-spacing:.5px;
  background:#eee;padding:1.5px 6px;border-radius:9px}
.selo.grave{background:var(--red);color:#fff}
.org{font-size:7pt;font-weight:800;color:var(--muted);letter-spacing:1px}
.caso p{font-size:9pt;margin-bottom:2px}
.ref{font-size:7.2pt;color:var(--muted)}
.lista{margin:0 0 6px 15px;font-size:9pt}
.lista li{margin-bottom:2.5px}
table{width:100%;border-collapse:collapse;font-size:8.6pt;margin-bottom:10px}
th{background:var(--ink);color:#fff;text-align:left;padding:5px 6px;font-size:7.6pt;
  text-transform:uppercase;letter-spacing:.5px}
td{padding:4px 6px;border-bottom:1px solid var(--line)}
tr.hi td{background:#fff6d9;font-weight:800}
td.num,th.num{text-align:right}
.qa{border-top:2px solid var(--ink);padding-top:7px;margin-bottom:11px;break-inside:avoid}
.qa .q{font-weight:800;font-size:10pt;margin-bottom:3px}
.qa .a{font-size:9.3pt}
.qa .a b{font-weight:800}
.pocket{display:grid;grid-template-columns:1fr 1fr;gap:6px}
.pk{background:var(--bg);padding:7px 9px;border-left:3px solid var(--gold);font-size:9pt}
.pk b{font-family:'Anton';font-size:11.5pt;display:block;line-height:1.15}
.foot{margin-top:12px;padding-top:7px;border-top:1px solid var(--line);
  font-size:7.6pt;color:var(--muted)}
"""


def tabela_ranking():
    rows = ranking()
    body = ""
    for nome, pop, pub, gr, per in rows:
        hi = ' class="hi"' if nome in SLUG else ""
        body += (f'<tr{hi}><td>{esc(nome)}</td><td class="num">{brl(pop)}</td>'
                 f'<td class="num">{pub}</td><td class="num">{gr}</td>'
                 f'<td class="num">{per:.1f}</td></tr>')
    return ('<table><tr><th>Município</th><th class="num">População</th>'
            '<th class="num">Casos publicáveis</th><th class="num">Graves</th>'
            '<th class="num">Graves / 10 mil hab.</th></tr>' + body + '</table>')


def tabela_financas():
    body = ""
    tp = tr = td = 0
    linhas = []
    for k, v in FIN.items():
        if not isinstance(v, dict) or "receita_liquida" not in v:
            continue
        pop = v.get("pop_ibge") or v["populacao"]
        linhas.append((k, pop, v["receita_liquida"], v["despesa"]))
    for k, pop, rl, de in sorted(linhas, key=lambda r: -r[1]):
        hi = ' class="hi"' if k in SLUG else ""
        body += (f'<tr{hi}><td>{esc(k)}</td><td class="num">{brl(pop)}</td>'
                 f'<td class="num">{brl(rl/1e6,1)}</td><td class="num">{brl(de/1e6,1)}</td>'
                 f'<td class="num">{brl(rl/pop)}</td></tr>')
        tp += pop; tr += rl; td += de
    body += (f'<tr style="border-top:2px solid #111"><td><b>TOTAL AMREC</b></td>'
             f'<td class="num"><b>{brl(tp)}</b></td><td class="num"><b>{brl(tr/1e6,1)}</b></td>'
             f'<td class="num"><b>{brl(td/1e6,1)}</b></td><td class="num"><b>{brl(tr/tp)}</b></td></tr>')
    return ('<table><tr><th>Município</th><th class="num">População</th>'
            '<th class="num">Receita líq. (R$ mi)</th><th class="num">Despesa (R$ mi)</th>'
            '<th class="num">Receita / hab.</th></tr>' + body + '</table>')


ANALISE_URUSSANGA = """
<p><b>A cidade que não cresce.</b> Urussanga tinha 20.223 habitantes em 2010 e
20.919 em 2022: <b>3,4% em doze anos</b>. No mesmo período Cocal do Sul cresceu
13,7% e Orleans, 10,6%. Não é uma cidade pobre — o PIB por habitante é de
R$ 58,4 mil, na média da região — é uma cidade que segura o tamanho. Esse é o
dado que abre conversa com qualquer ouvinte: quem sai, por que sai, e o que
faria voltar.</p>
<p><b>O tema que a própria cidade já conhece: transparência.</b> O Tribunal de
Contas multou gestores de Urussanga <b>cinco vezes</b> em processos ligados ao
portal da transparência e às parcerias com Organizações da Sociedade Civil. A
multa mais recente, de R$ 2.866,70, é da prefeita Stela Maris de Agostin
Talamini, por descumprir sem justificativa uma determinação anterior do próprio
tribunal. Antes dela, o então prefeito Luis Gustavo Cancellier levou multa de
R$ 1.990,60 no mesmo assunto. É o único município dos três em que a falta de
transparência virou multa reincidente — e é o assunto em que o seu trabalho
encaixa sem forçar.</p>
<p><b>O passivo do carvão continua aberto.</b> Uma condenação de <b>1991</b>
obriga a Indústria de Coque Rio Deserto, a UM Urussanga Minérios e a massa
falida da Minérios Coque a recuperar áreas degradadas — e o Ministério Público
ainda fiscaliza o cumprimento hoje, em 2025/2026. Trinta e cinco anos depois.</p>
<p><b>Meio ambiente é o volume.</b> A maior parte dos casos de Urussanga é
ambiental: desmatamento de Mata Atlântica, intervenção em área de preservação,
aterro irregular, poluição sonora de fábricas. Vários terminaram em acordo com
recuperação da área — o que é uma boa notícia e vale dizer assim.</p>
<p><b>Cuidado com o mapa.</b> A promotoria de Urussanga cobre também municípios
vizinhos: há casos de Cocal do Sul e de Morro da Fumaça dentro do levantamento
de Urussanga. Antes de atribuir um caso à cidade no ar, confira de que município
ele é.</p>
"""

ANALISE_ORLEANS = """
<p><b>A maior das três e a que mais tem dinheiro.</b> Orleans tem 23.661
habitantes, receita líquida de R$ 170,9 milhões e o segundo maior PIB do trio
(R$ 1,41 bilhão). Cresceu 10,6% entre 2010 e 2022.</p>
<p><b>Aqui o Tribunal de Contas não parou na multa: mandou devolver dinheiro.</b>
São dois casos de condenação a ressarcimento — o ex-prefeito Marco Bertoncini
Cascaes, o ex-secretário de Infraestrutura Udir Luiz Pavei e uma empresa foram
condenados solidariamente a devolver R$ 8.890 por mata-burros pagos e não
entregues; e um ex-coordenador de gestão de pessoas foi condenado a devolver
R$ 107.168,72 pagos a mais na folha. Isso é diferente de multa: é dinheiro
público que o tribunal mandou voltar ao caixa.</p>
<p><b>O caso da fundação de ensino.</b> Um contrato de R$ 683 mil com uma
fundação de apoio ao ensino foi julgado irregular pelo Tribunal de Contas e
gerou <b>duas ações civis públicas</b> do Ministério Público contra o município
no mesmo dia. É o maior valor em disputa entre os três municípios.</p>
<p><b>Compra de votos em 2024.</b> Há investigação do Ministério Público
Eleitoral sobre captação ilícita de sufrágio envolvendo uma candidata a
vereadora nas municipais de 2024. <b>Tema explosivo em ano eleitoral: não cite
nomes no ar.</b> Se o assunto vier, fale do fenômeno, não das pessoas.</p>
"""

ANALISE_COCAL = """
<p><b>O contraponto — e é por isso que ele importa.</b> Cocal do Sul é a menor
das três em população (17.240) e a <b>maior em PIB por habitante: R$ 62,9 mil</b>,
acima de Criciúma (R$ 57,5 mil). É também a que mais cresceu: +13,7% entre 2010
e 2022.</p>
<p><b>E tem o menor número de casos graves de toda a AMREC: um.</b> Com 0,6
casos graves por 10 mil habitantes, Cocal do Sul é o município mais limpo do
levantamento nas doze cidades da região. Isso é ouro no ar: mostra que o
material não é perseguição a prefeito nenhum — quando a cidade está bem, o
número diz que está bem. Use Cocal como prova de imparcialidade.</p>
<p><b>O caso que existe.</b> A desapropriação de imóveis para a 5ª Área
Industrial virou ação do Ministério Público por suspeita de sobrepreço, com
perícia técnica sobre a escolha da área e os valores pagos.</p>
<p><b>Dois casos de Cocal aparecem no levantamento de Urussanga</b>, por serem
da mesma promotoria: o concurso da Câmara de Cocal do Sul anulado após denúncia
de fraude na banca organizadora, e um caso grave de suspeita de abuso sexual por
professor em escola municipal, com a diretora investigada por omissão. Este
segundo envolve crianças e há ação penal em curso — <b>não é assunto para rádio
de manhã.</b> Está aqui só para você não ser pego de surpresa.</p>
"""


ROTEIRO = [
 ("A expectativa para as eleições de 2026",
  "Ancorar no concreto e no local. <b>Você tem um ativo que nenhum outro "
  "entrevistado tem:</b> um levantamento das 303 cidades de Santa Catarina a "
  "partir do Diário do MP e do Tribunal de Contas. Diga que a expectativa é de "
  "uma eleição decidida menos por promessa e mais por registro público — e que "
  "por isso você foi atrás do registro. Cite Urussanga: 105 casos levantados, "
  "27 graves, cinco multas do TCE por transparência."),
 ("O combate à desinformação durante o período eleitoral",
  "Este é o seu tema natural, mas cuidado com a armadilha: quem promete "
  "'combater a desinformação' soa como quem quer censurar. Vire a chave para "
  "<b>rastreabilidade</b>: cada caso do seu material cita data da edição e "
  "número do processo, e você mesmo publica que a coleta e o resumo foram "
  "feitos com inteligência artificial e podem conter erro. O antídoto à mentira "
  "não é apagar — é dar a fonte para o ouvinte conferir. Essa é uma frase forte "
  "e é verdade no seu caso."),
 ("A influência das redes sociais na campanha",
  "Diferencie alcance de confiança. Rede social distribui, mas quem valida "
  "ainda é a rádio local e o vizinho. Você está no estúdio da Marconi às 7h50 "
  "exatamente porque isso ainda vale mais em Urussanga do que um vídeo viral. "
  "Elogio verdadeiro à emissora, sem puxa-saco."),
 ("As mudanças no comportamento do eleitor",
  "Traga o dado demográfico: Urussanga cresceu 3,4% em doze anos enquanto Cocal "
  "do Sul cresceu 13,7%. Município que não cresce tem eleitorado mais velho, "
  "mais fixo e mais cético — ele já viu promessa demais. Isso muda o que "
  "funciona: menos proposta genérica, mais prestação de contas do que existe."),
 ("A tendência de polarização na disputa pela Presidência",
  "Não morda a isca de nacionalizar a entrevista. Reconheça a polarização, diga "
  "que ela sequestra a atenção que deveria estar no município — e puxe de volta: "
  "'enquanto a gente discute Brasília, o TCE multou a prefeitura daqui cinco "
  "vezes por transparência e quase ninguém ficou sabendo'. É a ponte mais "
  "eficiente que você tem para voltar ao seu terreno."),
 ("A possibilidade de uma terceira via",
  "Responder sem se rotular. O útil é dizer o que você faria diferente, não em "
  "que caixa você cabe. Se insistirem, seja direto sobre a sua posição — "
  "hesitação em rádio soa pior do que discordância."),
 ("As perspectivas para a disputa pelo Governo de Santa Catarina",
  "Você é candidato a deputado estadual: aqui é onde mostra que entende a "
  "máquina que vai fiscalizar. Ligação local pronta: a AMREC soma <b>446,8 mil "
  "habitantes e R$ 3,24 bilhões de receita líquida</b> — mais gente que muita "
  "capital de estado. A região tem peso e costuma ser tratada como periferia de "
  "Florianópolis."),
 ("A participação das mulheres na política e no debate eleitoral",
  "<b>O gancho local está pronto e é forte:</b> a prefeita de Urussanga, Stela "
  "Maris de Agostin Talamini, foi eleita em 2024 e vai <b>presidir a AMREC em "
  "2027</b> — uma mulher no comando da associação das doze cidades da região "
  "carbonífera. Reconhecer isso é justo e é local. Mas atenção: é a mesma "
  "gestora que o TCE multou em R$ 2.866,70 por descumprir determinação sobre "
  "transparência. <b>Não misture as duas coisas na mesma frase</b> — elogiar a "
  "representatividade e cobrar a gestão são falas separadas, e juntá-las soa "
  "como ataque pessoal de véspera de eleição."),
]

SENSIVEIS = """
<div class="danger"><b>1. A própria Rádio Marconi é parte de um dos casos.</b>
Dirigentes da emissora — <b>Daniel Pagani e André Niclele</b> — denunciaram ao
Ministério Público o então prefeito de Urussanga, Luís Gustavo Cancellier, e
Arnaldo Bez Batti, por suposta interferência na atividade da rádio. O MP
<b>não encontrou provas de improbidade administrativa</b>, mas encaminhou cópia
à Procuradoria-Geral de Justiça para avaliar possível crime do prefeito
(processo 06.2023.00000711-3). <br><br>
Ou seja: quem vai te entrevistar já foi ao MP contra um prefeito por liberdade
de imprensa. Isso é uma <b>oportunidade e um risco</b>. Oportunidade porque
transparência e liberdade de imprensa são a mesma conversa e eles vão te ouvir
com simpatia. Risco porque, se você citar o caso de improviso e errar o
desfecho, erra na casa do dono. <b>Não levante o assunto por conta própria.</b>
Se eles levantarem, o que é seguro dizer é exatamente isto: o MP não encontrou
provas de improbidade e mandou a parte criminal para a PGJ avaliar.</div>

<div class="danger"><b>2. Um nome que você não deve pronunciar sem checar.</b>
Existe no levantamento de Urussanga um procedimento arquivado em nome de
<b>Ademir Magagnin</b> (acordo cumprido integralmente, processo
09.2021.00004852-9). O atual prefeito de Cocal do Sul chama-se Ademir Magagnin.
<b>O registro do MP não diz cargo nem município de residência</b>, e o nome não é
raro na região. Não há como afirmar que é a mesma pessoa. Citar isso no ar sem
checagem é o tipo de erro que vira processo. <b>Não use.</b></div>

<div class="danger"><b>3. Três nomes, três períodos — não misture.</b>
Em Urussanga, as multas do TCE por transparência atingem gestores de gestões
diferentes: <b>Luis Gustavo Cancellier</b> (prefeito até 2024, multa de
R$ 1.990,60) e <b>Stela Maris de Agostin Talamini</b> (prefeita desde 2025,
multa de R$ 2.866,70). Um registro do TCE também cita "Jair Nandi, prefeito de
Urussanga" — mas esse mesmo registro está marcado como tendo <b>misturado
processos diferentes</b> na origem. <b>Não use o terceiro nome.</b></div>

<div class="warn"><b>4. Vocabulário jurídico — o erro mais caro do ar.</b>
Em período eleitoral, chamar de condenado quem foi investigado é o que derruba
candidatura. Guarde a escada: <b>apura / investiga</b> (não há culpado),
<b>arquivou</b> (não achou o que apurar), <b>firmou acordo ou TAC</b> (resolveu
sem processo), <b>ajuizou ação</b> (levou à Justiça, ainda sem decisão),
<b>multou / condenou a devolver</b> (aí sim houve decisão). Em Urussanga há
multa aplicada; em Orleans há condenação a devolver dinheiro; na maior parte do
resto há apenas apuração.</div>

<div class="warn"><b>5. Todo o material foi coletado e resumido com
inteligência artificial.</b> Antes de citar qualquer processo específico no ar,
confira na edição original do Diário. Se for citar de memória, cite o padrão
(“cinco multas por transparência”), não o detalhe (valor exato, nome completo).
O padrão você defende; o detalhe pode ter erro.</div>
"""


def build():
    u_fin = FIN["Urussanga"]
    u_pop = u_fin["pop_ibge"]
    du, ump, utce = casos("urussanga")
    u_gr = sum(1 for x in ump + utce if x.get("severity") == "alta")

    cover = f"""<section class="page cover">
      <div>
        <div class="eyebrow">Documento interno de preparação · não é material de campanha</div>
        <h1>Briefing<br>Rádio<br>Marconi</h1>
        <p style="font-size:12pt;margin-top:10px;max-width:135mm">
        Entrevista ao vivo no <b>Comando Marconi</b> — 99.9 FM, Urussanga.
        O que dizer, com que dado, e onde é perigoso pisar.</p>
      </div>
      <div class="meta">
        <p><b>Emissora:</b> Rádio Fundação Marconi 99.9 FM · Rua da Criança, 171, Centro, Urussanga/SC</p>
        <p><b>Programa:</b> Comando Marconi · ao vivo, 7h50 ou 8h20 · também em vídeo no YouTube</p>
        <p><b>Duração:</b> máximo de 20 minutos · roteiro de perguntas igual para todos os candidatos</p>
        <p><b>Formato:</b> presencial no estúdio em Urussanga ou remoto, mediante acordo prévio</p>
        <p><b>Contexto:</b> série de entrevistas com candidatos às eleições de 2026, iniciada em 10/08/2026</p>
        <p style="margin-top:8px;color:#6b6b6b;font-size:8.6pt">
        Fontes: curadoria Transparência Radical (Diário Oficial do MPSC e DOTC-e/TCE-SC,
        10/01/2022 a 25/06/2026) · IBGE Censo 2010 e 2022 e PIB municipal 2023 ·
        finanças municipais 2025 · regulamento publicado pela própria emissora.</p>
      </div>
    </section>"""

    p_sens = f"""<section class="page"><h2>Antes de entrar no ar</h2>
      <p style="margin-bottom:9px">Cinco coisas que, se você não souber, podem
      estragar vinte minutos bem preparados.</p>
      {SENSIVEIS}</section>"""

    p_uru = bloco_cidade("Urussanga", ANALISE_URUSSANGA, max_media=14)
    p_orl = bloco_cidade("Orleans", ANALISE_ORLEANS, max_media=10)
    p_coc = bloco_cidade("Cocal do Sul", ANALISE_COCAL, max_media=8)

    p_reg = f"""<section class="page"><h2>A região inteira</h2>
      <p>A AMREC — Associação dos Municípios da Região Carbonífera — reúne doze
      cidades. É o recorte que a própria emissora usa para escolher quem
      entrevista, então é o mapa que vale nesta conversa.</p>
      <h3 class="sub">Dinheiro público em 2025</h3>
      {tabela_financas()}
      <h3 class="sub">O que o MP e o TCE apuram, por cidade</h3>
      <p style="font-size:9pt;margin-bottom:6px">A última coluna é a que conta a
      história: casos graves por 10 mil habitantes corrige o tamanho da cidade.
      Criciúma tem mais casos em número absoluto porque é grande — mas
      proporcionalmente está longe do topo.</p>
      {tabela_ranking()}
      <div class="warn"><b>Leia a tabela com honestidade.</b> Mais casos não
      significa necessariamente cidade pior: significa cidade mais fiscalizada,
      com mais denúncia chegando ao MP e mais imprensa olhando. Se alguém te
      acusar de estar atacando um município, essa é a resposta — e ela é
      verdadeira.</div>
      </section>"""

    qa = "".join(f'<div class="qa"><div class="q">{i}. {esc(q)}</div>'
                 f'<div class="a">{a}</div></div>'
                 for i, (q, a) in enumerate(ROTEIRO, 1))
    p_rot = f"""<section class="page"><h2>Os oito temas anunciados</h2>
      <p style="margin-bottom:10px">A emissora publicou no regulamento os
      assuntos que serão abordados — todos os candidatos respondem ao mesmo
      roteiro. Você sabe as perguntas de antemão. Abaixo, um ângulo para cada
      uma. <b>Não são respostas para ler</b>: são a direção que aproveita o que
      só você tem.</p>{qa}</section>"""

    pocket = [
        ("20.919", "habitantes em Urussanga (Censo 2022) — só 3,4% a mais que em 2010"),
        ("R$ 147,7 mi", "receita líquida de Urussanga em 2025 — R$ 7.060 por habitante"),
        ("5 multas", "do TCE a gestores de Urussanga por transparência e parcerias com OSCs"),
        ("R$ 2.866,70", "multa à prefeita por descumprir determinação do TCE sobre transparência"),
        ("1991", "ano da condenação ambiental do carvão que o MP ainda fiscaliza em Urussanga"),
        ("27", "casos graves em Urussanga — 12,9 por 10 mil habitantes"),
        ("R$ 683 mil", "contrato da fundação de ensino em Orleans, julgado irregular pelo TCE"),
        ("R$ 107 mil", "que o TCE mandou um servidor de Orleans devolver aos cofres públicos"),
        ("1 caso grave", "em Cocal do Sul — o menor de toda a AMREC, use como prova de isenção"),
        ("R$ 62,9 mil", "PIB por habitante de Cocal do Sul — maior que o de Criciúma"),
        ("446.838", "habitantes na AMREC · R$ 3,24 bilhões de receita líquida somada"),
        ("2027", "ano em que a prefeita de Urussanga vai presidir a AMREC"),
    ]
    pk = "".join(f'<div class="pk"><b>{esc(a)}</b>{esc(b)}</div>' for a, b in pocket)
    p_pk = f"""<section class="page"><h2>Dados de bolso</h2>
      <p style="margin-bottom:10px">Os doze números que valem decorar. Se sair do
      estúdio tendo dito seis destes, a entrevista funcionou.</p>
      <div class="pocket">{pk}</div>
      <h3 class="sub">Três frases que sustentam o resto</h3>
      <ul class="lista">
        <li><b>Sobre o método:</b> "Cada caso que eu cito tem data de edição do
        Diário e número de processo. Não é para você acreditar em mim — é para
        você poder conferir."</li>
        <li><b>Sobre a isenção:</b> "Cocal do Sul tem um caso grave. Urussanga
        tem 27. Se fosse perseguição, o número seria igual nas duas."</li>
        <li><b>Sobre o limite:</b> "A coleta e o resumo foram feitos com
        inteligência artificial e podem ter erro. Por isso a fonte vai junto em
        cada caso."</li>
      </ul>
      <div class="warn"><b>Última checagem antes do ar:</b> confirme se a
      entrevista é 7h50 ou 8h20, se é presencial no estúdio da Rua da Criança ou
      remota, e se sua candidatura foi oficializada na lista da emissora — o
      regulamento manda a equipe do candidato solicitar o espaço quando o
      domicílio eleitoral é de fora da AMREC.</div>
      <div class="foot">Preparado em 24/08/2026 a partir da base Transparência
      Radical. Os casos citados são de fontes públicas oficiais e refletem o que
      estava publicado até 25/06/2026. Documento de uso interno.</div>
      </section>"""

    body = cover + p_sens + p_uru + p_orl + p_coc + p_reg + p_rot + p_pk
    return ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
            f'<style>{CSS}</style></head><body>{body}</body></html>')


def main():
    html_str = build()
    out = os.path.join(HERE, "..", "resumos", "BRIEFING-Radio-Marconi-Urussanga.pdf")
    out = os.path.abspath(out)
    if os.path.exists(out):
        os.unlink(out)
    fd, tmp = tempfile.mkstemp(suffix=".html", dir=AMREC)
    os.write(fd, html_str.encode())
    os.close(fd)
    try:
        for _ in range(2):
            try:
                subprocess.run([CHROME, "--headless", "--disable-gpu",
                                "--no-pdf-header-footer", f"--print-to-pdf={out}",
                                f"file://{tmp}"], timeout=120, capture_output=True)
            except subprocess.TimeoutExpired:
                pass
            if os.path.exists(out) and os.path.getsize(out) > 1000:
                print("->", out)
                return
            time.sleep(1)
        raise RuntimeError("Chrome não gerou o PDF")
    finally:
        os.unlink(tmp)


if __name__ == "__main__":
    main()
