#!/usr/bin/env python3
"""Diagrama os três conjuntos de extratos com títulos e situações lidos caso a caso.

Reutiliza capa, cabeçalho, cards, fontes e impressão de gen_dossie.py.
A revisão JSON é vinculada ao Markdown por SHA-256 de cada bloco; não há
classificação editorial por palavras-chave nem descarte de arquivamentos.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

from pypdf import PdfReader, PdfWriter
import gen_dossie as gd
import regiao_config as rc

STATUS = {
    'apuracao': ('Em apuração', 'yel'),
    'acompanhamento': ('Em acompanhamento', 'yel'),
    'arquivado': ('Arquivado', 'green'),
    'parcial': ('Arquivamento parcial', 'gray'),
    'tac': ('TAC firmado', 'amber'),
    'acp': ('Ação civil pública ajuizada', 'red'),
    'acao': ('Ação judicial ajuizada', 'red'),
    'denuncia': ('Denúncia ajuizada', 'red'),
    'instrucao': ('Em instrução', 'yel'),
    'sem_merito': ('Sem exame do mérito', 'gray'),
    'improcedente': ('Improcedente · arquivado', 'green'),
    'indefinido': ('Desfecho não informado', 'gray'),
    'determinacao': ('Determinação do TCE', 'tce'),
    'orientacao': ('Consulta respondida', 'gray'),
    'cautelar': ('Cautelar / sustação', 'amber'),
    'irregular': ('Julgado irregular', 'red'),
    'irregular_sem_multa': ('Irregular · sem penalidade', 'gray'),
    'regular': ('Ato considerado legal', 'green'),
    'cumprido': ('Determinação ou recomendação cumprida', 'green'),
    'outro_municipio': ('Registro de outro município', 'gray'),
    'estadual': ('Órgão estadual', 'gray'),
    'outro_orgao': ('Registro de outro órgão', 'gray'),
    'acnp': ('Acordo de não persecução civil', 'amber'),
    'prescrito': ('Prescrito · arquivado', 'gray'),
    'acordo_penal': ('Acordo de não persecução penal', 'amber'),
    'multa': ('Multa aplicada', 'red'),
    'irregular_sem_debito': ('Irregular · sem débito', 'gray'),
    'recurso_negado': ('Recurso não provido', 'gray'),
    'recurso_suspensivo': ('Recurso com efeito suspensivo', 'gray'),
    'registro_negado': ('Registro negado', 'red'),
}


def source_blocks(md):
    blocks = []
    for piece in re.split(r'(?=^## |^#### )', md, flags=re.M):
        if piece.startswith('#### '):
            blocks.append(re.split(r'^### ', piece, flags=re.M)[0].strip().removesuffix('---').strip())
    return blocks


def markdown_html(text):
    return subprocess.run(['pandoc', '--from=gfm', '--to=html5', '--wrap=none'],
                          input=text, text=True, capture_output=True, check=True).stdout


def render(md, region, city, out):
    reg = rc.get(region)
    review_path = md.parent / 'revisao' / (md.stem.replace('-base-documental', '') + '.json')
    records = json.loads(review_path.read_text())
    blocks = source_blocks(md.read_text())
    assert len(blocks) == len(records)
    cards = []
    long_titles = set()
    for i, (r, block) in enumerate(zip(records, blocks)):
        assert r['id'] == i and hashlib.sha256(block.encode()).hexdigest() == r['sha256'], f'Base alterada: {i}'
        if not r.get('include', True):
            continue
        assert r['title'].strip() and r['status_key'] in STATUS
        ymd = tuple(map(int, r['date'].split('-')))
        label, cls = STATUS[r['status_key']]
        # Metadata moves to the source line. In particular, do not repeat the
        # old automatic status beside the status established by reading.
        body = r['body'].partition('\n')[2].strip()
        if not body:
            body = 'O extrato disponível não detalha o objeto ou o desfecho da publicação.'
        content = markdown_html(body)
        if r.get('note'):
            content = f'<p class="source-note">{gd.esc(r["note"])}</p>' + content
        url = gd.mp_source_link(ymd) if r['src'] == 'mp' else gd.tce_source_link(ymd)
        source = 'Diário Oficial do MPSC' if r['src'] == 'mp' else 'DOTC-e/TCE-SC'
        ref = r['ref']
        if ref.startswith(('•', '·', '⭐')):
            ref = re.sub(r'^[•·⭐]\s*', '', ref)
        source_line = (f'Fonte: {source}, edição de {ymd[2]:02d}/{ymd[1]:02d}/{ymd[0]} '
                       f'· Processo nº {gd.esc(ref)} · '
                       f'<a href="{url}">conferir a edição original</a>')
        title = gd.esc(r['title'])
        if len(body) > 4500:
            long_titles.add(title)
        cards.append(dict(ymd=ymd, src='MP' if r['src']=='mp' else 'TCE', severity='media',
                          cls=cls, status=label, title=title, line=content,
                          fonte_html=source_line, dm=f'{ymd[2]:02d} {gd.MESES_PT[ymd[1]]}'))
    cards.sort(key=lambda c: c['ymd'], reverse=True)
    inner, count, _ = gd.build_city_html(reg, city, cards=cards)
    count_html = (f'<div class="ccount">{count} registros · '
                  f'{sum(c["src"]=="MP" for c in cards)} do Ministério Público · '
                  f'{sum(c["src"]=="TCE" for c in cards)} do Tribunal de Contas</div>'
                  '<p class="method-note">Situação na publicação citada. '
                  'Títulos e selos resumem os extratos disponíveis; consulte a fonte para atualizações.</p>')
    inner = re.sub(r'<div class="ccount">.*?</div>', lambda _: count_html, inner, count=1, flags=re.S)
    # Long decisions must be allowed to span pages instead of overflowing.
    for title in long_titles:
        marker = f'<h3>{title}</h3>'
        pos = inner.index(marker)
        start = inner.rfind('<div class="case"', 0, pos)
        assert start >= 0
        inner = inner[:start] + inner[start:].replace('class="case"', 'class="case long-record"', 1)
    style = '''
    .cityblock{page-break-before:auto}
    .case .ln p{margin:0 0 2mm;orphans:3;widows:3}
    .case .ln{overflow-wrap:anywhere}
    .case .body{min-width:0}
    .case h3{break-after:avoid}
    .case.long-record{break-inside:auto}
    .case .pl{flex-wrap:wrap}
    .case .ref{color:#777}
    .source-note{padding:2mm 3mm;border-left:2px solid #999;background:#f5f5f5;font-size:8pt}
    .method-note{font-size:8pt;line-height:1.4;color:#666;margin:-2mm 0 5mm}
    '''
    inner = inner.replace('</style>', style + '</style>')
    back = gd.wrap('''<section class="page cta"><div class="pad">
      <div class="eyebrow">Fontes públicas oficiais</div>
      <h2 style="font-family:Anton;font-size:36pt;margin:15mm 0">FONTES E MÉTODO</h2>
      <div style="font-size:12pt;line-height:1.6;color:#eee">
      <p>Documento baseado nos extratos do Diário Oficial do MPSC e do DOTC-e/TCE-SC
      armazenados no repositório. Cada registro traz a edição e a referência do processo.</p>
      <p style="margin-top:8mm">Os títulos e selos foram revistos a partir dos textos
      disponíveis. A situação indicada corresponde à publicação citada, e não comprova
      o desfecho atual. Investigações e acusações não equivalem a condenações.</p>
      <p style="margin-top:8mm">Arquivamentos e acordos são apresentados como tal.
      A contagem é de registros e pode incluir várias publicações do mesmo processo.</p>
      <p style="margin-top:8mm">A coleta e a organização dos textos foram feitas com
      inteligência artificial e podem conter erros. Há extratos truncados e registros
      com informações de outros órgãos ou municípios, assinalados no documento.</p>
      <p style="margin-top:8mm">Não houve nova conferência integral dos diários originais.
      Confira sempre a fonte e as decisões posteriores antes de usar as informações.</p>
      </div></div></section>''')
    build = Path(reg.dir) / '_build'
    build.mkdir(exist_ok=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    writer = PdfWriter()
    for name, doc in [('capa', gd.build_cover_html(reg, city)), ('miolo', inner), ('fontes', back)]:
        part = build / f'consulta_{rc.slugify(city)}_{name}.pdf'
        gd.html_to_pdf(reg, doc, str(part))
        writer.append(str(part))
    writer.write(str(out))
    writer.close()
    reader = PdfReader(str(out))
    compact = re.sub(r'\s+', '', reader.pages[0].extract_text()).upper()
    assert '68.475.851/0001-24' in compact and 'PROPAGANDAELEITORAL' in compact
    text = '\n'.join(p.extract_text() for p in reader.pages)
    assert 'REGISTRO EXTRAÍDO' not in text.upper()
    normalized = re.sub(r'\s+', '', text)
    for r in records:
        if not r.get('include', True):
            continue
        assert re.sub(r'\s+', '', r['title']) in normalized, f'Título ausente: {r["id"]}'
    print(f'{city}: {count} títulos conferidos, {len(reader.pages)} páginas → {out}', flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('md', type=Path)
    ap.add_argument('--regiao', required=True)
    ap.add_argument('--cidade', required=True)
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    render(args.md.resolve(), args.regiao, args.cidade, args.out.resolve())
