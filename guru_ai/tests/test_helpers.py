from core.ingestion import safe_filename


def test_safe_filename_removes_path_traversal():
    assert safe_filename("../../scheme.pdf") == "scheme.pdf"


def test_safe_filename_handles_empty_name():
    assert safe_filename("  ") == "uploaded_document.pdf"
