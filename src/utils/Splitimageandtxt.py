import os
import shutil

# Path to your dataset folder (update this)
dataset_path = r"C:/Users/Hp/RAj/Weapons-in-Images/Weapons-in-Images"

# Create destination folders
images_path = os.path.join(dataset_path, "images")
labels_path = os.path.join(dataset_path, "labels")

os.makedirs(images_path, exist_ok=True)
os.makedirs(labels_path, exist_ok=True)

# File extensions considered as images
image_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tif", ".tiff")

# Loop through files
for file_name in os.listdir(dataset_path):
    file_path = os.path.join(dataset_path, file_name)

    if os.path.isfile(file_path):
        # Move image files
        if file_name.lower().endswith(image_extensions):
            shutil.move(file_path, os.path.join(images_path, file_name))
        # Move label text files
        elif file_name.lower().endswith(".txt"):
            shutil.move(file_path, os.path.join(labels_path, file_name))

print("✅ Separation complete!")
print(f"Images moved to: {images_path}")
print(f"Labels moved to: {labels_path}")


# Create destination folders
images_path = os.path.join(dataset_path, "images")
labels_path = os.path.join(dataset_path, "labels")

os.makedirs(images_path, exist_ok=True)
os.makedirs(labels_path, exist_ok=True)

# File extensions considered as images
image_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tif", ".tiff")

# Loop through files
for file_name in os.listdir(dataset_path):
    file_path = os.path.join(dataset_path, file_name)

    if os.path.isfile(file_path):
        # Move image files
        if file_name.lower().endswith(image_extensions):
            shutil.move(file_path, os.path.join(images_path, file_name))
        # Move label text files
        elif file_name.lower().endswith(".txt"):
            shutil.move(file_path, os.path.join(labels_path, file_name))

print("✅ Separation complete!")
print(f"Images moved to: {images_path}")
print(f"Labels moved to: {labels_path}")
