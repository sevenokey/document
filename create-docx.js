const fs = require("fs");
const { AlignmentType, Document, Packer, Paragraph, TextRun } = require("docx");

const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: "Songti SC", size: 72 },
      },
    },
  },
  sections: [
    {
      children: [
        new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "自由万岁", bold: true })],
        }),
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => fs.writeFileSync("自由万岁.docx", buffer));
