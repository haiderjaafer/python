from flask import Blueprint, jsonify
from app.daos.estimator_dao import EstimatorDAO
from app.database.connection import DatabaseConnection  # Import the connection
import pyodbc

bp = Blueprint('estimators', __name__, url_prefix='/api/estimators')

@bp.route('/', methods=['GET'])
def get_all_estimators():
    try:
        # Initialize the DAO with the database connection
        dao = EstimatorDAO(DatabaseConnection.get_connection())  # Create an instance

        # Get all estimators from the database
        estimators = dao.get_all_estimators()  # Call the method on the instance

        # Convert Estimator objects to dictionaries for JSON response
        estimators_data = [{"estimatorID": estimator.estimatorID, "estimatorName": estimator.estimatorName} for estimator in estimators]
        return jsonify(estimators_data), 200
    except pyodbc.Error as e:
        print(f"Database error details: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500