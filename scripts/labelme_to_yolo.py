"""
LabelMe JSON -> YOLO .txt 转换工具
用法: python scripts/labelme_to_yolo.py [--delete-json]
会将 images/ 下所有 json 转为同名的 .txt
"""

import argparse
import json
from pathlib import Path

IMG_DIR = Path("data/gaokao_dataset/images")


def convert_labelme_json_to_yolo(json_path: Path):
    """把单个 LabelMe JSON 转成 YOLO .txt"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    img_w = data["imageWidth"]
    img_h = data["imageHeight"]
    shapes = data["shapes"]

    # 收集所有标签，去重并按字母排序，生成类别映射
    labels = sorted(set(s["label"] for s in shapes))
    # 如果没有 label_map.txt，就生成一个
    label_map_path = IMG_DIR / "label_map.txt"
    if not label_map_path.exists():
        with open(label_map_path, "w", encoding="utf-8") as f:
            for i, lbl in enumerate(labels):
                f.write(f"{i}: {lbl}\n")

    yolo_lines = []
    for s in shapes:
        label_name = s["label"]
        class_id = labels.index(label_name)
        pts = s["points"]
        # LabelMe 的 points 存的是 [[x1,y1], [x2,y2], ...]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)

        # 转 YOLO 归一化格式: class_id center_x center_y width height
        cx = (x_min + x_max) / 2.0 / img_w
        cy = (y_min + y_max) / 2.0 / img_h
        w = (x_max - x_min) / img_w
        h = (y_max - y_min) / img_h

        yolo_lines.append(f"{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")

    # 写 .txt（和图片同名）
    txt_path = json_path.with_suffix(".txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(yolo_lines))

    return len(shapes)


def main():
    parser = argparse.ArgumentParser(description="Convert labelme JSON annotations to YOLO format txt files")
    parser.add_argument("-d", "--delete-json", action="store_true",
                        help="Delete original JSON files after conversion")
    args = parser.parse_args()

    json_files = sorted(IMG_DIR.glob("*.json"))
    # 排除 label_map.txt（如果有）
    json_files = [f for f in json_files if f.name != "label_map.txt"]

    if not json_files:
        print(f"No JSON files found in {IMG_DIR}")
        return

    total_boxes = 0
    for jf in json_files:
        n = convert_labelme_json_to_yolo(jf)
        txt_path = jf.with_suffix(".txt")
        total_boxes += n
        print(f"  {jf.name} -> {txt_path.name} ({n} boxes)")

        if args.delete_json:
            jf.unlink()
            print(f"    Deleted: {jf.name}")

    print(f"\nDone! {len(json_files)} files, {total_boxes} boxes total")
    print(f"Label map: {IMG_DIR / 'label_map.txt'}")
    if args.delete_json:
        print("Original JSON files have been deleted.")


if __name__ == "__main__":
    main()
