# apps/api/app/services/document_preprocessor.py

import io
from typing import List
from PIL import Image, ImageEnhance, ImageOps
import fitz  # PyMuPDF


class DocumentPreprocessor:
    """
    Normalizes unstructured invoice attachments (WhatsApp photos, scanned PDFs, images)
    for high-accuracy vision model tokenization.
    """

    MAX_DIMENSION = 1280  # Optimized resolution budget for Vision Transformers

    @classmethod
    def process_raw_bytes(cls, file_bytes: bytes, filename: str) -> List[Image.Image]:
        """
        Converts raw document bytes into a list of preprocessed, contrast-enhanced PIL Images.
        """
        images = []
        lower_name = filename.lower()

        if lower_name.endswith(".pdf"):
            # Multi-page PDF rasterization via PyMuPDF
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page_idx in range(len(doc)):
                page = doc.load_page(page_idx)
                # Render page at 2.0x zoom (~144 DPI) for clear numerical OCR
                pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
                img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
                images.append(cls._enhance_image(img))
            doc.close()
        else:
            # WhatsApp captures, JPG, PNG, WEBP
            img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
            # Auto-orient based on EXIF camera metadata
            img = ImageOps.exif_transpose(img)
            images.append(cls._enhance_image(img))

        return images

    @classmethod
    def _enhance_image(cls, img: Image.Image) -> Image.Image:
        """
        Rescales image to optimal token budget, enhances contrast and text edge sharpness.
        """
        width, height = img.size
        if max(width, height) > cls.MAX_DIMENSION:
            scale = cls.MAX_DIMENSION / float(max(width, height))
            new_size = (int(width * scale), int(height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        # Contrast enhancement for washed-out receipt prints
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.20)

        # Edge sharpness enhancement for numeric digits
        sharpness = ImageEnhance.Sharpness(img)
        img = sharpness.enhance(1.15)

        return img
