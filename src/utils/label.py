import os
import json
from PIL import Image
from tqdm import tqdm

# Base dataset path (change this)
dataset_path = r"D:\CrowedSense 360\datasets\Weapons"

# Subdirectories
splits = ["train", "val"]
images_dir = os.path.join(dataset_path, "images")
labels_dir = os.path.join(dataset_path, "labels")

def create_cache(split):
    """Create cache file for YOLO training or validation set."""
    img_folder = os.path.join(images_dir, split)
    lbl_folder = os.path.join(labels_dir, split)
    cache_data = {}

    if not os.path.exists(img_folder):
        print(f"⚠️ Missing folder: {img_folder}")
        return

    print(f"\n📦 Creating cache for '{split}' set...")

    for img_file in tqdm(os.listdir(img_folder)):
        if not img_file.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        img_path = os.path.join(img_folder, img_file)
        lbl_path = os.path.join(lbl_folder, os.path.splitext(img_file)[0] + ".txt")

        # Read image size
        try:
            with Image.open(img_path) as im:
                width, height = im.size
        except Exception as e:
            print(f"❌ Error reading image {img_file}: {e}")
            continue

        # Read YOLO label data
        labels = []
        if os.path.exists(lbl_path):
            with open(lbl_path, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        labels.append([float(x) for x in parts])
        else:
            print(f"⚠️ No label found for {img_file}")

        cache_data[img_path] = {
            "shape": [height, width],
            "labels": labels,
            "label_path": lbl_path,
        }

    # Save cache file
    cache_path = os.path.join(dataset_path, f"{split}.cache")
    with open(cache_path, "w") as f:
        json.dump(cache_data, f, indent=2)

    print(f"✅ {split.capitalize()} cache file created: {cache_path}")
    print(f"🖼️ Total cached images: {len(cache_data)}")

# Generate cache for both train and val
for split in splits:
    create_cache(split)

print("\n🎯 Cache generation complete for train and val sets!")
