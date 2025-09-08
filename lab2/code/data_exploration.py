from pathlib import Path
import io
import pandas as pd

def find_csv(data_dir: Path) -> Path:
    # Look for CSV in data/ and one level below (in case unzip created a subfolder)
    candidates = list(data_dir.glob("*.csv")) + list(data_dir.glob("*/*.csv"))
    if not candidates:
        raise FileNotFoundError("No CSV found in lab2/data. Download first.")
    # Prefer a file that looks like the student scores dataset
    preferred = [p for p in candidates if "student" in p.name.lower() and "score" in p.name.lower()]
    return preferred[0] if preferred else candidates[0]

def main():
    # This file is at lab2/code/, so data dir is one parent up
    base_dir = Path(__file__).resolve().parents[1]   # .../lab2
    data_dir = base_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    csv_path = find_csv(data_dir)
    print(f"Using CSV: {csv_path}")

    df = pd.read_csv(csv_path)

    print("\n=== HEAD(10) ===")
    print(df.head(10))

    print("\n=== SHAPE ===")
    print(f"rows: {df.shape[0]}, cols: {df.shape[1]}")

    print("\n=== MISSING VALUES PER COLUMN ===")
    print(df.isnull().sum())

    print("\n=== INFO ===")
    buf = io.StringIO()
    df.info(buf=buf)
    info_text = buf.getvalue()
    print(info_text)

    print("\n=== DESCRIBE (numeric) ===")
    print(df.describe())

    # Save an Excel copy and a head(10) preview CSV
    (data_dir / "student_scores.xlsx").write_bytes(b"")  # touch clears if exists
    df.to_excel(data_dir / "student_scores.xlsx", index=False)
    df.head(10).to_csv(data_dir / "student_scores_head10.csv", index=False)

    print("\n[done] Saved files in lab2/data:")
    print("- student_scores.xlsx")
    print("- student_scores_head10.csv")
    print("- _summary.txt")

if __name__ == "__main__":
    main()
