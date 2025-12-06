import os, csv

AI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATASET_DIR = os.path.join(AI_DIR, "dataset", "train")
CSV_OUT = os.path.abspath(os.path.join(AI_DIR, "img_ml", "dataset.csv"))

def gather():
    rows = []
    for label_name, label_value in [("real", 0), ("ai", 1)]:
        folder = os.path.join(DATASET_DIR, label_name)
        if not os.path.isdir(folder):
            print("Warning: folder not found:", folder)
            continue
        for root, _, files in os.walk(folder):
            for fname in files:
                if fname.lower().endswith((".jpg",".jpeg",".png",".webp")):
                    path = os.path.abspath(os.path.join(root, fname))
                    rows.append([path, label_value])
    with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["image_path","label"])
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {CSV_OUT}")

if __name__ == "__main__":
    gather()
