import re
import nltk
import fitz
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import io
import textwrap

nltk.download("punkt_tab")
nltk.download('punkt')
nltk.download('stopwords')

stop_words  = set(stopwords.words("english"))

def preprocess(text: str) -> list[str]:
    words = word_tokenize(text.lower())
    return [w for w in words if w.isalnum() and w not in stop_words]

def extract_text(pdf) -> list[str]:
    text = []
    with fitz.open(stream=pdf.read(), filetype="pdf") as doc:
        for page in doc:
            text.append(page.get_text())
    return text

def split_paragraphs(text):
    txt = text.replace('\r\n', '\n').replace('\r', '\n')
    paras = re.split(r'\n\s*\n+', txt)
    paras = [p.strip() for p in paras if p.strip()]
    return paras

def chunk_text(pages: list[str], min_chars: int = 50):
    all_chunks = []

    for page_no, page_text in enumerate(pages):
        paras = split_paragraphs(page_text)
        buffer = ""
        for p in paras:
            if len(p) < min_chars:
                buffer += " " + p
            else:
                chunk = (buffer + " " + p).strip()
                all_chunks.append({
                    "page": page_no + 1,
                    "text": chunk.replace("\n", " ")
                })
                buffer = ""
        if buffer:
            all_chunks.append({
                "page": page_no + 1,
                "text": buffer.strip().replace("\n", " ")
            })
            buffer = ""
    return all_chunks

def find_best_match(question: str, chunks: list[list[dict]]):
    words = set(preprocess(question))
    scores = []

    for file_idx, file in enumerate(chunks):
        for chunk in file:
            chunk_words = set(preprocess(chunk["text"]))
            score = len(words & chunk_words)
            s = {
                'page': chunk["page"],
                'text': chunk["text"],
                'score': score,
                'file_idx': file_idx
            }
            scores.append(s)

    sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
    best_chunk = sorted_scores[0]
    second_best_chunk = sorted_scores[1] if len(sorted_scores) > 1 else None
    print(f"Best chunk score: {best_chunk['score']}, Second best chunk score: {second_best_chunk['score'] if second_best_chunk else 'N/A'}")
    if second_best_chunk and second_best_chunk['score'] >= 0.7 * best_chunk['score']:
        print("Returning two best chunks")
        return (best_chunk, second_best_chunk)
    return best_chunk

# ---Exports finctions---
def export_txt(history):
    buffer = io.StringIO()
    for i, item in enumerate(history, 1):
        buffer.write(f"Q{i}: {item['question']}\n")
        buffer.write(f"File: {item['file']}\n")
        buffer.write(f"Page: {item['page']} - {item['chunk']}\n\n")
        buffer.write(f"A: {item['answer']}\n\n")
    mime = "text/plain"
    file_ext = "txt"

    return buffer.getvalue(), mime, file_ext

def export_pdf(history):
    doc = fitz.open()
    page = doc.new_page()
    y = 72
    margin = 72
    max_y = 792 - margin  # Typical A4 height - bottom margin
    line_height = 15
    max_width = 450  # Adjust if needed for your font size

    def write_wrapped_text(page, text, x, y):
        lines = textwrap.wrap(text, width=90)  # Adjust width to fit the page
        for line in lines:
            if y > max_y:
                return line, True  # Need new page
            page.insert_text((x, y), line)
            y += line_height
        return "", y

    for i, item in enumerate(history, 1):
        for content in [
            f"Q{i}: {item['question']}",
            f"A: {item['answer']}",
            f"File: {item['file']}",
            f"{item['page']} {item['chunk']}",
            ""
        ]:
            wrapped, result = write_wrapped_text(page, content, margin, y)
            if result is True:
                page = doc.new_page()
                y = margin
                # Re-insert the last line on the new page
                if wrapped:
                    page.insert_text((margin, y), wrapped)
                    y += line_height
            else:
                y = result
            y += 5  # Small spacing between sections

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    mime = "application/pdf"
    file_ext = "pdf"
    return buffer.getvalue(), mime, file_ext

def export_markdown(history):
    buffer = io.StringIO()
    for i, item in enumerate(history, 1):
        buffer.write(f"**Q{i}:** {item['question']}\n\n")
        buffer.write(f"**A:** {item['answer']}\n\n")
        buffer.write(f"**File:** {item['file']}\n")
        buffer.write(f"**Page {item['page']}:** {item['chunk']}\n\n")
        buffer.write("---\n\n")
    mime = "text/markdown"
    file_ext = "md"

    return buffer.getvalue(), mime, file_ext