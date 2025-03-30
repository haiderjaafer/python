# app/daos/pdf_dao.py
import os
from typing import List, Optional
from app.daos.base_dao import BaseDAO
from app.models.pdf_table import PdfTable
import pyodbc

class PdfDAO(BaseDAO):
    def __init__(self, connection):
        super().__init__(connection)

    def get_next_count(self, order_id: int) -> int:
        """Get next countPdf number for an order"""
        query = "SELECT MAX(countPdf) FROM dbo.pdfTable WHERE orderID = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (order_id,))
        max_count = cursor.fetchone()[0]
        return (max_count or 0) + 1

    def insert_pdf(self, pdf: PdfTable, file_content: bytes, base_path: str) -> int:
        """Save PDF file and insert record"""
        # Get next count number
        pdf.countPdf = self.get_next_count(pdf.orderID)
        
        # Construct filename and full path
        filename = f"{pdf.orderNo}.{pdf.orderYear}.{pdf.countPdf}.pdf"
        pdf.pdf = os.path.join(base_path, filename)
        
        # Ensure base directory exists
        os.makedirs(base_path, exist_ok=True)
        
        # Save file
        with open(pdf.pdf, 'wb') as f:
            f.write(file_content)
        
        # Insert database record
        query = """
        INSERT INTO dbo.pdfTable (
            orderID, orderNo, orderYear, countPdf, pdf
        ) 
        OUTPUT INSERTED.pdfID
        VALUES (?, ?, ?, ?, ?)
        """
        
        params = (
            pdf.orderID,
            pdf.orderNo,
            pdf.orderYear,
            pdf.countPdf,
            pdf.pdf
        )

        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            self.connection.commit()
            
            if not result:
                raise ValueError("Failed to retrieve pdfID")
            return result[0]
            
        except pyodbc.Error as e:
            self.connection.rollback()
            # Clean up file if DB operation failed
            if os.path.exists(pdf.pdf):
                os.remove(pdf.pdf)
            raise ValueError(f"Database error: {str(e)}")
        finally:
            if cursor:
                cursor.close()