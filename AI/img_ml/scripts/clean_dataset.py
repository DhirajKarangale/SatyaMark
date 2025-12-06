import os
from PIL import Image
import shutil

AI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATASET_DIR = os.path.join(AI_DIR, "dataset", "train")

def is_valid_image(path):
    try:
        Image.open(path).verify()
        return True
    except Exception:
        return False

def clean_folder(folder):
    print(f"\nChecking folder: {folder}")
    valid = 0
    removed = 0
    for fname in os.listdir(folder):
        fpath = os.path.join(folder, fname)

        # skip if not a file
        if not os.path.isfile(fpath):
            continue

        # remove files with invalid filename characters
        bad_chars = ['?', '*', '<', '>', '|', ':', '"', '\\', '/', ' ']
        if any(c in fname for c in bad_chars) or fname.startswith('.'):
            print("Removing bad filename:", fname)
            os.remove(fpath)
            removed += 1
            continue

        # remove corrupted images
        if not is_valid_image(fpath):
            print("Removing corrupted:", fname)
            os.remove(fpath)
            removed += 1
            continue

        valid += 1

    print(f"Valid: {valid}, Removed: {removed}")

def main():
    for cls in ["real", "ai"]:
        folder = os.path.join(DATASET_DIR, cls)
        if os.path.isdir(folder):
            clean_folder(folder)
        else:
            print("Folder missing:", folder)

if __name__ == "__main__":
    main()
