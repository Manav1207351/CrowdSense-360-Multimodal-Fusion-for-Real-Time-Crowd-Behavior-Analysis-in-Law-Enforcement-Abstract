import os
import random

# ✅ Base dataset directory (one level above "images" and "labels")
dataset_path = r"D:\CrowedSense 360\datasets\Weapons"

# Input folders
images_train = os.path.join(dataset_path, "images", "train")
images_val = os.path.join(dataset_path, "images", "val")

# Output folders
labels_train = os.path.join(dataset_path, "labels", "train")
labels_val = os.path.join(dataset_path, "labels", "val")

os.makedirs(labels_train, exist_ok=True)
os.makedirs(labels_val, exist_ok=True)

num_classes = 3
max_objects_per_image = 5

def generate_random_label_line():
    cls = random.randint(0, num_classes - 1)
    x_center = round(random.uniform(0.05, 0.95), 6)
    y_center = round(random.uniform(0.05, 0.95), 6)
    width = round(random.uniform(0.05, 0.4), 6)
    height = round(random.uniform(0.05, 0.4), 6)
    return f"{cls} {x_center} {y_center} {width} {height}"

def generate_labels_for_folder(image_folder, label_folder):
    count = 0
    if not os.path.exists(image_folder):
        print(f"⚠️ Image folder not found: {image_folder}")
        return
    for img_file in os.listdir(image_folder):
        if img_file.lower().endswith((".jpg", ".jpeg", ".png")):
            base_name = os.path.splitext(img_file)[0]
            label_path = os.path.join(label_folder, f"{base_name}.txt")
            num_objects = random.randint(1, max_objects_per_image)
            lines = [generate_random_label_line() for _ in range(num_objects)]
            with open(label_path, "w") as f:
                f.write("\n".join(lines) + "\n")
            count += 1
    print(f"✅ Generated {count} label files in: {label_folder}")

generate_labels_for_folder(images_train, labels_train)
generate_labels_for_folder(images_val, labels_val)

print("\n🎯 Random labels successfully generated for all images!")
