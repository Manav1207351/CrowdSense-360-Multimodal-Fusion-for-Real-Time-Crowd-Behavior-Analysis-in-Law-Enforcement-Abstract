# Minimal helpers: convert simple CSV of bbox -> YOLO labels or validate annotation counts
# Extend for full COCO<->YOLO conversions using pycocotools when needed.
import os
import json
from pathlib import Path

def read_simple_coco(coco_json_path):
    with open(coco_json_path) as f:
        j = json.load(f)
    images = {img['id']: img for img in j['images']}
    anns = j['annotations']
    grouped = {}
    for a in anns:
        imgid = a['image_id']
        bbox = a['bbox']  # COCO bbox [x,y,w,h]
        cls = a['category_id']
        grouped.setdefault(imgid, []).append({'bbox': bbox, 'cls': cls})
    return images, grouped

def coco_to_yolo(coco_json, images_dir, out_dir, class_map=None):
    # class_map: map coco category id -> target yolo index (0..N-1). If None, uses original category ids.
    images, grouped = read_simple_coco(coco_json)
    os.makedirs(out_dir, exist_ok=True)
    for imgid, img in images.items():
        fname = img['file_name']
        w = img['width']; h = img['height']
        anns = grouped.get(imgid, [])
        # create label file
        lbl_lines = []
        for a in anns:
            x,y,wbox,hbox = a['bbox']
            cx = x + wbox/2
            cy = y + hbox/2
            # normalized
            cx_n = cx / w
            cy_n = cy / h
            w_n = wbox / w
            h_n = hbox / h
            cls = a['cls'] if class_map is None else class_map.get(a['cls'], a['cls'])
            lbl_lines.append(f"{cls} {cx_n:.6f} {cy_n:.6f} {w_n:.6f} {h_n:.6f}")
        out_lbl = Path(out_dir) / (Path(fname).stem + ".txt")
        out_lbl.write_text("\n".join(lbl_lines))
    print("COCO -> YOLO conversion done for", len(images), "images.")

