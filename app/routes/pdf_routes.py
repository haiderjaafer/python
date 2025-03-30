# app/routes/pdf_routes.py
from flask import Blueprint, jsonify, request, current_app
from app.daos.pdf_dao import PdfDAO
from app.models.pdf_table import PdfTable
from app.database.connection import DatabaseConnection
from werkzeug.utils import secure_filename
import os
import pyodbc

bp = Blueprint('pdfs', __name__, url_prefix='/api/pdfs')

@bp.route('/upload', methods=['POST'])
def upload_pdf():
    try:
        # Verify the request contains files
        if 'pdf' not in request.files:
            return jsonify({"error": "No file part"}), 400
            
        file = request.files['pdf']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        # Get form data
        order_id = request.form.get('orderID')
        order_no = request.form.get('orderNo')
        order_year = request.form.get('orderYear')
        
        # Validate required fields
        if not all([order_id, order_no, order_year]):
            return jsonify({"error": "Missing required fields (orderID, orderNo, orderYear)"}), 400
            
        # Secure the filename and validate extension
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Only PDF files are allowed"}), 400
            
        # Create PDF object
        pdf = PdfTable(
            orderID=int(order_id),
            orderNo=secure_filename(order_no),
            orderYear=secure_filename(order_year)
        )
        
        # Get the base path from app config
        base_path = current_app.config['PDF_BASE_PATH']
        
        # Process file upload
        dao = PdfDAO(DatabaseConnection.get_connection())
        pdf_id = dao.insert_pdf(pdf, file.read(), base_path)
        
        return jsonify({
            "message": "PDF uploaded successfully",
            "pdfID": pdf_id,
            "filePath": pdf.pdf
        }), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except pyodbc.Error as e:
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database operation failed"}), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": str(e)}), 500  # More detailed error