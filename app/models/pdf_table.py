# app/models/pdf_table.py
from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class PdfTable:
    pdfID: Optional[int] = None
    orderID: Optional[int] = None
    orderNo: Optional[str] = None
    orderYear: Optional[str] = None
    countPdf: Optional[int] = None
    pdf: Optional[str] = None  # This will store the full path

    def validate(self):
        """Validate before saving"""
        if not self.orderID:
            raise ValueError("orderID is required")
        if not self.orderNo:
            raise ValueError("orderNo is required")
        if not self.orderYear:
            raise ValueError("orderYear is required")
        if not self.countPdf or self.countPdf < 1:
            raise ValueError("countPdf must be at least 1")

    def construct_path(self, base_path: str) -> str:
        """Generate the PDF path based on your requirements"""
        return os.path.join(
            base_path,
            self.orderNo,
            self.orderYear,
            f"{self.countPdf}.pdf"
        )