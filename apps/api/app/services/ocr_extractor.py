# apps/api/app/services/ocr_extractor.py

import os
import io
import json
import base64
from typing import Optional
from PIL import Image

from app.schemas.invoice_ocr import StructuredInvoiceOutput
from app.services.document_preprocessor import DocumentPreprocessor


class InvoiceOCRExtractor:
    """
    Dual-engine structured invoice extraction service.
    Engine 1: Local CUDA GPU via Outlines guided decoding (Qwen2-VL).
    Engine 2: Cloud Fallback via Groq LPU Vision API (llama-3.2-11b-vision-preview).
    """

    def __init__(self):
        self.use_local_gpu = os.getenv("USE_LOCAL_VLM", "false").lower() == "true"
        self.outlines_generator = None
        self.groq_client = None

        if self.use_local_gpu:
            self._init_local_outlines_engine()
        else:
            self._init_cloud_fallback_engine()

    def _init_local_outlines_engine(self):
        """Initializes Outlines with quantized Qwen2-VL on local CUDA hardware."""
        try:
            import torch
            import outlines
            from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

            model_id = "Qwen/Qwen2-VL-2B-Instruct"
            print(f"[INFO] Initializing Outlines Local Engine with {model_id} on CUDA...")

            model = Qwen2VLForConditionalGeneration.from_pretrained(
                model_id,
                torch_dtype=torch.float16,
                device_map="cuda:0",
                low_cpu_mem_usage=True
            )
            processor = AutoProcessor.from_pretrained(model_id)

            outlines_model = outlines.models.TransformersVision(model, processor)
            self.outlines_generator = outlines.generate.json(
                outlines_model,
                StructuredInvoiceOutput
            )
            print("[SUCCESS] Local Outlines FSM Generator ready.")
        except Exception as e:
            print(f"[WARN] Failed to load local CUDA engine: {str(e)}. Falling back to Cloud API.")
            self.use_local_gpu = False
            self._init_cloud_fallback_engine()

    def _init_cloud_fallback_engine(self):
        """Initializes Groq LPU Vision client."""
        try:
            from app.core.config import settings
            api_key = getattr(settings, "GROQ_API_KEY", "") or os.getenv("GROQ_API_KEY", "")
            if not api_key:
                print("[WARN] GROQ_API_KEY is not set. Cloud extraction will require API key.")
                self.groq_client = None
                return

            from groq import Groq
            self.groq_client = Groq(api_key=api_key)
        except ImportError:
            self.groq_client = None

    def extract_from_file_bytes(self, file_bytes: bytes, filename: str) -> StructuredInvoiceOutput:
        """
        Normalizes input document bytes and executes guided structured extraction.
        """
        images = DocumentPreprocessor.process_raw_bytes(file_bytes, filename)
        if not images:
            raise ValueError("Document contains no processable pages or images.")

        # Process primary page containing header and tax summary
        primary_image = images[0]

        if self.use_local_gpu and self.outlines_generator:
            return self._extract_local(primary_image)
        else:
            return self._extract_cloud(primary_image)

    def _extract_local(self, image: Image.Image) -> StructuredInvoiceOutput:
        prompt = (
            "Extract all Indian B2B tax invoice fields conforming strictly to schema: "
            "vendor_name, vendor_pan, vendor_gstin, invoice_number, invoice_date, "
            "taxable_amount, cgst_amount, sgst_amount, igst_amount, total_amount, "
            "detected_credit_terms_days, and tds_section_applicable."
        )
        return self.outlines_generator(image, prompt)

    def _extract_cloud(self, image: Image.Image) -> StructuredInvoiceOutput:
        """
        Cloud extraction using Groq LPU Vision API (llama-3.2-11b-vision-preview).
        """
        if not self.groq_client:
            from app.core.config import settings
            api_key = getattr(settings, "GROQ_API_KEY", "") or os.getenv("GROQ_API_KEY", "")
            if not api_key:
                raise RuntimeError("GROQ_API_KEY is missing and local GPU engine is disabled.")
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=api_key)
            except ImportError:
                raise RuntimeError("The 'groq' package is not installed. Please install it with `pip install groq`.")

        # 1. Convert PIL Image to Base64 JPEG data URL
        buffered = io.BytesIO()
        rgb_image = image.convert("RGB") if image.mode != "RGB" else image
        rgb_image.save(buffered, format="JPEG", quality=90)
        base64_encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")
        image_data_url = f"data:image/jpeg;base64,{base64_encoded}"

        # 2. Build JSON Schema and Statutory Extraction Prompt
        schema_json = json.dumps(StructuredInvoiceOutput.model_json_schema(), indent=2)

        system_prompt = (
            "You are an expert Indian Corporate Tax and GST Auditor specializing in MSME Section 43B(h) compliance.\n"
            "Extract all invoice metadata from the provided image and return ONLY a valid JSON object strictly conforming to "
            f"this JSON schema:\n{schema_json}\n\n"
            "MANDATORY STATUTORY RULES:\n"
            "1. Extract 10-character vendor_pan (e.g. AABCM1234K) and 15-character vendor_gstin accurately.\n"
            "2. If payment credit terms are not explicitly stated on the invoice, set detected_credit_terms_days to 15 (Section 15 statutory default).\n"
            "3. Format invoice_date as YYYY-MM-DD.\n"
            "4. Extract taxable_amount, cgst_amount, sgst_amount, igst_amount, and total_amount as numbers or numerical strings.\n"
            "5. Return ONLY the raw JSON object. Do not wrap in markdown or include extra text."
        )

        user_content = [
            {
                "type": "text",
                "text": "Extract all structured B2B tax invoice fields conforming to the statutory schema."
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": image_data_url
                }
            }
        ]

        # 3. Call Groq Vision API
        completion = self.groq_client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )

        content = completion.choices[0].message.content
        if not content:
            raise ValueError("Groq Vision API returned empty response content.")

        return StructuredInvoiceOutput.model_validate_json(content.strip())
