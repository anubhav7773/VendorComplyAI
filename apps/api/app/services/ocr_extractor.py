# apps/api/app/services/ocr_extractor.py

import os
import json
from typing import Optional
from PIL import Image

from app.schemas.invoice_ocr import StructuredInvoiceOutput
from app.services.document_preprocessor import DocumentPreprocessor


class InvoiceOCRExtractor:
    """
    Dual-engine structured invoice extraction service.
    Engine 1: Local CUDA GPU via Outlines guided decoding (Qwen2-VL).
    Engine 2: Cloud Fallback via Google AI Studio Gemini 2.0 Flash (Pydantic schema enforcement).
    """

    def __init__(self):
        self.use_local_gpu = os.getenv("USE_LOCAL_VLM", "false").lower() == "true"
        self.outlines_generator = None
        self.gemini_client = None

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
        """Initializes Google AI Studio free tier client."""
        try:
            from google import genai
            api_key = os.getenv("GEMINI_API_KEY", "")
            self.gemini_client = genai.Client(api_key=api_key) if api_key else None
            if not api_key:
                print("[WARN] GEMINI_API_KEY is not set. Cloud extraction will require API key.")
        except ImportError:
            self.gemini_client = None

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
        if not self.gemini_client:
            raise RuntimeError("GEMINI_API_KEY is missing and local GPU engine is disabled.")

        from google.genai import types

        prompt = (
            "You are an expert Indian Corporate Tax and GST Auditor. Extract all invoice "
            "metadata conforming strictly to the requested JSON schema. If payment credit terms "
            "are not explicitly printed on the document, set detected_credit_terms_days to 15. "
            "Extract 10-character PAN and 15-character GSTIN accurately."
        )

        response = self.gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[image, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=StructuredInvoiceOutput,
                temperature=0.0
            )
        )

        return StructuredInvoiceOutput.model_validate_json(response.text)
