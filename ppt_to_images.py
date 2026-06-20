"""
PPT转图片工具
将指定目录下所有PPT文件的每一页转换为同名_数字的图片

使用方法:
    python ppt_to_images.py <PPT文件或目录路径> [输出目录] [图片宽度] [图片高度]

示例:
    python ppt_to_images.py ./my_ppt.pptx
    python ppt_to_images.py ./ppt_folder
    python ppt_to_images.py ./ppt_folder ./output 1920 1080
"""

import os
import sys
import glob
from pathlib import Path

def convert_with_comtypes(ppt_path, output_dir, width, height):
    """使用PowerPoint COM接口转换（需要安装PowerPoint）"""
    import comtypes.client
    import subprocess
    import time

    # 先杀掉残留的PowerPoint进程，避免COM阻塞
    subprocess.run(["taskkill", "/F", "/IM", "POWERPNT.EXE"], capture_output=True)
    time.sleep(1)

    comtypes.CoInitialize()
    powerpoint = comtypes.client.CreateObject("PowerPoint.Application")
    try:
        powerpoint.Visible = 1
    except Exception:
        # 某些情况下设置Visible会失败，但不影响导出功能
        pass

    abs_ppt_path = os.path.abspath(ppt_path)
    presentation = powerpoint.Presentations.Open(abs_ppt_path)

    ppt_name = Path(ppt_path).stem
    # 为每个PPT创建独立文件夹
    file_output_dir = os.path.join(output_dir, ppt_name)
    os.makedirs(file_output_dir, exist_ok=True)

    slide_count = len(presentation.Slides)
    print(f"正在转换: {ppt_path} ({slide_count}页)")

    for i, slide in enumerate(presentation.Slides, 1):
        slide_path = os.path.join(file_output_dir, f"{ppt_name}_{i}.png")
        slide.Export(slide_path, "PNG", width, height)
        print(f"  已导出: {ppt_name}_{i}.png")

    presentation.Close()
    powerpoint.Quit()
    comtypes.CoUninitialize()
    print(f"完成! 共导出 {slide_count} 张图片 → {file_output_dir}\n")


def convert_with_libreoffice(ppt_path, output_dir):
    """使用LibreOffice转换（免费，跨平台）"""
    import subprocess

    ppt_name = Path(ppt_path).stem
    # 为每个PPT创建独立文件夹
    file_output_dir = os.path.join(output_dir, ppt_name)
    os.makedirs(file_output_dir, exist_ok=True)

    # 先转为PDF
    pdf_dir = os.path.join(file_output_dir, "_temp_pdf")
    os.makedirs(pdf_dir, exist_ok=True)

    cmd = [
        "libreoffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", pdf_dir,
        os.path.abspath(ppt_path)
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    # 找到生成的PDF
    pdf_path = os.path.join(pdf_dir, f"{ppt_name}.pdf")

    if os.path.exists(pdf_path):
        # 使用pdf2image转换PDF为图片
        try:
            from pdf2image import convert_from_path
        except ImportError:
            print("请安装pdf2image: pip install pdf2image")
            print("还需要安装poppler: https://github.com/osber/poppler-windows/releases")
            return

        images = convert_from_path(pdf_path)
        for i, img in enumerate(images, 1):
            img_path = os.path.join(file_output_dir, f"{ppt_name}_{i}.png")
            img.save(img_path, "PNG")
            print(f"  已导出: {ppt_name}_{i}.png")

        # 清理临时PDF
        os.remove(pdf_path)
        os.rmdir(pdf_dir)
        print(f"完成! 共导出 {len(images)} 张图片 → {file_output_dir}\n")


def find_ppt_files(directory):
    """查找目录下所有PPT文件"""
    ppt_files = []
    for ext in ["*.ppt", "*.pptx"]:
        ppt_files.extend(glob.glob(os.path.join(directory, ext)))
        ppt_files.extend(glob.glob(os.path.join(directory, "**", ext), recursive=True))
    return list(set(ppt_files))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 1920
    height = int(sys.argv[4]) if len(sys.argv) > 4 else 1080

    # 确定要转换的PPT文件列表
    if os.path.isfile(input_path):
        ppt_files = [input_path]
    elif os.path.isdir(input_path):
        ppt_files = find_ppt_files(input_path)
    else:
        print(f"错误: 路径不存在 - {input_path}")
        sys.exit(1)

    if not ppt_files:
        print("未找到任何PPT文件")
        sys.exit(0)

    print(f"找到 {len(ppt_files)} 个PPT文件\n")

    # 选择转换方法
    try:
        import comtypes
        print("使用PowerPoint COM接口转换\n")
        for ppt_file in ppt_files:
            out = output_dir or os.path.join(os.path.dirname(ppt_file), "output")
            convert_with_comtypes(ppt_file, out, width, height)
    except ImportError:
        print("未安装comtypes，尝试使用LibreOffice\n")
        for ppt_file in ppt_files:
            out = output_dir or os.path.join(os.path.dirname(ppt_file), "output")
            convert_with_libreoffice(ppt_file, out)


if __name__ == "__main__":
    main()
