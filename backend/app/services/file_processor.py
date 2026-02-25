import os
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ProcessedFile:
    text: str
    metadata: dict
    content_hash: str


class FileProcessor:
    EXTRACTORS = {
        ".pdf": "_extract_pdf",
        ".docx": "_extract_docx",
        ".doc": "_extract_docx",
        ".txt": "_extract_text",
        ".md": "_extract_text",
        ".py": "_extract_text",
        ".js": "_extract_text",
        ".ts": "_extract_text",
        ".tsx": "_extract_text",
        ".jsx": "_extract_text",
        ".go": "_extract_text",
        ".java": "_extract_text",
        ".rs": "_extract_text",
        ".json": "_extract_text",
        ".csv": "_extract_text",
        ".xml": "_extract_text",
        ".yaml": "_extract_text",
        ".yml": "_extract_text",
        ".png": "_extract_image_ocr",
        ".jpg": "_extract_image_ocr",
        ".jpeg": "_extract_image_ocr",
    }

    async def process_file(self, file_path: str) -> ProcessedFile:
        from app.utils.hashing import compute_file_hash

        path = Path(file_path)
        ext = path.suffix.lower()

        if ext not in self.EXTRACTORS:
            raise ValueError(f"Unsupported file type: {ext}")

        content_hash = compute_file_hash(file_path)
        extractor = getattr(self, self.EXTRACTORS[ext])
        text = extractor(file_path)

        stat = path.stat()
        metadata = {
            "file_name": path.name,
            "file_type": ext.lstrip("."),
            "file_size": stat.st_size,
            "page_count": None,
        }

        if ext == ".pdf":
            metadata["page_count"] = self._get_pdf_page_count(file_path)

        return ProcessedFile(text=text, metadata=metadata, content_hash=content_hash)

    def _extract_text(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    def _extract_pdf(self, file_path: str) -> str:
        from PyPDF2 import PdfReader

        reader = PdfReader(file_path)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)

    def _get_pdf_page_count(self, file_path: str) -> int:
        from PyPDF2 import PdfReader

        reader = PdfReader(file_path)
        return len(reader.pages)

    def _extract_docx(self, file_path: str) -> str:
        from docx import Document

        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)

    def _extract_image_ocr(self, file_path: str) -> str:
        try:
            import pytesseract
            from PIL import Image

            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except ImportError:
            return f"[Image file: {Path(file_path).name} — OCR not available (install pytesseract)]"
        except Exception as e:
            return f"[Image file: {Path(file_path).name} — OCR failed: {e}]"
