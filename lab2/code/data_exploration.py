from pathlib import Path
import io
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

def find_csv(data_dir: Path) -> Path:
    # Look for CSV in data/ and one level below (in case unzip created a subfolder)
    candidates = list(data_dir.glob("*.csv")) + list(data_dir.glob("*/*.csv"))
    if not candidates:
        raise FileNotFoundError("No CSV found in lab2/data. Download first.")
    # Prefer a file that looks like the student scores dataset
    preferred = [p for p in candidates if "student" in p.name.lower() and "score" in p.name.lower()]
    return preferred[0] if preferred else candidates[0]

def scrape_stackexchange(pages=2):
    """
    Scrape Math StackExchange questions + top answers.
    pages = number of listing pages to scrape
    """
    base_url = "https://math.stackexchange.com"
    qna_data = []

    for page in range(1, pages + 1):
        print(f"Scraping page {page}...")
        url = f"{base_url}/questions?tab=Active&page={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract question links
        question_links = [
            base_url + q["href"]
            for q in soup.select(".s-post-summary--content-title a")
        ]

        # Visit each question to extract question + top answer
        for link in question_links[:5]:  # limit to 5 per page to avoid long runtime
            try:
                q_res = requests.get(link)
                q_soup = BeautifulSoup(q_res.text, "html.parser")

                # Question
                q_title = q_soup.select_one("h1").get_text(strip=True)
                q_body = q_soup.select_one(".s-prose").get_text(" ", strip=True)

                # First (top) answer if exists
                ans_elem = q_soup.select_one(".answer .s-prose")
                answer = ans_elem.get_text(" ", strip=True) if ans_elem else None

                qna_data.append({
                    "question_title": q_title,
                    "question_body": q_body,
                    "answer_body": answer,
                    "url": link
                })

                time.sleep(1)  # be polite to server
            except Exception as e:
                print("Error scraping", link, ":", e)

    return pd.DataFrame(qna_data)

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

    print("\n--- ASCII Text (Forum / HTML) Data Exploration ---\n")

    df = scrape_stackexchange(pages=1)  # scrape 1 page

    # Basic exploration
    print("\nFirst 5 Q&A pairs:\n", df.head())
    print("\nDataset shape:", df.shape)
    print("\nMissing values:\n", df.isnull().sum())

    # Save to CSV
    output_dir = Path.home() / "shivani_rajesh_9186135295" / "chat-DSCI560-fa25" / "lab2" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "stackexchange_qna.csv"
    df.to_csv(output_file, index=False)
    print(f"\n[done] Saved forum Q&A to {output_file}")

if __name__ == "__main__":
    main()
