"""Document upload, text extraction (PDF/TXT/MD, optional OCR) and TF-IDF retrieval (RAG sources)."""
import io, re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def _ocr(data):
    try:
        from pdf2image import convert_from_bytes; import pytesseract
        return [pytesseract.image_to_string(im) for im in convert_from_bytes(data)]
    except Exception:
        return []

def read_file(name, data):
    """Return (pages, status). pages = list of text strings."""
    try:
        if name.lower().endswith(".pdf"):
            from pypdf import PdfReader
            pages = [(pg.extract_text() or "") for pg in PdfReader(io.BytesIO(data)).pages]
            if sum(len(p.strip()) for p in pages) < 50:
                o = _ocr(data)
                if o: return o, "Scanned PDF read with OCR"
                return [], "No text found. Scanned PDF: install pytesseract + pdf2image (see requirements.txt)"
            return pages, "Text extracted"
        return [data.decode("utf-8", "ignore")], "Text read"
    except Exception as e:
        return [], f"Could not read file: {e}"

class KnowledgeBase:
    def __init__(self): self.chunks, self.meta, self.docs, self.vec, self.mat = [], [], {}, None, None
    def add(self, name, data):
        pages, status = read_file(name, data); n = 0
        for i, pg in enumerate(pages, 1):
            for part in re.split(r"\n\s*\n", pg):
                part = " ".join(part.split())
                if len(part) > 60: self.chunks.append(part); self.meta.append((name, i)); n += 1
        self.docs[name] = f"{status} ({n} passages)" if n else status
        if self.chunks:
            self.vec = TfidfVectorizer(stop_words="english"); self.mat = self.vec.fit_transform(self.chunks)
    def search(self, query, k=3, min_score=.12):
        if self.mat is None: return []
        s = cosine_similarity(self.vec.transform([query]), self.mat)[0]
        return [{"doc":self.meta[i][0],"page":self.meta[i][1],"text":self.chunks[i],"score":float(s[i])}
                for i in s.argsort()[::-1][:k] if s[i] >= min_score]
