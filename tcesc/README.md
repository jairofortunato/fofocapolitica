# TCE/SC — Pipeline do Diário Oficial Eletrônico (DOTC-e)

Este diretório espelha a estrutura usada para o MPSC, mas **separada** para não misturar fontes.

## 📁 Estrutura

```
mp/                                     ← raiz do projeto
├── pdfs/                              ← MPSC (90 PDFs, jan-mai 2026)
├── texts/                             ← MPSC textos
├── parsed/                            ← MPSC JSON
├── resumos/                           ← MPSC análises e dossiês
│   ├── INDEX.md
│   ├── edicoes/
│   ├── lotes/
│   ├── cidades/
│   └── regioes/
│
└── tcesc/                             ← TCE/SC (este diretório)
    ├── README.md                      ← você está aqui
    ├── download_pdfs.sh               ← baixador (configurável por mês/ano)
    ├── pdfs/                          ← 35 PDFs (abr+mai 2026)
    ├── texts/                         ← (a popular com pdftotext)
    ├── parsed/                        ← (a popular com parser)
    └── resumos/
        ├── edicoes/
        ├── lotes/
        ├── cidades/
        └── regioes/
```

## 🌐 Fonte oficial

- Página índice (frontend): https://www.tcesc.tc.br/content/dotc-e
- Endpoint que lista edições (iframe): https://servicos.tcesc.tc.br/endpoint-dotce/index.php
- **Padrão de URL dos PDFs:**
  - Edições regulares: `https://consulta.tce.sc.gov.br/Diario/dotc-e[YYYY-MM-DD].pdf`
  - Edições extraordinárias: `https://consulta.tce.sc.gov.br/Diario/dotc-e[YYYY-MM-DD]-E.pdf`

## 📥 O que já foi coletado

**Abril/2026:** 19 PDFs (incluindo 1 extraordinária em 23/04)
**Maio/2026:** 16 PDFs (até 25/05)
**Total:** 35 PDFs (~19 MB)

## 🛠 Como rodar com outro período

```bash
# Padrão (abril + maio 2026)
./download_pdfs.sh

# Outro mês
YEAR=2026 MONTHS="06" ./download_pdfs.sh

# Vários meses
YEAR=2026 MONTHS="03 04 05 06" ./download_pdfs.sh

# Outro ano
YEAR=2025 MONTHS="11 12" ./download_pdfs.sh
```

O script gera todas as datas do mês e tenta baixar — finais de semana e feriados retornam 404 e são automaticamente descartados.

## 🔭 Próximos passos sugeridos

1. Extrair texto: `for f in pdfs/*.pdf; do base=$(basename "$f" .pdf); pdftotext -layout "$f" "texts/${base}.txt"; done`
2. Adaptar o `parse_extracts.py` do MPSC para os tipos do TCE/SC (Pareceres Prévios, Decisões Singulares, Acórdãos, Citações, Audiências)
3. Curar por cidade/região conforme o foco editorial

## 📋 Diferenças entre MPSC e TCE/SC

| Item | MPSC | TCE/SC |
|------|------|--------|
| Frequência | dias úteis | dias úteis |
| Conteúdo principal | Inquéritos civis, ACPs, recomendações | Pareceres de prestação de contas, multas, decisões singulares, citações |
| Foco municipal | Improbidade, ambiental, saúde, urbanismo | Contas (prefeito, vereadores), licitações, gestão fiscal |
| Sumário por cidade | Não estruturado | **Sim, com índice e numeração de página** |
| Quem assina | Promotores | Conselheiros + Ministério Público de Contas |

> Por isso, vale construir parser próprio para TCE/SC: a estrutura é mais limpa (sumário formal) e os tipos de ato são diferentes.
