import io
from PyPDF2 import PdfReader


def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Extracts raw text from an uploaded file based on its extension.
    Supports PDF, TXT, and MD.
    """
    extension = filename.lower().rsplit(".", 1)[-1]

    if extension == "pdf":
        reader = PdfReader(io.BytesIO(file_bytes))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text

    elif extension in ("txt", "md"):
        return file_bytes.decode("utf-8", errors="ignore")

    else:
        raise ValueError(f"Unsupported file type: .{extension}")