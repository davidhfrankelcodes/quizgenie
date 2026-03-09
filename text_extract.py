def extract_text(file_path: str, content_type: str) -> str:
    if content_type == "pdf":
        return _extract_pdf(file_path)
    elif content_type == "docx":
        return _extract_docx(file_path)
    elif content_type == "txt":
        return _extract_txt(file_path)
    else:
        raise ValueError(f"Unsupported content type: {content_type}")


def _extract_pdf(path: str) -> str:
    import pdfplumber
    pages = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
    return "\n\n".join(pages)


def _extract_docx(path: str) -> str:
    from docx import Document
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


def _extract_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()
