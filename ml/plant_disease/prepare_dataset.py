from pathlib import Path
import random
import shutil


# ============================================================
# CONFIGURATION
# ============================================================

SOURCE_DIR = Path(
    r"C:\Users\risha\Documents\CODING\Minor Project\PlantVillage-Dataset\raw\color"
)

DEST_DIR = Path(
    r"C:\Users\risha\Documents\CODING\Minor Project\KrishiVision\ml\plant_disease\dataset"
)

SEED = 42


# ============================================================
# CHECK SOURCE
# ============================================================

if not SOURCE_DIR.exists():
    raise FileNotFoundError(
        f"Source dataset not found:\n{SOURCE_DIR}"
    )


# ============================================================
# CHECK DESTINATION
# ============================================================

for split in ["train", "validation", "test"]:
    split_dir = DEST_DIR / split

    if not split_dir.exists():
        split_dir.mkdir(parents=True, exist_ok=True)


# Prevent accidental duplication if the script is run again
existing_files = [
    file
    for file in DEST_DIR.rglob("*")
    if file.is_file()
]

if existing_files:
    raise RuntimeError(
        "Destination dataset already contains files.\n"
        "Please verify the dataset before running the script again."
    )


# ============================================================
# FIND CLASSES
# ============================================================

class_dirs = sorted(
    [
        directory
        for directory in SOURCE_DIR.iterdir()
        if directory.is_dir()
    ]
)

print("=" * 60)
print("PLANT DISEASE DATASET PREPARATION")
print("=" * 60)

print(f"Source: {SOURCE_DIR}")
print(f"Destination: {DEST_DIR}")
print(f"Classes found: {len(class_dirs)}")
print(f"Random seed: {SEED}")
print()


# ============================================================
# SPLIT DATA
# ============================================================

random_generator = random.Random(SEED)

total_train = 0
total_validation = 0
total_test = 0
total_images = 0


for class_dir in class_dirs:

    class_name = class_dir.name

    # Get all files belonging to this class
    files = sorted(
        [
            file
            for file in class_dir.iterdir()
            if file.is_file()
        ]
    )

    # Shuffle deterministically
    random_generator.shuffle(files)

    total = len(files)

    # 80 / 10 / 10 split
    train_count = int(total * 0.80)
    validation_count = int(total * 0.10)
    test_count = total - train_count - validation_count

    train_files = files[:train_count]

    validation_files = files[
        train_count:train_count + validation_count
    ]

    test_files = files[
        train_count + validation_count:
    ]

    # Create destination class folders
    train_class_dir = DEST_DIR / "train" / class_name
    validation_class_dir = DEST_DIR / "validation" / class_name
    test_class_dir = DEST_DIR / "test" / class_name

    train_class_dir.mkdir(parents=True, exist_ok=True)
    validation_class_dir.mkdir(parents=True, exist_ok=True)
    test_class_dir.mkdir(parents=True, exist_ok=True)

    # Copy training images
    for file in train_files:
        shutil.copy2(
            file,
            train_class_dir / file.name
        )

    # Copy validation images
    for file in validation_files:
        shutil.copy2(
            file,
            validation_class_dir / file.name
        )

    # Copy test images
    for file in test_files:
        shutil.copy2(
            file,
            test_class_dir / file.name
        )

    total_train += len(train_files)
    total_validation += len(validation_files)
    total_test += len(test_files)
    total_images += total

    print(
        f"{class_name}: "
        f"{len(train_files)} train | "
        f"{len(validation_files)} validation | "
        f"{len(test_files)} test"
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 60)
print("DATASET SPLIT COMPLETE")
print("=" * 60)

print(f"Total images:       {total_images}")
print(f"Training images:    {total_train}")
print(f"Validation images:  {total_validation}")
print(f"Test images:        {total_test}")

print()
print(
    f"Check: "
    f"{total_train} + {total_validation} + {total_test} "
    f"= {total_train + total_validation + total_test}"
)

print()
print("Original PlantVillage dataset was not modified.")
print("=" * 60)