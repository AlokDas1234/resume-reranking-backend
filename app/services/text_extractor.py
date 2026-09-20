import fitz  # PyMuPDF
from docx import Document

# def extract_pdf_text(file_path: str) -> str:
#     text = ""
#     pdf = fitz.open(file_path)
#     for page in pdf:
#         text += page.get_text()
#     pdf.close()
#     return text

def extract_pdf_text(file_path: str) -> str:
    text = ""

    pdf = fitz.open(file_path)

    print("Number of pages:", len(pdf))

    for page_number, page in enumerate(pdf):
        page_text = page.get_text()

        print(
            f"Page {page_number + 1} characters:",
            len(page_text)
        )

        text += page_text

    pdf.close()

    print("TOTAL EXTRACTED CHARACTERS:", len(text))

    return text


def extract_docx_text(file_path: str) -> str:
    doc = Document(file_path)
    text = "\n".join(
        paragraph.text
        for paragraph in doc.paragraphs
    )
    return text