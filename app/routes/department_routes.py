from flask import Blueprint, jsonify, request
from app.daos.department_dao import DepartmentDAO
from app.models.department import Department
from app.database.connection import DatabaseConnection  # Import the connection
from datetime import datetime
import pyodbc

bp = Blueprint('departments', __name__, url_prefix='/api/departments')

@bp.route('/<int:coID>', methods=['GET'])
def get_departments_by_coID(coID: int):
    try:
        # Initialize the DAO with the database connection
        dao = DepartmentDAO(DatabaseConnection.get_connection())  # Create an instance

        # Get departments for the specified coID
        departments = dao.get_departments_by_coID(coID)  # Call the method on the instance

        # Convert Department objects to dictionaries for JSON response
        departments_data = [{"deID": department.deID, "Dep": department.Dep, "coID": department.coID} for department in departments]
        return jsonify(departments_data), 200
    except pyodbc.Error as e:
        print(f"Database error details: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@bp.route('/', methods=['POST'])
def create_department():
    data = request.json
    try:
        # Create a Department object from the request data
        department = Department(
            deID=data.get('deID'),
            Dep=data.get('Dep'),
            coID=data.get('coID')
        )

        # Initialize the DAO with the database connection
        dao = DepartmentDAO(DatabaseConnection.get_connection())  # Create an instance

        # Insert the department into the database
        dao.insert_department(department)

        return jsonify({"message": "Department created successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except pyodbc.Error as e:
        print(f"Database error details: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500