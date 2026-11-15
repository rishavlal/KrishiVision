from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

SOURCE_DIR = Path(
    r"C:\Users\risha\Documents\CODING\Minor Project\PlantVillage-Dataset\raw\color"
)

DATASET_DIR = Path(
    r"C:\Users\risha\Documents\CODING\Minor Project\KrishiVision\ml\plant_disease\dataset"
)

SPLITS = ["train", "validation", "test"]


# ============================================================
# FIND ORIGINAL CLASSES
# ============================================================

original_classes = sorted(
    directory.name
    for directory in SOURCE_DIR.iterdir()
    if directory.is_dir()
)


print("=" * 70)
print("PLANT DISEASE DATASET VERIFICATION")
print("=" * 70)

print(f"Original classes found: {len(original_classes)}")
print()


# ============================================================
# CHECK EACH SPLIT
# ============================================================

all_checks_passed = True

split_counts = {}


for split in SPLITS:

    split_dir = DATASET_DIR / split

    print("-" * 70)
    print(f"Checking: {split.upper()}")
    print("-" * 70)

    if not split_dir.exists():
        print(f"ERROR: {split_dir} does not exist.")
        all_checks_passed = False
        continue

    split_classes = sorted(
        directory.name
        for directory in split_dir.iterdir()
        if directory.is_dir()
    )

    print(f"Classes found: {len(split_classes)}")

    # Check class folders
    missing_classes = set(original_classes) - set(split_classes)
    extra_classes = set(split_classes) - set(original_classes)

    if missing_classes:
        print("Missing classes:")
        for class_name in sorted(missing_classes):
            print(f"  - {class_name}")
        all_checks_passed = False

    if extra_classes:
        print("Unexpected classes:")
        for class_name in sorted(extra_classes):
            print(f"  - {class_name}")
        all_checks_passed = False

    # Count images
    counts = {}

    for class_name in original_classes:

        class_dir = split_dir / class_name

        if class_dir.exists():
            image_count = sum(
                1
                for file in class_dir.iterdir()
                if file.is_file()
            )
        else:
            image_count = 0

        counts[class_name] = image_count

    split_counts[split] = counts

    print(f"Images in {split}: {sum(counts.values())}")


# ============================================================
# VERIFY CLASS-WISE TOTALS
# ============================================================

print()
print("=" * 70)
print("CLASS-WISE VERIFICATION")
print("=" * 70)

for class_name in original_classes:

    original_count = sum(
        1
        for file in (SOURCE_DIR / class_name).iterdir()
        if file.is_file()
    )

    train_count = split_counts["train"].get(class_name, 0)
    validation_count = split_counts["validation"].get(class_name, 0)
    test_count = split_counts["test"].get(class_name, 0)

    split_total = (
        train_count
        + validation_count
        + test_count
    )

    if split_total != original_count:
        print(
            f"ERROR: {class_name}\n"
            f"  Original:   {original_count}\n"
            f"  Train:      {train_count}\n"
            f"  Validation: {validation_count}\n"
            f"  Test:       {test_count}\n"
            f"  Split total: {split_total}"
        )

        all_checks_passed = False


# ============================================================
# FINAL TOTALS
# ============================================================

original_total = sum(
    sum(
        1
        for file in class_dir.iterdir()
        if file.is_file()
    )
    for class_dir in SOURCE_DIR.iterdir()
    if class_dir.is_dir()
)

train_total = sum(split_counts["train"].values())
validation_total = sum(split_counts["validation"].values())
test_total = sum(split_counts["test"].values())

split_total = (
    train_total
    + validation_total
    + test_total
)


print()
print("=" * 70)
print("FINAL TOTALS")
print("=" * 70)

print(f"Original dataset: {original_total}")
print(f"Training:         {train_total}")
print(f"Validation:       {validation_total}")
print(f"Test:             {test_total}")
print(f"Combined splits:  {split_total}")

print()
print(
    f"Check: {train_total} + {validation_total} + "
    f"{test_total} = {split_total}"
)


# ============================================================
# FINAL RESULT
# ============================================================

print()
print("=" * 70)

if all_checks_passed and original_total == split_total:
    print("ALL DATASET VERIFICATION CHECKS PASSED")
    print("Dataset split is valid and ready for preprocessing.")
else:
    print("DATASET VERIFICATION FAILED")
    print("Do NOT continue to model training.")

print("=" * 70)