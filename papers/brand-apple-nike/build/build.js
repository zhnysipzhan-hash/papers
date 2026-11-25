const fs = require('fs');
const path = require('path');
const { LineRuleType,
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  AlignmentType, WidthType, BorderStyle, ShadingType, Footer, PageNumber,
  VerticalAlign,
} = require('docx');

const dir = __dirname;
const out = process.argv[2];
const FONT = 'Times New Roman';
const SZ = 28;        // 14 pt
const TSZ = 24;       // 12 pt in tables
const LINE = 240;     // single spacing
const IND = 709;      // 1.25 cm

function runs(text, size = SZ, base = {}) {
  // **bold**, *italic*
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/).filter(Boolean);
  return parts.map(p => {
    if (p.startsWith('**')) return new TextRun({ text: p.slice(2, -2), bold: true, font: FONT, size, ...base });
    if (p.startsWith('*')) return new TextRun({ text: p.slice(1, -1), italics: true, font: FONT, size, ...base });
    return new TextRun({ text: p, font: FONT, size, ...base });
  });
}
const para = (text, o = {}) => new Paragraph({
  alignment: o.align ?? AlignmentType.JUSTIFIED,
  indent: o.noIndent ? undefined : { firstLine: IND },
  spacing: { line: LINE, lineRule: LineRuleType.AUTO, before: o.before ?? 0, after: o.after ?? 0 },
  keepNext: o.keepNext,
  children: runs(text, o.size ?? SZ, o.base),
});
const heading = (text, center) => new Paragraph({
  alignment: center ? AlignmentType.CENTER : AlignmentType.JUSTIFIED,
  indent: center ? undefined : { firstLine: IND },
  spacing: { line: LINE, before: 120, after: 60 },
  keepNext: true,
  children: [new TextRun({ text, bold: true, font: FONT, size: SZ })],
});

// ---------- tables ----------
const TW = 9354; // text width in DXA (21 cm - 3 cm - 1.5 cm)
const border = { style: BorderStyle.SINGLE, size: 4, color: '000000' };
const borders = { top: border, bottom: border, left: border, right: border };
function table(rows, widths) {
  return new Table({
    width: { size: TW, type: WidthType.DXA },
    columnWidths: widths,
    rows: rows.map((r, i) => new TableRow({
      tableHeader: i === 0,
      cantSplit: true,
      children: r.map((c, j) => new TableCell({
        width: { size: widths[j], type: WidthType.DXA },
        borders,
        verticalAlign: VerticalAlign.CENTER,
        shading: i === 0 ? { type: ShadingType.CLEAR, color: 'auto', fill: 'E7E6E6' } : undefined,
        margins: { top: 30, bottom: 30, left: 80, right: 80 },
        children: [new Paragraph({
          alignment: i === 0 ? AlignmentType.CENTER : AlignmentType.LEFT,
          spacing: { line: 240 },
          children: runs(c, TSZ, i === 0 ? { bold: true } : {}),
        })],
      })),
    })),
  });
}
const caption = (t) => new Paragraph({
  alignment: AlignmentType.LEFT, spacing: { line: LINE, before: 120, after: 60 }, keepNext: true,
  children: [new TextRun({ text: t, italics: true, font: FONT, size: SZ })],
});
const note = (t) => new Paragraph({
  alignment: AlignmentType.JUSTIFIED, spacing: { line: LINE, before: 40, after: 120 },
  children: [new TextRun({ text: t, italics: true, font: FONT, size: TSZ })],
});

const T1 = [
  caption('1-кесте. Apple және Nike компанияларының негізгі көрсеткіштері'),
  table([
    ['Көрсеткіш', 'Apple', 'Nike'],
    ['Бренд құны (Interbrand, 2025)', '470,9 млрд $, 1-орын', 'шамамен 33,7 млрд $, 23-орын (бір жылда –26%)'],
    ['Түсім, 2024 қаржы жылы', '391,0 млрд $', '51,4 млрд $'],
    ['Жалпы маржа, 2024 қаржы жылы', '46,2% (өнімдер – 37,2%, қызметтер – 73,9%)', '44,6%'],
  ], [3000, 3177, 3177]),
  note('Дереккөз: Interbrand (2025); Apple Inc. (2024a); Nike, Inc. (2024a).'),
];
const T2 = [
  caption('2-кесте. Сауалнама нәтижелері: блоктар бойынша орташа балл (n = 10)'),
  table([
    ['Блок (сұрақ нөмірі)', 'Орташа балл (1–5)', 'Келіскендер үлесі (4–5 балл)'],
    ['Эмоциялық байланыс (10)', '3,4', '60%'],
    ['Өзіндік сәйкестік (12–13)', '3,1', '50%'],
    ['Әдет және бағаға төзімділік (11)', '2,9', '40%'],
    ['ESG және сенім (16–19)', '2,9', '38%'],
    ['Әлеуметтік ықпал мен мәртебе (14–15)', '2,5', '30%'],
    ['Бағаға жалпы дайындық (20)', '3,1', '50%'],
  ], [4354, 2300, 2700]),
  note('Дереккөз: автордың сауалнамасы (Google Forms, 2026 ж. қараша). Келіскендер үлесі блоктағы сұрақтар бойынша орташаланған.'),
];

const FIG = [
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 120 }, keepNext: true,
    children: [new ImageRun({ type: 'png', data: fs.readFileSync(path.join(dir, 'model.png')),
      transformation: { width: 540, height: 285 } })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { line: LINE, before: 60, after: 120 },
    children: [new TextRun({ text: '1-сурет. Тұтынушының қымбат бренд таңдауының тұжырымдамалық моделі (автор әзірлеген)', italics: true, font: FONT, size: SZ })],
  }),
];

const REFS_LIST = [
  'Aaker, D. A. (1991). *Managing brand equity: Capitalizing on the value of a brand name*. Free Press.',
  'Apple Inc. (2024a). *Form 10-K for the fiscal year ended September 28, 2024*. U.S. Securities and Exchange Commission. https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240928.htm',
  'Apple Inc. (2024b). *Environmental progress report*. https://www.apple.com/environment/',
  'Batra, R., Ahuvia, A., & Bagozzi, R. P. (2012). Brand love. *Journal of Marketing, 76*(2), 1–16. https://doi.org/10.1509/jm.09.0339',
  'Becker-Olsen, K. L., Cudmore, B. A., & Hill, R. P. (2006). The impact of perceived corporate social responsibility on consumer behavior. *Journal of Business Research, 59*(1), 46–53. https://doi.org/10.1016/j.jbusres.2005.01.001',
  'Belk, R. W. (1988). Possessions and the extended self. *Journal of Consumer Research, 15*(2), 139–168. https://doi.org/10.1086/209154',
  'Burnham, T. A., Frels, J. K., & Mahajan, V. (2003). Consumer switching costs: A typology, antecedents, and consequences. *Journal of the Academy of Marketing Science, 31*(2), 109–126. https://doi.org/10.1177/0092070302250897',
  'Delmas, M. A., & Burbano, V. C. (2011). The drivers of greenwashing. *California Management Review, 54*(1), 64–87. https://doi.org/10.1525/cmr.2011.54.1.64',
  'Escalas, J. E., & Bettman, J. R. (2005). Self-construal, reference groups, and brand meaning. *Journal of Consumer Research, 32*(3), 378–389. https://doi.org/10.1086/497549',
  'Han, Y. J., Nunes, J. C., & Drèze, X. (2010). Signaling status with luxury goods: The role of brand prominence. *Journal of Marketing, 74*(4), 15–30. https://doi.org/10.1509/jmkg.74.4.015',
  'Holbrook, M. B. (Ed.). (1999). *Consumer value: A framework for analysis and research*. Routledge.',
  'Interbrand. (2025). *Best global brands 2025*. https://interbrand.com/best-brands/',
  'Keller, K. L. (1993). Conceptualizing, measuring, and managing customer-based brand equity. *Journal of Marketing, 57*(1), 1–22. https://doi.org/10.1177/002224299305700101',
  'Locke, R. M. (2013). *The promise and limits of private power: Promoting labor standards in a global economy*. Cambridge University Press.',
  'Nike, Inc. (2024a). *Form 10-K for the fiscal year ended May 31, 2024*. U.S. Securities and Exchange Commission. https://www.sec.gov/Archives/edgar/data/320187/000032018724000044/nke-20240531.htm',
  'Nike, Inc. (2024b). *Impact report*. https://about.nike.com/en/impact',
  'Sheth, J. N., Newman, B. I., & Gross, B. L. (1991). Why we buy what we buy: A theory of consumption values. *Journal of Business Research, 22*(2), 159–170. https://doi.org/10.1016/0148-2963(91)90050-8',
  'Thomson, M., MacInnis, D. J., & Park, C. W. (2005). The ties that bind: Measuring the strength of consumers’ emotional attachments to brands. *Journal of Consumer Psychology, 15*(1), 77–91. https://doi.org/10.1207/s15327663jcp1501_10',
  'White, K., Habib, R., & Hardisty, D. J. (2019). How to SHIFT consumer behaviors to be more sustainable: A literature review and guiding framework. *Journal of Marketing, 83*(3), 22–49. https://doi.org/10.1177/0022242919825649',
  'Zeithaml, V. A. (1988). Consumer perceptions of price, quality, and value: A means-end model and synthesis of evidence. *Journal of Marketing, 52*(3), 2–22. https://doi.org/10.1177/002224298805200302',
];
const REFS = [
  heading('Пайдаланылған әдебиеттер', true),
  ...REFS_LIST.map((r, i) => new Paragraph({
    alignment: AlignmentType.LEFT,
    indent: { left: 426, hanging: 426 },
    spacing: { line: LINE },
    children: runs(`${i + 1}. ${r}`),
  })),
];

// ---------- body from content.txt ----------
const body = [];
for (const raw of fs.readFileSync(path.join(dir, 'content.txt'), 'utf8').split('\n')) {
  const line = raw.trimEnd();
  if (!line) continue;
  if (line === '[[FIG]]') body.push(...FIG);
  else if (line === '[[T1]]') body.push(...T1);
  else if (line === '[[T2]]') body.push(...T2);
  else if (line === '[[REFS]]') body.push(...REFS);
  else if (line.startsWith('## ')) {
    const t = line.slice(3);
    body.push(heading(t, /^(Кіріспе|Қорытынды)$/.test(t)));
  }
  else if (line.startsWith('### ')) body.push(heading(line.slice(4), false));
  else if (line.startsWith('- ')) body.push(para('– ' + line.slice(2)));
  else body.push(para(line));
}

// ---------- cover ----------
const blank = (n) => Array.from({ length: n }, () => new Paragraph({ spacing: { line: LINE }, children: [] }));
const cover = [
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({ type: 'png',
    data: fs.readFileSync(path.join(dir, 'logo.png')), transformation: { width: 600, height: 91 } })] }),
  ...blank(5),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { line: LINE }, children: [
    new TextRun({ text: 'НАРХОЗ УНИВЕРСИТЕТІ', bold: true, font: FONT, size: SZ })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { line: LINE }, children: [
    new TextRun({ text: '«ЭКОНОМИКА ЖӘНЕ МЕНЕДЖМЕНТ» МЕКТЕБІ', bold: true, font: FONT, size: SZ })] }),
  ...blank(4),
  new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { line: 360 }, children: [
    new TextRun({ text: 'Тақырыбы: ', bold: true, font: FONT, size: SZ }),
    new TextRun({ text: '«Неліктен адамдар бір брендті жақсы көріп, қымбат болса да сатып алады? Apple және Nike сияқты брендтер адамдардың сезіміне қалай әсер етеді?»', font: FONT, size: SZ })] }),
  ...blank(4),
  new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { line: 360 }, children: [
    new TextRun({ text: 'Орындаған: ', bold: true, font: FONT, size: SZ }),
    new TextRun({ text: 'Жарылқады Айша Әсетқызы', font: FONT, size: SZ })] }),
  new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { line: 360 }, children: [
    new TextRun({ text: 'Қабылдаған: ', bold: true, font: FONT, size: SZ }),
    new TextRun({ text: 'Ибрагимова Ақгүл Амангельдіқызы', font: FONT, size: SZ })] }),
  ...blank(22),
  new Paragraph({ alignment: AlignmentType.CENTER, pageBreakBefore: false, children: [
    new TextRun({ text: 'Алматы, 2026', bold: true, font: FONT, size: SZ })] }),
];

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: SZ } } } },
  sections: [
    {
      properties: {
        page: { size: { width: 11906, height: 16838 },
          margin: { top: 1134, bottom: 1134, left: 1701, right: 851 } },
      },
      children: cover,
    },
    {
      properties: {
        page: { size: { width: 11906, height: 16838 },
          margin: { top: 1134, bottom: 1134, left: 1701, right: 851 } },
      },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 24 })] })] }) },
      children: body,
    },
  ],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(out, b); console.log('written', out); });
