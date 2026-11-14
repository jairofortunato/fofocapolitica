const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const inputDir = path.join(root, 'pdf_template', 'amunesc', '_lotes');
const outputDir = path.join(root, 'pdf_template', 'amunesc', '_lotes_curados');

const files = [
  'joinville__72.json',
  'joinville__73.json',
  'joinville__74.json',
  'joinville__75.json',
  'joinville__76.json',
  'joinville__77.json',
  'joinville__78.json',
  'joinville__79.json',
];

const exceptions = {
  'joinville__72.json': {
    598: {
      keep: true,
      title: 'TCE aponta cálculo irregular em aposentadoria de Edna de Souza Augusto',
      description:
        'O TCE identificou que os proventos foram calculados de forma irregular e deu prazo para o IPREVILLE corrigir a conta. A decisão aponta descumprimento da regra da Lei 10.887/2004 sobre a média das remunerações. O caso segue com restrição a ser sanada.',
      status: '🔴 apontou irregularidade',
      severity: 'media',
    },
    611: {
      keep: true,
      title: 'TCE barra aposentadoria de Maria das Dores por acúmulo ilegal',
      description:
        'O Tribunal negou o registro da aposentadoria de Maria das Dores de Oliveira Santiago Silva por acúmulo ilegal de cargos com o Estado. Também determinou a anulação do ato e a comunicação das providências em 30 dias. O caso ficou marcado como ato ilegal.',
      status: '⬛ julgado irregular',
      severity: 'media',
    },
  },
  'joinville__73.json': {
    647: {
      keep: true,
      title: 'TCE mantém indeferimento da aposentadoria de Terezinha Hoegen',
      description:
        'O Tribunal conheceu o agravo e negou provimento, mantendo a decisão que barrou a aposentadoria de Terezinha Fernandes de Rosa Hoegen. A irregularidade apontada foi o ingresso no cargo de historiadora sem concurso após o marco constitucional. O processo terminou sem reforma da decisão.',
      status: '⬛ julgado irregular',
      severity: 'media',
    },
  },
  'joinville__74.json': {},
  'joinville__75.json': {},
  'joinville__76.json': {},
  'joinville__77.json': {
    925: {
      keep: true,
      title: 'TCE aponta reenquadramento irregular em aposentadoria de Denise Gaga',
      description:
        'O Tribunal apontou que a aposentadoria foi concedida com base em reenquadramento irregular, feito sem concurso público após o marco constitucional. O IPREVILLE recebeu prazo para corrigir a falha formal no ato. O caso ficou com apontamento de irregularidade.',
      status: '🔴 apontou irregularidade',
      severity: 'media',
    },
    932: {
      keep: true,
      title: 'TCE revoga registro da aposentadoria de Marili Bernardete Fagundes',
      description:
        'O colegiado conheceu o decreto que reverteu a aposentadoria por invalidez e revogou o registro anterior do ato. Com isso, cessaram os efeitos da decisão que havia validado a aposentadoria. O processo terminou com a revogação do registro.',
      status: '⬛ julgado irregular',
      severity: 'media',
    },
  },
  'joinville__78.json': {
    1029: {
      keep: true,
      title: 'TCE barra aposentadoria de Amazilda Bergue por concessão irregular',
      description:
        'O Tribunal negou o registro da aposentadoria de Amazilda Maria Bergue por considerar irregular a regra usada para conceder o benefício. A decisão manda anular o ato e revisar o valor dos proventos em novo registro, se for o caso. O caso ficou como aposentadoria ilegal.',
      status: '⬛ julgado irregular',
      severity: 'media',
    },
  },
  'joinville__79.json': {
    1077: {
      keep: true,
      title: 'TCE revoga registro da aposentadoria de Gisele Guesser',
      description:
        'O Tribunal reconheceu o decreto que reverteu a aposentadoria por invalidez de Gisele Cristina Francisco Guesser e revogou o registro anterior. A decisão também cessou os efeitos do ato validado em 2018. O caso terminou com desfazimento do registro.',
      status: '⬛ julgado irregular',
      severity: 'media',
    },
    1085: {
      keep: true,
      title: 'TCE barra aposentadoria de Maria Salete Safanelli por acúmulo de cargos',
      description:
        'O Tribunal negou o registro porque Maria Salete Safanelli acumulava benefício previdenciário estadual com o cargo municipal de auxiliar de enfermagem. A decisão manda anular o ato e comunicar as providências ao TCE. O caso ficou como aposentadoria irregular.',
      status: '⬛ julgado irregular',
      severity: 'media',
    },
    1086: {
      keep: true,
      title: 'TCE barra aposentadoria de Terezinha Hoegen por enquadramento sem concurso',
      description:
        'O Tribunal negou o registro da aposentadoria de Terezinha Fernandes de Rosa Hoegen por enquadramento irregular no cargo de historiadora, sem concurso público. A decisão determina a anulação do ato e a comunicação das providências. O caso ficou como irregular.',
      status: '⬛ julgado irregular',
      severity: 'media',
    },
    1095: {
      keep: true,
      title: 'TCE barra aposentadoria de Carlos Eliel Torres por falhas no cálculo e documentos',
      description:
        'O Tribunal negou o registro da aposentadoria de Carlos Eliel Torres por falta de certidão de tempo de contribuição e por cálculo irregular dos proventos. A decisão manda anular o decreto e refazer o benefício. O caso ficou como ato ilegal.',
      status: '⬛ julgado irregular',
      severity: 'media',
    },
  },
};

for (const file of files) {
  const inputPath = path.join(inputDir, file);
  const outputPath = path.join(outputDir, file);
  const raw = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
  const overrides = exceptions[file] || {};

  const cases = raw.casos.map((item) => {
    const override = overrides[item.i];
    if (!override) {
      return {
        i: item.i,
        tipo: item.tipo,
        keep: false,
        title: '',
        description: '',
        status: '',
        severity: '',
      };
    }

    return {
      i: item.i,
      tipo: item.tipo,
      keep: override.keep,
      title: override.title,
      description: override.description,
      status: override.status,
      severity: override.severity,
    };
  });

  fs.writeFileSync(outputPath, JSON.stringify(cases, null, 2) + '\n');
}
