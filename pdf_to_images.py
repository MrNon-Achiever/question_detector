"""
PDF转图片工具
将指定目录下所有PDF文件的每一页转换为同名_数字的图片

使用方法:
    python pdf_to_images.py <PDF文件或目录路径> [输出目录] [图片DPI]

示例:
    python pdf_to_images.py ./my_file.pdf
    python pdf_to_images.py ./pdf_folder
    python pdf_to_images.py ./pdf_folder ./output 300
"""

import os
import sys
import glob
from pathlib import Path


def convert_with_pymupdf(pdf_path, output_dir, dpi=200):
    """使用PyMuPDF(fitz)转换（推荐，速度快）"""
    import fitz  # PyMuPDF

    pdf_name = Path(pdf_path).stem
    # 为每个PDF创建独立文件夹
    file_output_dir = os.path.join(output_dir, pdf_name)
    os.makedirs(file_output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    page_count = len(doc)
    print(f"正在转换: {pdf_path} ({page_count}页)")

    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)

    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(matrix=mat)
        img_path = os.path.join(file_output_dir, f"{pdf_name}_{i}.png")
        pix.save(img_path)
        print(f"  已导出: {pdf_name}_{i}.png")

    doc.close()
    print(f"完成! 共导出 {page_count} 张图片 → {file_output_dir}\n")


def convert_with_pdf2image(pdf_path, output_dir, dpi=200):
    """使用pdf2image转换（底层使用poppler）"""
    from pdf2image import convert_from_path

    pdf_name = Path(pdf_path).stem
    # 为每个PDF创建独立文件夹
    file_output_dir = os.path.join(output_dir, pdf_name)
    os.makedirs(file_output_dir, exist_ok=True)

    print(f"正在转换: {pdf_path}")
    images = convert_from_path(pdf_path, dpi=dpi)

    for i, img in enumerate(images, 1):
        img_path = os.path.join(file_output_dir, f"{pdf_name}_{i}.png")
        img.save(img_path, "PNG")
        print(f"  已导出: {pdf_name}_{i}.png")

    print(f"完成! 共导出 {len(images)} 张图片 → {file_output_dir}\n")


def convert_with_wand(pdf_path, output_dir, dpi=200):
    """使用Wand(ImageMagick)转换"""
    from wand.image import Image

    pdf_name = Path(pdf_path).stem
    # 为每个PDF创建独立文件夹
    file_output_dir = os.path.join(output_dir, pdf_name)
    os.makedirs(file_output_dir, exist_ok=True)

    print(f"正在转换: {pdf_path}")
    with Image(filename=pdf_path, resolution=dpi) as img:
        page_count = len(img.sequence)
        for i in range(page_count):
            with Image(image=img.sequence[i]) as page:
                img_path = os.path.join(file_output_dir, f"{pdf_name}_{i+1}.png")
                page.save(filename=img_path)
                print(f"  已导出: {pdf_name}_{i+1}.png")

    print(f"完成! 共导出 {page_count} 张图片 → {file_output_dir}\n")


def find_pdf_files(directory):
    """查找目录下所有PDF文件"""
    pdf_files = []
    for ext in ["*.pdf", "*.PDF"]:
        pdf_files.extend(glob.glob(os.path.join(directory, ext)))
        pdf_files.extend(glob.glob(os.path.join(directory, "**", ext), recursive=True))
    return list(set(pdf_files))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 200

    # 确定要转换的PDF文件列表
    if os.path.isfile(input_path):
        pdf_files = [input_path]
    elif os.path.isdir(input_path):
        pdf_files = find_pdf_files(input_path)
    else:
        print(f"错误: 路径不存在 - {input_path}")
        sys.exit(1)

    if not pdf_files:
        print("未找到任何PDF文件")
        sys.exit(0)

    print(f"找到 {len(pdf_files)} 个PDF文件\n")

    # 尝试使用可用的转换方法
    converters = [
        ("PyMuPDF", convert_with_pymupdf),
        ("pdf2image", convert_with_pdf2image),
        ("Wand", convert_with_wand),
    ]

    for name, converter in converters:
        try:
            # 检查依赖是否可用
            if name == "PyMuPDF":
                import fitz
            elif name == "pdf2image":
                from pdf2image import convert_from_path
            elif name == "Wand":
                from wand.image import Image

            print(f"使用{name}转换\n")
            for pdf_file in pdf_files:
                out = output_dir or os.path.join(os.path.dirname(pdf_file), "output")
                converter(pdf_file, out, dpi)
            return
        except ImportError:
            continue

    print("错误: 未找到可用的转换库")
    print("请安装以下任一依赖:")
    print("  pip install PyMuPDF      # 推荐，速度快")
    print("  pip install pdf2image    # 需要安装poppler")
    print("  pip install Wand         # 需要安装ImageMagick")
    sys.exit(1)


if __name__ == "__main__":
    main()
