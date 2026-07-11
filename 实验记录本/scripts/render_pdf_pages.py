from pathlib import Path

import pypdfium2 as pdfium


PDF = Path(r"D:\Users\ao\Documents\电致变色\实验记录本\outputs\qa_da_gel_plan\DA凝胶器件综合性能优化实验方案.pdf")
OUT_DIR = Path(r"D:\Users\ao\Documents\电致变色\实验记录本\outputs\qa_da_gel_plan\pages")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(PDF)
    print(f"pages={len(pdf)}")
    for i, page in enumerate(pdf):
        bitmap = page.render(scale=1.6)
        image = bitmap.to_pil()
        out = OUT_DIR / f"page-{i + 1:02d}.png"
        image.save(out)
        print(out)


if __name__ == "__main__":
    main()
