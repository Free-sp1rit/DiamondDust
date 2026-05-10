from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from diamonddust.domain.schema import SourceOrigin
from diamonddust.storage.markdown import (
    MarkdownIngestionError,
    compute_content_hash,
    ingest_markdown_text,
    read_markdown_essay,
)


class MarkdownIngestionTests(unittest.TestCase):
    def test_reads_markdown_file_without_mutating_source(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            essay_path = root / "00-inbox" / "my-essay.md"
            essay_path.parent.mkdir()
            original = "Hello DiamondDust\n\nThis is the source essay.\n"
            essay_path.write_text(original, encoding="utf-8")

            ingested = read_markdown_essay(essay_path, root=root)

            self.assertEqual(essay_path.read_text(encoding="utf-8"), original)
            self.assertEqual(ingested.source_path, "00-inbox/my-essay.md")
            self.assertEqual(ingested.raw_content, original)
            self.assertEqual(ingested.body, original)
            self.assertEqual(dict(ingested.frontmatter), {})
            self.assertTrue(ingested.source_id.startswith("raw_essay_my_essay_"))
            self.assertEqual(ingested.source_ref.origin, SourceOrigin.USER_TEXT)
            self.assertEqual(ingested.source_ref.source_span, "lines 1-3")
            self.assertEqual(
                ingested.source_ref.content_hash,
                compute_content_hash(original),
            )

    def test_parses_frontmatter_and_body_line_span(self) -> None:
        raw = (
            "---\n"
            "id: raw_custom_source\n"
            "title: \"Frontmatter Test\"\n"
            "topics:\n"
            "  - AI\n"
            "  - knowledge systems\n"
            "draft: false\n"
            "---\n"
            "# Body\n"
            "Source paragraph.\n"
        )

        ingested = ingest_markdown_text(raw, source_path="00-inbox/test.md")

        self.assertEqual(ingested.source_id, "raw_custom_source")
        self.assertEqual(ingested.frontmatter["title"], "Frontmatter Test")
        self.assertEqual(ingested.frontmatter["topics"], ("AI", "knowledge systems"))
        self.assertEqual(ingested.frontmatter["draft"], False)
        self.assertEqual(ingested.body, "# Body\nSource paragraph.\n")
        self.assertEqual(ingested.body_line_start, 9)
        self.assertEqual(ingested.body_line_end, 10)
        self.assertEqual(ingested.source_ref.source_span, "lines 9-10")
        self.assertEqual(
            ingested.source_ref.content_hash,
            compute_content_hash("# Body\nSource paragraph.\n"),
        )

    def test_hashes_are_stable_and_content_sensitive(self) -> None:
        self.assertEqual(compute_content_hash("same"), compute_content_hash("same"))
        self.assertNotEqual(compute_content_hash("same"), compute_content_hash("different"))
        self.assertTrue(compute_content_hash("same").startswith("sha256:"))

    def test_rejects_non_markdown_file_paths(self) -> None:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "essay.txt"
            path.write_text("not markdown", encoding="utf-8")

            with self.assertRaises(MarkdownIngestionError):
                read_markdown_essay(path)

    def test_rejects_path_outside_declared_root(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            root = temp_path / "vault"
            outside = temp_path / "outside.md"
            root.mkdir()
            outside.write_text("outside", encoding="utf-8")

            with self.assertRaises(MarkdownIngestionError):
                read_markdown_essay(outside, root=root)

    def test_rejects_unclosed_frontmatter(self) -> None:
        with self.assertRaises(MarkdownIngestionError):
            ingest_markdown_text(
                "---\ntitle: Missing close\n",
                source_path="00-inbox/bad.md",
            )

    def test_rejects_nested_or_orphan_frontmatter_lines(self) -> None:
        with self.assertRaises(MarkdownIngestionError):
            ingest_markdown_text(
                "---\n  - orphan\n---\nBody\n",
                source_path="00-inbox/bad.md",
            )


if __name__ == "__main__":
    unittest.main()
