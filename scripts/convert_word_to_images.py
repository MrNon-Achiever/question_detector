"""
Word 文档 -> JPG 图片转换工具
将 gaokao_dataset/ 下的所有高考数学试卷逐页转为 JPG 图片
输出到 gaokao_dataset/images/ 下，每套卷子一个子文件夹
"""

import win32com.client
import pythoncom
import fitz  # PyMuPDF
from pathlib import Path
import sys
import tempfile
import time

GAOKAO_DIR = Path("data/gaokao_dataset")
OUTPUT_DIR = GAOKAO_DIR / "images"


def word_to_pdf(word_path: Path, pdf_path: Path):
    """用本地 Word 把 doc/docx 另存为 PDF"""
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = False

    try:
        doc = word.Documents.Open(str(word_path.resolve()))
        doc.SaveAs(str(pdf_path.resolve()), FileFormat=17)  # 17 = wdFormatPDF
        doc.Close()
    except Exception as e:
        raise RuntimeError(f"Word Open/Save failed: {e}")
    finally:
        word.Quit()


def pdf_to_jpgs(pdf_path: Path, output_folder: Path, dpi: int = 200):
    """PDF 每页转成一张 JPG"""
    doc = fitz.open(pdf_path)
    count = 0
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=dpi)
        out = output_folder / f"page_{i + 1}.jpg"
        pix.save(str(out))
        count += 1
    doc.close()
    return count


def main():
    pythoncom.CoInitialize()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    word_files = sorted(
        list(GAOKAO_DIR.glob("*.docx")) + list(GAOKAO_DIR.glob("*.doc"))
    )

    if not word_files:
        print(f"[ERROR] No .docx/.doc files found in {GAOKAO_DIR.resolve()}")
        sys.exit(1)

    results = []

    for wf in word_files:
        paper_name = wf.stem
        paper_dir = OUTPUT_DIR / paper_name

        if paper_dir.exists() and any(paper_dir.glob("*.jpg")):
            count = len(list(paper_dir.glob("*.jpg")))
            print(f"[SKIP] {paper_name} ({count} pages)")
            results.append((paper_name, "skipped", count))
            continue

        print(f"\n>>> {paper_name} ...", end=" ", flush=True)
        paper_dir.mkdir(parents=True, exist_ok=True)

        tmp_pdf = Path(tempfile.gettempdir()) / f"{paper_name}.pdf"

        try:
            word_to_pdf(wf, tmp_pdf)
            pages = pdf_to_jpgs(tmp_pdf, paper_dir)
            print(f"OK ({pages} pages)")
            results.append((paper_name, "ok", pages))
        except Exception as e:
            print(f"FAILED: {e}")
            results.append((paper_name, "failed", 0))
            # 清理空文件夹
            if paper_dir.exists() and not any(paper_dir.glob("*")):
                paper_dir.rmdir()
        finally:
            if tmp_pdf.exists():
                tmp_pdf.unlink()

    print(f"\n{'='*50}")
    print(f"RESULTS:")
    ok = sum(1 for r in results if r[1] == "ok")
    fail = sum(1 for r in results if r[1] == "failed")
    total_pages = sum(r[2] for r in results)
    for name, status, pages in results:
        icon = "OK" if status == "ok" else "SKIP" if status == "skipped" else "FAIL"
        print(f"  [{icon}] {name} ({pages}p)")
    print(f"\n{ok+fail} papers, {ok} ok, {fail} failed, {total_pages} pages total")
    print(f"Images: {OUTPUT_DIR.resolve()}")

    pythoncom.CoUninitialize()


if __name__ == "__main__":
    main()
