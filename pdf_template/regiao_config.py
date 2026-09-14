#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configuração por região do dossiê "Fofoca Política: Transparência Radical".

A AMREC foi construída com região/sigla/contagem de cidades escritos direto no
HTML e no gerador. Ao escalar para as outras 20 regiões isso vira erro silencioso
(um PDF de Araranguá dizendo "Região Carbonífera · AMREC"), então tudo que muda
de região para região passa a viver aqui.

Cada região expõe:
  sigla       — usada nos nomes de arquivo e nos MDs de origem (regiao-<sigla>.md)
  nome        — nome por extenso, como aparece no PDF ("Extremo Sul")
  label       — linha de identificação no cabeçalho/capa
  ordem       — ordem de geração das cidades (as maiores primeiro)
  cores       — cor de destaque por cidade
  imgs        — bandeira/brasão por cidade (caminho relativo ao dir da região)
  financas    — pop / rec / desp por cidade
"""
import json
import os
import unicodedata
import re

HERE = os.path.dirname(os.path.abspath(__file__))


def slugify(city: str) -> str:
    s = unicodedata.normalize("NFKD", city).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def asset_slug(city: str) -> str:
    """Slug usado nos nomes de imagem (sem separador): 'Cocal do Sul' -> 'cocaldosul'."""
    s = unicodedata.normalize("NFKD", city).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.lower())


class Regiao:
    def __init__(self, sigla, nome, label, ordem, cores, financas, imgs=None):
        self.sigla = sigla
        self.nome = nome
        self.label = label
        self.ordem = ordem
        self.cores = cores
        self.financas = financas
        self._imgs = imgs

    @property
    def dir(self):
        return os.path.join(HERE, self.sigla)

    @property
    def n_cidades(self):
        return len(self.ordem)

    def imgs(self, city):
        """Descobre bandeira/brasão no disco em vez de manter uma lista fixa:
        as extensões variam por cidade (.png/.jpg) conforme o que a fonte tinha."""
        if self._imgs is not None:
            return self._imgs.get(city, {})
        out = {}
        base = os.path.join(self.dir, "assets", "cidades")
        for key, suf in (("bandeira", "b"), ("brasao", "e")):
            for ext in ("png", "jpg", "jpeg", "svg"):
                fn = f"{asset_slug(city)}-{suf}.{ext}"
                if os.path.exists(os.path.join(base, fn)):
                    out[key] = f"./assets/cidades/{fn}"
                    break
        return out

    def texto_capa(self, city):
        return (f"{city} é uma das {self.n_cidades} cidades cobertas pelo "
                f"monitoramento Transparência Radical nesta região.")


def _load_json(sigla, name, default):
    path = os.path.join(HERE, sigla, name)
    return json.load(open(path)) if os.path.exists(path) else default


# --- AMREC ---------------------------------------------------------------
# Mantém os valores originais importados de amrec/gen_amrec.py, que continua
# sendo a fonte de verdade dessa região (já validada e publicada).
def _amrec():
    import sys
    sys.path.insert(0, os.path.join(HERE, "amrec"))
    import gen_amrec as g
    return Regiao(
        sigla="amrec",
        nome="Região Carbonífera",
        label="Região Carbonífera · AMREC",
        ordem=g.ORDEM,
        cores=g.CITY_COLOR,
        financas=g.FINANCAS,
        imgs=g.IMGS,
    )


# --- AMESC ---------------------------------------------------------------
AMESC_ORDEM = [
    "Araranguá", "Sombrio", "Balneário Gaivota", "Turvo", "Passo de Torres",
    "Santa Rosa do Sul", "Balneário Arroio do Silva", "Maracajá", "Meleiro",
    "Praia Grande", "São João do Sul", "Jacinto Machado", "Ermo",
    "Timbé do Sul", "Morro Grande",
]

AMESC = Regiao(
    sigla="amesc",
    nome="Extremo Sul",
    label="Extremo Sul · AMESC",
    ordem=AMESC_ORDEM,
    cores=_load_json("amesc", "cores.json", {}),
    financas=_load_json("amesc", "financas.json", {}),
)

# --- AMUREL --------------------------------------------------------------
AMUREL_ORDEM = [
    "Tubarão", "Laguna", "Imbituba", "Braço do Norte", "Jaguaruna",
    "Capivari de Baixo", "Imaruí", "Gravatal", "Treze de Maio", "Sangão",
    "São Ludgero", "Armazém", "Pedras Grandes", "Pescaria Brava",
    "Rio Fortuna", "Santa Rosa de Lima", "Grão-Pará", "São Martinho",
]

AMUREL = Regiao(
    sigla="amurel",
    nome="Tubarão-Laguna",
    label="Tubarão-Laguna · AMUREL",
    ordem=AMUREL_ORDEM,
    cores=_load_json("amurel", "cores.json", {}),
    financas=_load_json("amurel", "financas.json", {}),
)

# --- AMURES --------------------------------------------------------------
AMURES_ORDEM = [
    "Lages", "São Joaquim", "Otacílio Costa", "Correia Pinto", "Urubici",
    "São José do Cerrito", "Bom Retiro", "Anita Garibaldi", "Campo Belo do Sul",
    "Ponte Alta", "Bom Jardim da Serra", "Bocaina do Sul", "Cerro Negro",
    "Urupema", "Capão Alto", "Palmeira", "Rio Rufino", "Painel",
]

AMURES = Regiao(
    sigla="amures",
    nome="Serra Catarinense",
    label="Serra Catarinense · AMURES",
    ordem=AMURES_ORDEM,
    cores=_load_json("amures", "cores.json", {}),
    financas=_load_json("amures", "financas.json", {}),
)

# --- AMVALI --------------------------------------------------------------
AMVALI_ORDEM = [
    "Jaraguá do Sul", "Guaramirim", "Barra Velha", "Schroeder", "Massaranduba",
    "Corupá", "São João do Itaperiú",
]

AMVALI = Regiao(
    sigla="amvali",
    nome="Vale do Itapocu",
    label="Vale do Itapocu · AMVALI",
    ordem=AMVALI_ORDEM,
    cores=_load_json("amvali", "cores.json", {}),
    financas=_load_json("amvali", "financas.json", {}),
)

# --- AMMVI ---------------------------------------------------------------
AMMVI_ORDEM = [
    "Blumenau", "Brusque", "Gaspar", "Indaial", "Timbó", "Pomerode",
    "Guabiruba", "Rodeio", "Rio dos Cedros", "Benedito Novo", "Apiúna",
    "Ascurra", "Botuverá", "Doutor Pedrinho",
]

AMMVI = Regiao(
    sigla="ammvi",
    nome="Médio Vale do Itajaí",
    label="Médio Vale do Itajaí · AMMVI",
    ordem=AMMVI_ORDEM,
    cores=_load_json("ammvi", "cores.json", {}),
    financas=_load_json("ammvi", "financas.json", {}),
)

# --- AMUNESC -------------------------------------------------------------
AMUNESC_ORDEM = [
    "Joinville", "São Bento do Sul", "São Francisco do Sul", "Araquari",
    "Rio Negrinho", "Itapoá", "Garuva", "Balneário Barra do Sul",
    "Campo Alegre",
]

AMUNESC = Regiao(
    sigla="amunesc",
    nome="Nordeste",
    label="Nordeste · AMUNESC",
    ordem=AMUNESC_ORDEM,
    cores=_load_json("amunesc", "cores.json", {}),
    financas=_load_json("amunesc", "financas.json", {}),
)

_REGIOES_BASE = {"amesc": AMESC, "amurel": AMUREL, "amures": AMURES,
                 "amvali": AMVALI, "ammvi": AMMVI, "amunesc": AMUNESC}


# --- AMURC / AMPLASC / GRANFPOLIS ----------------------------------------
# Regiões montadas cidade a cidade a pedido, e não em lote: os MDs de origem
# são anteriores à correção de atribuição, então o raw destas vem do
# `extract_city_strict.py`, que exige âncora institucional e faz a decisão do
# tribunal mandar na atribuição. O `financas.json` destas é aberto cidade a
# cidade, conforme cada uma é publicada (IBGE Censo 2022 + RREO do Siconfi);
# cidade ainda sem número fica de fora do arquivo e o cabeçalho omite o box em
# vez de estimar dinheiro público.
AMURC = Regiao(
    sigla="amurc",
    nome="Região do Contestado",
    label="Região do Contestado · AMURC",
    ordem=["Curitibanos", "Santa Cecília", "Ponte Alta do Norte",
           "São Cristóvão do Sul", "Frei Rogério"],
    cores=_load_json("amurc", "cores.json", {}),
    financas=_load_json("amurc", "financas.json", {}),
)

AMPLASC = Regiao(
    sigla="amplasc",
    nome="Planalto Sul",
    label="Planalto Sul · AMPLASC",
    ordem=["Campos Novos", "Monte Carlo", "Celso Ramos", "Abdon Batista",
           "Brunópolis", "Vargem", "Zortéa"],
    cores=_load_json("amplasc", "cores.json", {}),
    financas=_load_json("amplasc", "financas.json", {}),
)

GRANFPOLIS = Regiao(
    sigla="granfpolis",
    nome="Grande Florianópolis",
    label="Grande Florianópolis · GRANFPOLIS",
    ordem=["Florianópolis", "São José", "Palhoça", "Biguaçu", "Tijucas",
           "São João Batista", "Garopaba", "Santo Amaro da Imperatriz",
           "Nova Trento", "Canelinha", "Governador Celso Ramos",
           "Alfredo Wagner", "Paulo Lopes", "Antônio Carlos", "Águas Mornas",
           "Angelina", "Anitápolis", "Rancho Queimado", "São Bonifácio",
           "São Pedro de Alcântara", "Major Gercino", "Leoberto Leal"],
    cores=_load_json("granfpolis", "cores.json", {}),
    financas=_load_json("granfpolis", "financas.json", {}),
)

AMOSC = Regiao(
    sigla="amosc",
    nome="Oeste Catarinense",
    label="Oeste Catarinense · AMOSC",
    ordem=["Chapecó", "Coronel Freitas", "Guatambú", "Nova Erechim", "Pinhalzinho",
           "Quilombo", "São Carlos", "Águas de Chapecó", "Águas Frias",
           "Caxambu do Sul", "Cordilheira Alta", "Formosa do Sul", "Irati",
           "Jardinópolis", "Nova Itaberaba", "Novo Horizonte", "Planalto Alegre",
           "Santiago do Sul", "São Lourenço do Oeste", "Serra Alta",
           "Sul Brasil", "União do Oeste"],
    cores=_load_json("amosc", "cores.json", {}),
    financas=_load_json("amosc", "financas.json", {}),
)

AMPLANORTE = Regiao(
    sigla="amplanorte",
    nome="Planalto Norte",
    label="Planalto Norte · AMPLANORTE",
    ordem=["Mafra", "Canoinhas", "Porto União", "Itaiópolis", "Papanduva",
           "Três Barras", "Irineópolis", "Monte Castelo", "Major Vieira",
           "Bela Vista do Toldo"],
    cores=_load_json("amplanorte", "cores.json", {}),
    financas=_load_json("amplanorte", "financas.json", {}),
)

AMEOSC = Regiao(
    sigla="ameosc",
    nome="Extremo Oeste",
    label="Extremo Oeste · AMEOSC",
    ordem=["São Miguel do Oeste", "Itapiranga", "Dionísio Cerqueira",
           "São José do Cedro", "Mondaí", "Descanso", "Anchieta", "Palma Sola",
           "Guaraciaba", "Iporã do Oeste", "São João do Oeste", "Guarujá do Sul",
           "Tunápolis", "Bandeirante", "Paraíso", "Barra Bonita", "Belmonte",
           "Princesa", "Santa Helena"],
    cores=_load_json("ameosc", "cores.json", {}),
    financas=_load_json("ameosc", "financas.json", {}),
)


# --- AMARP ---------------------------------------------------------------
# Aberta a pedido, cidade a cidade (Caçador primeiro), no mesmo molde de
# AMURC/AMPLASC/GRANFPOLIS: raw pelo `extract_city_strict.py` e `financas.json`
# aberto cidade a cidade, conforme cada uma é publicada.
AMARP = Regiao(
    sigla="amarp",
    nome="Alto Vale do Rio do Peixe",
    label="Alto Vale do Rio do Peixe · AMARP",
    ordem=["Caçador", "Videira", "Fraiburgo", "Lebon Régis", "Tangará",
           "Timbó Grande", "Rio das Antas", "Salto Veloso", "Pinheiro Preto",
           "Arroio Trinta", "Calmon", "Iomerê", "Matos Costa", "Ibiam",
           "Macieira"],
    cores=_load_json("amarp", "cores.json", {}),
    financas=_load_json("amarp", "financas.json", {}),
)



# --- AMFRI / AMAVI -------------------------------------------------------
# Abertas para o lote de dossiês de casos graves (Ilhota, Itapema e Taió). Mesmo
# molde das anteriores: raw pelo `extract_city_strict.py`, ordem por população do
# Censo 2022, finanças do RREO 2025 quando o município publicou no Siconfi.
AMFRI = Regiao(
    sigla="amfri",
    nome="Foz do Rio Itajaí",
    label="Foz do Rio Itajaí · AMFRI",
    ordem=["Itajaí", "Balneário Camboriú", "Camboriú", "Navegantes", "Itapema",
           "Penha", "Porto Belo", "Balneário Piçarras", "Bombinhas", "Ilhota",
           "Luiz Alves"],
    cores=_load_json("amfri", "cores.json", {}),
    financas=_load_json("amfri", "financas.json", {}),
)

AMAVI = Regiao(
    sigla="amavi",
    nome="Alto Vale do Itajaí",
    label="Alto Vale do Itajaí · AMAVI",
    ordem=["Rio do Sul", "Ituporanga", "Presidente Getúlio", "Ibirama", "Taió",
           "Pouso Redondo", "Lontras", "Agrolândia", "Santa Terezinha",
           "Laurentino", "Rio do Oeste", "Salete", "Trombudo Central", "Aurora",
           "Petrolândia", "Rio do Campo", "Vidal Ramos", "Agronômica",
           "José Boiteux", "Imbuia", "Vitor Meireles", "Witmarsum",
           "Dona Emma", "Braço do Trombudo", "Atalanta", "Chapadão do Lageado",
           "Mirim Doce", "Presidente Nereu"],
    cores=_load_json("amavi", "cores.json", {}),
    financas=_load_json("amavi", "financas.json", {}),
)


REGIOES = dict(_REGIOES_BASE,
                amurc=AMURC, amplasc=AMPLASC, granfpolis=GRANFPOLIS,
                amosc=AMOSC, amplanorte=AMPLANORTE, ameosc=AMEOSC,
                amarp=AMARP, amfri=AMFRI, amavi=AMAVI)


def get(sigla):
    if sigla == "amrec":
        return _amrec()
    if sigla not in REGIOES:
        raise KeyError(f"região não configurada: {sigla}")
    return REGIOES[sigla]
