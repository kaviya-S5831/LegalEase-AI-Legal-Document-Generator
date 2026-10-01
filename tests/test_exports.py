from backend.services.document_export import format_docx, format_pdf, format_txt


def test_txt_export():
    result = format_txt("Hello legal draft.")
    assert result == b"Hello legal draft."


def test_docx_export():
    result = format_docx("1. Definitions\nThis is a draft.", "NDA")
    assert result.startswith(b"PK")


def test_pdf_export():
    result = format_pdf("1. Definitions\nThis is a draft.", "NDA")
    assert result.startswith(b"%PDF")
