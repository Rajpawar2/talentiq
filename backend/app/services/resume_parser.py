import io
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import Tuple, Dict, Any
from pypdf import PdfReader
from app.ai.factory import get_ai_provider

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text content from a PDF file."""
    reader = PdfReader(io.BytesIO(file_bytes))
    extracted = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted.append(text)
    return "\n".join(extracted).strip()

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extracts text content from a DOCX file using standard library zipfile and XML."""
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
        if "word/document.xml" not in z.namelist():
            raise ValueError("Invalid DOCX format: missing word/document.xml")
        xml_content = z.read("word/document.xml")
        tree = ET.fromstring(xml_content)
        
        paragraphs = []
        for elem in tree.iter():
            if elem.tag.endswith('p'):
                p_text = "".join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text])
                if p_text.strip():
                    paragraphs.append(p_text.strip())
        
        if paragraphs:
            return "\n".join(paragraphs).strip()
        
        # Fallback to text nodes directly
        texts = [node.text for node in tree.iter() if node.text and node.tag.endswith('t')]
        if texts:
            return " ".join(texts).strip()
        return " ".join([node.text for node in tree.iter() if node.text]).strip()

def clean_extracted_text(text: str) -> str:
    """Normalizes whitespace and removes extraneous unprintable characters."""
    text = re.sub(r'[\r\t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()

def parse_resume_content(file_bytes: bytes, filename: str) -> Tuple[str, Dict[str, Any]]:
    """
    Parses resume binary, extracts clean text, and runs structural AI analysis.
    Returns (cleaned_text, parsed_data).
    """
    ext = filename.lower().split(".")[-1] if "." in filename else ""
    raw_text = ""

    if ext == "pdf":
        try:
            raw_text = extract_text_from_pdf(file_bytes)
        except Exception as e:
            raise ValueError(f"Could not read PDF document: {str(e)}")
    elif ext == "docx":
        try:
            raw_text = extract_text_from_docx(file_bytes)
        except Exception as e:
            raise ValueError(f"Could not read DOCX document: {str(e)}")
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Only PDF and DOCX are supported.")

    cleaned_text = clean_extracted_text(raw_text)
    if not cleaned_text or len(cleaned_text) < 10:
        raise ValueError("Could not extract readable text from the uploaded document. Document might be empty or image-only.")

    ai_provider = get_ai_provider()
    parsed_data = ai_provider.analyze_resume(cleaned_text)
    
    return cleaned_text, parsed_data
