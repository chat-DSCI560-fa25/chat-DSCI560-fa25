from pathlib import Path
import io
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from pathlib import Path
import re, csv
from PyPDF2 import PdfReader

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


#PDF Exploration Part Begins
#Regular Expression for common stuff
DATE  = re.compile(r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:,\s*\d{2,4})?", re.I)
EMAIL = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
OFFICE= re.compile(r"office\s*hours?\s*[:\-]?\s*([^\n\r]+)", re.I)

#Read all text from a PDF using PyPDF2.
def _read_pdf_text(pdf_path: Path) -> str:
    try:
        reader = PdfReader(str(pdf_path))
        return "\n".join([(p.extract_text() or "") for p in reader.pages])
    except Exception as e:
        # Returning empty if failure
        return ""


#HW check
def _is_homework(filename: str, text: str) -> bool:
    name = filename.lower()
    t = text.lower()
    return name.startswith("hw") or "homework" in t or re.search(r"\bhw\s*\d+\b", t) is not None


#Pull three things for homework pdf due date,no of problems and points
def _extract_hw_fields(text: str):
    # due date
    due = ""
    m_due_line = re.search(r"(due\s*(?:by|date|:|-)\s*)(.+)", text, re.I)
    if m_due_line:
        rhs = m_due_line.group(2)[:60]
        m_dt = DATE.search(rhs)
        due = m_dt.group(0) if m_dt else rhs.strip().split("\n")[0][:50]
    if not due:
        m_dt2 = DATE.search(text)
        due = m_dt2.group(0) if m_dt2 else ""

    # points
    pts = ""
    m_pts = re.search(r"(total\s+points?|points?)\s*[:\-]?\s*(\d{1,4})", text, re.I)
    if m_pts:
        pts = m_pts.group(2)

    # problems
    probs = ""
    m_probs = re.search(r"total\s+(\d{1,3})\s+(problems?|questions?)", text, re.I)
    if m_probs:
        probs = m_probs.group(1)
    else:
        # fallback: count lines that look like "1. ..." or "Problem 1"
        probs = str(len(re.findall(r"^\s*(?:\d+\.\s|\bProblem\s*\d+)", text, re.M))) or ""

    return due, pts, probs

#Common stuff like, email,office hours etc
def _extract_common_meta(text: str):
    emails = "; ".join(sorted(set(EMAIL.findall(text)))[:10])
    m_off = OFFICE.search(text)
    office = (m_off.group(1).strip() if m_off else "")
    return emails, office


#Exploration of pdfs individually
def explore_pdfs_min(data_dir: Path) -> Path:    
    pdfs = sorted(list(data_dir.glob("*.pdf")) + list(data_dir.glob("*/*.pdf")))
    out = data_dir / "pdf_summary_min.csv"

    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["file","type","due_date","total_points","num_problems","emails","office_hours","preview"])

        for p in pdfs:
            txt = _read_pdf_text(p)

            # homework vs syllabus vs other pdfs
            lower_text = txt.lower()
            if _is_homework(p.name, txt):
                typ = "homework"
            elif "office hours" in lower_text or "syllabus" in lower_text or "course schedule" in lower_text:
                typ = "syllabus"
            else:
                typ = "other"

            # fields
            if typ == "homework":
                due, pts, probs = _extract_hw_fields(txt)
            else:
                due, pts, probs = "", "", ""

            emails, office = _extract_common_meta(txt)
            preview = " ".join(txt.split())[:180]  # tiny sanity check of content

            w.writerow([p.name, typ, due, pts, probs, emails, office, preview])

    return out



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


    #PDF Exploration
    data_dir = Path(__file__).resolve().parent.parent / "data" 
    print("\n--- PDF exploration ---")
    pdf_csv_path = explore_pdfs_min(data_dir)
    print(f"[pdf] wrote {pdf_csv_path}")

if __name__ == "__main__":
    main()
