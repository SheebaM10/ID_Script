import os
from pptx import Presentation
from docx import Document
from pdfminer.high_level import extract_text as extract_pdf_text

def extract_text_from_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == '.pptx':
            return extract_from_pptx(filepath)
        elif ext == '.docx':
            return extract_from_docx(filepath)
        elif ext == '.pdf':
            return extract_from_pdf(filepath)
        else:
            return f"[Extraction Error] Unsupported file type: {ext}"
    except Exception as e:
        return f"[Extraction Error] {str(e)}"

def extract_from_pptx(path):
    try:
        prs = Presentation(path)
        slides = []
        for i, slide in enumerate(prs.slides, start=1):
            texts = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    texts.append(shape.text.strip())
                if hasattr(shape, "has_table") and shape.has_table:
                    for row in shape.table.rows:
                        for cell in row.cells:
                            cell_text = cell.text.strip()
                            if cell_text:
                                texts.append(cell_text)
            slide_text = "\n".join(texts)
            slides.append(f"--- Slide {i} ---\n{slide_text}")
        return "\n\n".join(slides).strip()
    except Exception as e:
        return f"[PPTX Extraction Error] {str(e)}"

def extract_from_docx(path):
    try:
        doc = Document(path)
        paragraphs = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    if cell_text:
                        paragraphs.append(cell_text)
        return "\n\n".join(paragraphs)
    except Exception as e:
        return f"[DOCX Extraction Error] {str(e)}"

def extract_from_pdf(path):
    try:
        text = extract_pdf_text(path)
        return text.strip()
    except Exception as e:
        return f"[PDF Extraction Error] {str(e)}"
