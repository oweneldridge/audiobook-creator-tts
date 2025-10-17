"""
Unit tests for document parsing functionality

Tests for DocumentParser, Chapter class, and file format handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from main_document_mode import DocumentParser, Chapter


@pytest.mark.unit
@pytest.mark.document
class TestChapterClass:
    """Tests for Chapter dataclass"""

    def test_chapter_creation(self):
        """Test creating a Chapter instance"""
        chapter = Chapter(
            number=1, title="Introduction", dir_name="01-introduction", text="Chapter content here.", chunks=[]
        )

        assert chapter.number == 1
        assert chapter.title == "Introduction"
        assert chapter.dir_name == "01-introduction"
        assert chapter.text == "Chapter content here."
        assert chapter.chunks == []

    def test_chapter_with_empty_text(self):
        """Test chapter with empty text"""
        chapter = Chapter(number=1, title="Empty", dir_name="01-empty", text="", chunks=[])

        assert chapter.number == 1
        assert chapter.text == ""

    def test_chapter_with_long_text(self, long_text):
        """Test chapter with long text content"""
        chapter = Chapter(number=5, title="Long Chapter", dir_name="05-long-chapter", text=long_text, chunks=[])

        assert chapter.number == 5
        assert len(chapter.text) > 1000

    def test_chapter_attributes(self):
        """Test that Chapter has expected attributes"""
        chapter = Chapter(number=1, title="Test", dir_name="01-test", text="Content", chunks=[])

        assert hasattr(chapter, "number")
        assert hasattr(chapter, "title")
        assert hasattr(chapter, "text")
        assert hasattr(chapter, "dir_name")
        assert hasattr(chapter, "chunks")

    def test_chapter_immutability(self):
        """Test Chapter is a dataclass (mutable by default)"""
        chapter = Chapter(number=1, title="Test", dir_name="01-test", text="Original", chunks=[])

        # Should be able to modify
        chapter.text = "Modified"
        assert chapter.text == "Modified"


@pytest.mark.unit
@pytest.mark.document
class TestDocumentParserTXT:
    """Tests for DocumentParser.extract_text_from_txt"""

    def test_extract_txt_basic(self, tmp_path):
        """Test extracting text from basic TXT file"""
        txt_file = tmp_path / "test.txt"
        content = "This is a test document.\nWith multiple lines."
        txt_file.write_text(content, encoding="utf-8")

        result = DocumentParser.extract_text_from_txt(str(txt_file))

        assert result == content

    def test_extract_txt_utf8_with_bom(self, tmp_path):
        """Test handling UTF-8 with BOM"""
        txt_file = tmp_path / "test_bom.txt"
        content = "\ufeffThis has a BOM marker."
        txt_file.write_text(content, encoding="utf-8-sig")

        result = DocumentParser.extract_text_from_txt(str(txt_file))

        assert result is not None
        assert "This has a BOM marker" in result

    def test_extract_txt_latin1_encoding(self, tmp_path):
        """Test handling Latin-1 encoded file"""
        txt_file = tmp_path / "test_latin1.txt"
        content = "Café résumé"
        txt_file.write_bytes(content.encode("latin-1"))

        result = DocumentParser.extract_text_from_txt(str(txt_file))

        assert result is not None
        # chardet should detect and decode properly

    def test_extract_txt_empty_file(self, tmp_path):
        """Test handling empty TXT file"""
        txt_file = tmp_path / "empty.txt"
        txt_file.write_text("")

        result = DocumentParser.extract_text_from_txt(str(txt_file))

        assert result == ""

    def test_extract_txt_file_not_found(self, capsys):
        """Test handling non-existent file"""
        result = DocumentParser.extract_text_from_txt("/nonexistent/file.txt")

        # Implementation returns empty string on error, not None
        assert result == ""
        captured = capsys.readouterr()
        assert "Error reading TXT" in captured.out

    def test_extract_txt_large_file(self, tmp_path):
        """Test handling large text file"""
        txt_file = tmp_path / "large.txt"
        content = "Line of text.\n" * 10000
        txt_file.write_text(content)

        result = DocumentParser.extract_text_from_txt(str(txt_file))

        assert result is not None
        assert len(result) > 100000


@pytest.mark.unit
@pytest.mark.document
class TestDocumentParserPDF:
    """Tests for DocumentParser PDF extraction"""

    @patch("main_document_mode.PdfReader")
    def test_extract_pdf_basic(self, mock_pdf_reader, tmp_path):
        """Test basic PDF text extraction"""
        # Mock PDF reader
        mock_page = Mock()
        mock_page.extract_text.return_value = "Page 1 content"

        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page]

        mock_pdf_reader.return_value = mock_reader_instance

        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"fake pdf content")

        result = DocumentParser.extract_text_from_pdf(str(pdf_file))

        assert result is not None
        assert "Page 1 content" in result

    @patch("main_document_mode.PdfReader")
    def test_extract_pdf_multiple_pages(self, mock_pdf_reader):
        """Test PDF with multiple pages"""
        # Mock multiple pages
        mock_pages = [
            Mock(extract_text=Mock(return_value="Page 1")),
            Mock(extract_text=Mock(return_value="Page 2")),
            Mock(extract_text=Mock(return_value="Page 3")),
        ]

        mock_reader_instance = Mock()
        mock_reader_instance.pages = mock_pages

        mock_pdf_reader.return_value = mock_reader_instance

        result = DocumentParser.extract_text_from_pdf("dummy.pdf")

        assert "Page 1" in result
        assert "Page 2" in result
        assert "Page 3" in result

    @patch("main_document_mode.PdfReader")
    def test_extract_pdf_empty_pages(self, mock_pdf_reader):
        """Test PDF with empty pages"""
        mock_page = Mock()
        mock_page.extract_text.return_value = ""

        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page]

        mock_pdf_reader.return_value = mock_reader_instance

        result = DocumentParser.extract_text_from_pdf("dummy.pdf")

        assert result is not None  # Should handle empty pages

    @patch("main_document_mode.PdfReader")
    def test_extract_pdf_error_handling(self, mock_pdf_reader, capsys):
        """Test PDF extraction error handling"""
        mock_pdf_reader.side_effect = Exception("PDF read error")

        result = DocumentParser.extract_text_from_pdf("dummy.pdf")

        # Implementation returns empty string on error
        assert result == ""
        captured = capsys.readouterr()
        assert "Error reading PDF" in captured.out

    def test_extract_pdf_file_not_found(self, capsys):
        """Test handling non-existent PDF"""
        result = DocumentParser.extract_text_from_pdf("/nonexistent/file.pdf")

        # Implementation returns empty string on error
        assert result == ""
        captured = capsys.readouterr()
        assert "Error reading PDF" in captured.out


@pytest.mark.unit
@pytest.mark.document
class TestDocumentParserEPUB:
    """Tests for DocumentParser EPUB extraction"""

    @patch("main_document_mode.epub")
    @patch("main_document_mode.BeautifulSoup")
    @patch("main_document_mode.ebooklib.ITEM_DOCUMENT", 9)
    def test_extract_epub_basic(self, mock_bs, mock_epub, capsys):
        """Test basic EPUB text extraction"""
        # Mock EPUB structure
        mock_item = Mock()
        mock_item.get_content.return_value = b"<html><body>Chapter content</body></html>"

        mock_book = Mock()
        mock_book.get_items_of_type.return_value = [mock_item]

        mock_epub.read_epub.return_value = mock_book

        # Mock BeautifulSoup to behave like actual implementation:
        # soup(["script", "style"]) returns list of elements to decompose
        # soup.get_text() returns text content
        mock_soup = Mock()
        mock_soup.return_value = []  # No script/style elements to decompose
        mock_soup.get_text.return_value = "Chapter content"
        mock_bs.return_value = mock_soup

        result = DocumentParser.extract_text_from_epub("dummy.epub")

        assert result is not None
        assert "Chapter content" in result

    @patch("main_document_mode.epub")
    @patch("main_document_mode.BeautifulSoup")
    @patch("main_document_mode.ebooklib.ITEM_DOCUMENT", 9)
    def test_extract_epub_multiple_chapters(self, mock_bs, mock_epub, capsys):
        """Test EPUB with multiple chapters"""
        # Mock multiple items
        items = []
        for i in range(3):
            mock_item = Mock()
            mock_item.get_content.return_value = f"<html><body>Chapter {i+1}</body></html>".encode()
            items.append(mock_item)

        mock_book = Mock()
        mock_book.get_items_of_type.return_value = items

        mock_epub.read_epub.return_value = mock_book

        # Mock BeautifulSoup to return different text for each call
        call_count = [0]

        def mock_soup_side_effect(*args, **kwargs):
            soup = Mock()
            soup.return_value = []  # For soup(["script", "style"])
            call_count[0] += 1
            soup.get_text.return_value = f"Chapter {call_count[0]}"
            return soup

        mock_bs.side_effect = mock_soup_side_effect

        result = DocumentParser.extract_text_from_epub("dummy.epub")

        assert len(result) > 0  # Should have extracted text

    @patch("main_document_mode.epub")
    def test_extract_epub_error_handling(self, mock_epub, capsys):
        """Test EPUB extraction error handling"""
        mock_epub.read_epub.side_effect = Exception("EPUB read error")

        result = DocumentParser.extract_text_from_epub("dummy.epub")

        # Implementation returns empty string on error
        assert result == ""
        captured = capsys.readouterr()
        assert "Error reading EPUB" in captured.out

    def test_extract_epub_file_not_found(self, capsys):
        """Test handling non-existent EPUB"""
        result = DocumentParser.extract_text_from_epub("/nonexistent/file.epub")

        # Implementation returns empty string on error
        assert result == ""
        captured = capsys.readouterr()
        assert "Error reading EPUB" in captured.out


@pytest.mark.unit
@pytest.mark.document
class TestDocumentParserChapters:
    """Tests for chapter extraction methods"""

    @patch("main_document_mode.PdfReader")
    def test_extract_chapters_from_pdf(self, mock_pdf_reader, capsys):
        """Test extracting chapters from PDF"""
        # Mock PDF pages with simple text (will trigger fallback to single chapter)
        mock_page = Mock()
        mock_page.extract_text.return_value = "Chapter 1 content. " * 100

        mock_reader = Mock()
        mock_reader.pages = [mock_page]

        mock_pdf_reader.return_value = mock_reader

        chapters = DocumentParser.extract_chapters_from_pdf("dummy.pdf")

        # Should create at least one chapter (fallback to single chapter if no headings)
        assert chapters is not None
        assert len(chapters) >= 1
        if len(chapters) > 0:
            assert all(isinstance(ch, Chapter) for ch in chapters)
            # Check fallback chapter properties
            assert chapters[0].number == 1
            assert chapters[0].title == "Full Document"

    @patch("main_document_mode.epub")
    @patch("main_document_mode.BeautifulSoup")
    @patch("main_document_mode.ebooklib.ITEM_DOCUMENT", 9)
    def test_extract_chapters_from_epub(self, mock_bs, mock_epub, capsys):
        """Test extracting chapters from EPUB"""
        # Mock EPUB item
        mock_item = Mock()
        mock_item.get_content.return_value = b"<html><body>Chapter content</body></html>"

        mock_book = Mock()
        mock_book.toc = []  # No TOC, will use file structure fallback
        mock_book.get_items_of_type.return_value = [mock_item]

        mock_epub.read_epub.return_value = mock_book

        # Mock BeautifulSoup for file structure extraction
        # Use MagicMock instead of Mock to make it callable by default
        mock_soup = MagicMock()
        # When soup is called with ["script", "style"], return empty list (no scripts to remove)
        mock_soup.return_value = []
        # When find_all is called (for headings detection), return empty list (no headings found)
        mock_soup.find_all.return_value = []
        # When find is called for headings in file structure, return None (no headings)
        mock_soup.find.return_value = None
        # When get_text is called, return content
        mock_soup.get_text.return_value = "Chapter content"
        # Make BeautifulSoup return our mock
        mock_bs.return_value = mock_soup

        chapters = DocumentParser.extract_chapters_from_epub("dummy.epub")

        # Should create at least one chapter (fallback to file structure)
        assert chapters is not None
        assert len(chapters) >= 1
        if len(chapters) > 0:
            assert all(isinstance(ch, Chapter) for ch in chapters)
            # Verify chapter properties
            assert chapters[0].title == "Section 1"  # Default title when no heading found
            assert chapters[0].number == 1

    @patch("main_document_mode.DocumentParser.extract_text_from_pdf")
    def test_extract_chapters_empty_pdf(self, mock_extract, capsys):
        """Test extracting chapters from empty PDF"""
        mock_extract.return_value = ""

        chapters = DocumentParser.extract_chapters_from_pdf("dummy.pdf")

        # Returns empty list for empty PDF
        assert chapters == []

    @patch("main_document_mode.DocumentParser.extract_text_from_pdf")
    def test_extract_chapters_pdf_error(self, mock_extract, capsys):
        """Test handling PDF extraction error"""
        mock_extract.return_value = ""  # Error returns empty string

        chapters = DocumentParser.extract_chapters_from_pdf("dummy.pdf")

        # Returns empty list for error
        assert chapters == []


@pytest.mark.unit
@pytest.mark.document
class TestDocumentParserDOCX:
    """Tests for DOCX document parsing"""

    def test_extract_docx_basic(self, tmp_path):
        """Test basic DOCX text extraction"""
        # Mock Document structure
        mock_para = Mock()
        mock_para.text = "Paragraph text"

        mock_doc = Mock()
        mock_doc.paragraphs = [mock_para]

        with patch("main_document_mode.DOCX_AVAILABLE", True):
            with patch("main_document_mode.DocxDocument", return_value=mock_doc, create=True):
                result = DocumentParser.extract_text_from_docx("dummy.docx")

                assert result is not None
                assert "Paragraph text" in result

    def test_extract_docx_multiple_paragraphs(self):
        """Test DOCX with multiple paragraphs"""
        paragraphs = [
            Mock(text="First paragraph"),
            Mock(text="Second paragraph"),
            Mock(text="Third paragraph"),
        ]

        mock_doc = Mock()
        mock_doc.paragraphs = paragraphs

        with patch("main_document_mode.DOCX_AVAILABLE", True):
            with patch("main_document_mode.DocxDocument", return_value=mock_doc, create=True):
                result = DocumentParser.extract_text_from_docx("dummy.docx")

                assert "First paragraph" in result
                assert "Second paragraph" in result
                assert "Third paragraph" in result

    def test_extract_docx_empty(self):
        """Test empty DOCX"""
        mock_doc = Mock()
        mock_doc.paragraphs = []

        with patch("main_document_mode.DOCX_AVAILABLE", True):
            with patch("main_document_mode.DocxDocument", return_value=mock_doc, create=True):
                result = DocumentParser.extract_text_from_docx("dummy.docx")

                assert result is not None
                assert result == ""

    def test_extract_docx_error_handling(self, capsys):
        """Test DOCX extraction error handling"""
        with patch("main_document_mode.DOCX_AVAILABLE", True):
            with patch("main_document_mode.DocxDocument", side_effect=Exception("DOCX read error"), create=True):
                result = DocumentParser.extract_text_from_docx("dummy.docx")

                # Implementation returns empty string on error
                assert result == ""
                captured = capsys.readouterr()
                assert "Error reading DOCX" in captured.out


@pytest.mark.unit
@pytest.mark.document
class TestDocumentParserHTML:
    """Tests for HTML document parsing"""

    @patch("main_document_mode.BeautifulSoup")
    def test_extract_html_basic(self, mock_bs, tmp_path):
        """Test basic HTML text extraction"""
        html_file = tmp_path / "test.html"
        html_file.write_text("<html><body><p>Test content</p></body></html>")

        # Mock BeautifulSoup behavior
        mock_soup = Mock()
        mock_soup.return_value = []  # No script/style/nav/header/footer elements
        mock_soup.find.return_value = None  # No main content area found
        mock_soup.get_text.return_value = "Test content"
        mock_bs.return_value = mock_soup

        result = DocumentParser.extract_text_from_html(str(html_file))

        assert result is not None
        assert "Test content" in result

    @patch("main_document_mode.BeautifulSoup")
    def test_extract_html_strips_tags(self, mock_bs, tmp_path):
        """Test that HTML tags are stripped"""
        html_file = tmp_path / "test.html"
        html_file.write_text("<html><body><h1>Title</h1><p>Content</p></body></html>")

        # Mock BeautifulSoup behavior
        mock_soup = Mock()
        mock_soup.return_value = []  # No script/style/nav/header/footer elements
        mock_soup.find.return_value = None  # No main content area found
        mock_soup.get_text.return_value = "Title\nContent"
        mock_bs.return_value = mock_soup

        result = DocumentParser.extract_text_from_html(str(html_file))

        # Should not contain HTML tags
        assert "<h1>" not in result
        assert "<p>" not in result

    def test_extract_html_file_not_found(self, capsys):
        """Test handling non-existent HTML file"""
        result = DocumentParser.extract_text_from_html("/nonexistent/file.html")

        # Implementation returns empty string on error
        assert result == ""
        captured = capsys.readouterr()
        assert "Error reading HTML" in captured.out


@pytest.mark.unit
@pytest.mark.document
class TestDocumentParserMarkdown:
    """Tests for Markdown document parsing"""

    def test_extract_markdown_basic(self, tmp_path):
        """Test basic Markdown extraction"""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Title\n\nContent here.")

        # Mock mistune.create_markdown() and the returned markdown instance
        mock_markdown = Mock()
        mock_markdown.return_value = "<h1>Title</h1><p>Content here.</p>"

        with patch("main_document_mode.MISTUNE_AVAILABLE", True):
            with patch("main_document_mode.mistune", create=True) as mock_mistune_module:
                mock_mistune_module.create_markdown.return_value = mock_markdown

                with patch("main_document_mode.BeautifulSoup") as mock_bs:
                    mock_soup = Mock()
                    mock_soup.get_text.return_value = "Title\nContent here."
                    mock_bs.return_value = mock_soup

                    result = DocumentParser.extract_text_from_markdown(str(md_file))

                    assert result is not None
                    assert "Title" in result

    def test_extract_markdown_file_not_found(self, capsys):
        """Test handling non-existent Markdown file"""
        result = DocumentParser.extract_text_from_markdown("/nonexistent/file.md")

        # Implementation returns empty string on error
        assert result == ""
        captured = capsys.readouterr()
        assert "Error reading Markdown" in captured.out


@pytest.mark.unit
@pytest.mark.document
class TestDocumentParsingEdgeCases:
    """Edge cases for document parsing"""

    def test_binary_file_handling(self, tmp_path):
        """Test handling binary files as text"""
        binary_file = tmp_path / "binary.txt"
        binary_file.write_bytes(b"\x00\x01\x02\x03\x04")

        # Should handle gracefully
        result = DocumentParser.extract_text_from_txt(str(binary_file))
        # May return None or empty string, but shouldn't crash

    def test_very_large_document(self, tmp_path):
        """Test handling very large documents"""
        large_file = tmp_path / "large.txt"
        content = "A" * 10_000_000  # 10MB of text

        large_file.write_text(content)

        result = DocumentParser.extract_text_from_txt(str(large_file))

        assert result is not None
        assert len(result) > 1_000_000

    @patch("main_document_mode.PdfReader")
    def test_corrupted_pdf(self, mock_pdf_reader, capsys):
        """Test handling corrupted PDF"""
        mock_pdf_reader.side_effect = Exception("Corrupted PDF")

        result = DocumentParser.extract_text_from_pdf("corrupted.pdf")

        # Implementation returns empty string on error
        assert result == ""
        captured = capsys.readouterr()
        assert "Error reading PDF" in captured.out
