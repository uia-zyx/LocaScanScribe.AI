import asyncio
import base64
import tempfile
from pathlib import Path

import fitz
import httpx
from markitdown import MarkItDown

from app.core.settings import get_settings
from app.domain.models import ProcessingStrategy
from app.parsers.base import ParsedDocument, StoredFile


class ParserRegistry:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.markitdown = MarkItDown()

    async def parse(self, file: StoredFile, strategy: ProcessingStrategy) -> ParsedDocument:
        if strategy == ProcessingStrategy.ocr_model:
            return await self._parse_with_ocr_model(file)

        if strategy == ProcessingStrategy.scanner_ocr:
            return await self._parse_with_best_available_scanner(file)

        return await self._parse_with_markitdown(file, ProcessingStrategy.parser)

    async def _parse_with_best_available_scanner(self, file: StoredFile) -> ParsedDocument:
        parsed = await self._parse_with_markitdown(file, ProcessingStrategy.scanner_ocr)
        if self._has_meaningful_content(parsed.markdown):
            return parsed

        return await self._parse_with_ocr_model(file, strategy=ProcessingStrategy.scanner_ocr)

    async def _parse_with_markitdown(
        self,
        file: StoredFile,
        strategy: ProcessingStrategy,
    ) -> ParsedDocument:
        if file.mime_type in {"text/markdown", "text/plain"}:
            markdown = self._decode_text(file.content)
        else:
            markdown = await asyncio.to_thread(self._convert_with_markitdown, file)

        return ParsedDocument(
            title=file.filename,
            markdown=self._normalize_markdown(file.filename, markdown),
            strategy=strategy,
        )

    async def _parse_with_ocr_model(
        self,
        file: StoredFile,
        strategy: ProcessingStrategy = ProcessingStrategy.ocr_model,
    ) -> ParsedDocument:
        if self._is_pdf(file):
            markdown = await asyncio.to_thread(self._ocr_pdf_pages, file)
        elif self._is_image(file):
            markdown = await self._ocr_image_bytes(file.content, file.mime_type, file.filename)
        else:
            parsed = await self._parse_with_markitdown(file, strategy)
            return parsed

        return ParsedDocument(
            title=file.filename,
            markdown=self._normalize_markdown(file.filename, markdown),
            strategy=strategy,
        )

    def _convert_with_markitdown(self, file: StoredFile) -> str:
        suffix = Path(file.filename).suffix or self._extension_from_mime(file.mime_type)
        with tempfile.NamedTemporaryFile(suffix=suffix) as temp_file:
            temp_file.write(file.content)
            temp_file.flush()
            result = self.markitdown.convert(temp_file.name)
            return result.text_content

    def _ocr_pdf_pages(self, file: StoredFile) -> str:
        document = fitz.open(stream=file.content, filetype="pdf")
        pages: list[str] = []

        for page_index in range(document.page_count):
            page = document.load_page(page_index)
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image_bytes = pixmap.tobytes("png")
            page_markdown = asyncio.run(
                self._ocr_image_bytes(image_bytes, "image/png", f"{file.filename} page {page_index + 1}")
            )
            pages.append(f"## Page {page_index + 1}\n\n{page_markdown.strip()}")

        return "\n\n".join(pages)

    async def _ocr_image_bytes(self, content: bytes, mime_type: str, title: str) -> str:
        image_base64 = base64.b64encode(content).decode("ascii")
        payload = {
            "model": self.settings.llama_ocr_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Text Recognition:",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}",
                            },
                        },
                    ],
                }
            ],
            "temperature": 0,
            "max_tokens": 4096,
        }

        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(
                f"{self.settings.llama_ocr_base_url}/chat/completions",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        return f"# {title}\n\n{content}" if not content.lstrip().startswith("#") else content

    def _decode_text(self, content: bytes) -> str:
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("utf-8", errors="replace")

    def _normalize_markdown(self, filename: str, markdown: str) -> str:
        cleaned = markdown.strip()
        if not cleaned:
            cleaned = "_No text could be extracted from this document._"

        return cleaned if cleaned.lstrip().startswith("#") else f"# {filename}\n\n{cleaned}"

    def _has_meaningful_content(self, markdown: str) -> bool:
        text = markdown.replace("#", "").strip()
        return len(text) >= 80

    def _is_pdf(self, file: StoredFile) -> bool:
        return file.mime_type == "application/pdf" or file.filename.lower().endswith(".pdf")

    def _is_image(self, file: StoredFile) -> bool:
        return file.mime_type.startswith("image/")

    def _extension_from_mime(self, mime_type: str) -> str:
        extensions = {
            "application/pdf": ".pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
            "text/html": ".html",
            "text/plain": ".txt",
            "text/markdown": ".md",
        }
        return extensions.get(mime_type, "")

