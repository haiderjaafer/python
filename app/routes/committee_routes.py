from flask import Blueprint, jsonify
from app.daos.committee_dao import CommitteeDAO
from app.database.connection import DatabaseConnection  # Import the connection
import pyodbc

bp = Blueprint('committees', __name__, url_prefix='/api/committees')

@bp.route('/', methods=['GET'])
def get_all_committees():
    try:
        # Initialize the DAO with the database connection
        dao = CommitteeDAO(DatabaseConnection.get_connection())  # Create an instance

        # Get all committees from the database
        committees = dao.get_all_committees()  # Call the method on the instance

        # Convert Committee objects to dictionaries for JSON response
        committees_data = [{"coID": committee.coID, "Com": committee.Com} for committee in committees]
        return jsonify(committees_data), 200
    except pyodbc.Error as e:
        print(f"Database error details: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500
    

    

@bp.route('/', methods=['POST'])
def create_committee():
    # Your existing create_committee logic here
    pass