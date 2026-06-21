import asyncio
import base64
import logging
import tempfile
from pathlib import Path

import fitz
import httpx
from markitdown import MarkItDown

from app.core.settings import get_settings
from app.domain.models import ProcessingStrategy
from app.parsers.base import ParsedDocument, StoredFile

logger = logging.getLogger(__name__)


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
        if self._is_pdf(file):
            return await self._parse_with_ocr_model(file, strategy=ProcessingStrategy.scanner_ocr)

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
            markdown = await self._ocr_pdf_pages(file)
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

    async def _ocr_pdf_pages(self, file: StoredFile) -> str:
        with fitz.open(stream=file.content, filetype="pdf") as document:
            page_count = document.page_count
            pages: list[str | None] = [None] * page_count
            pending: set[asyncio.Task[tuple[int, str]]] = set()
            concurrency = max(1, self.settings.pdf_ocr_concurrency)

            for page_index in range(page_count):
                image_bytes, mime_type = self._render_pdf_page_to_image(document, page_index)
                logger.info(
                    "Rendered PDF page %s/%s for OCR as %s (%s bytes)",
                    page_index + 1,
                    page_count,
                    mime_type,
                    len(image_bytes),
                )
                pending.add(
                    asyncio.create_task(
                        self._ocr_pdf_page(
                            page_index,
                            page_count,
                            image_bytes,
                            mime_type,
                            f"{file.filename} page {page_index + 1}",
                        )
                    )
                )

                if len(pending) >= concurrency:
                    await self._collect_finished_pdf_pages(pending, pages)

            while pending:
                await self._collect_finished_pdf_pages(pending, pages)

        return "\n\n".join(page for page in pages if page is not None)

    async def _collect_finished_pdf_pages(
        self,
        pending: set[asyncio.Task[tuple[int, str]]],
        pages: list[str | None],
    ) -> None:
        done, pending_tasks = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
        pending.clear()
        pending.update(pending_tasks)

        for task in done:
            page_index, page_text = await task
            pages[page_index] = page_text

    async def _ocr_pdf_page(
        self,
        page_index: int,
        page_count: int,
        image_bytes: bytes,
        mime_type: str,
        title: str,
    ) -> tuple[int, str]:
        logger.info("Starting OCR for PDF page %s/%s", page_index + 1, page_count)
        page_markdown = await self._ocr_image_bytes(image_bytes, mime_type, title)
        page_text = page_markdown.strip()
        if not page_text:
            page_text = "_No text could be recognized on this page._"

        logger.info("Finished OCR for PDF page %s/%s", page_index + 1, page_count)
        return page_index, f"## Page {page_index + 1}\n\n{page_text}"

    def _render_pdf_page_to_image(self, document: fitz.Document, page_index: int) -> tuple[bytes, str]:
        page = document.load_page(page_index)
        scale = self.settings.pdf_ocr_render_scale
        pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        return pixmap.tobytes("jpeg", jpg_quality=self.settings.pdf_ocr_jpeg_quality), "image/jpeg"

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

        async with httpx.AsyncClient(timeout=600) as client:
            response = await client.post(
                f"{self.settings.llama_ocr_base_url}/chat/completions",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"].strip()
        if not content:
            return "_No text could be recognized in this image._"

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

