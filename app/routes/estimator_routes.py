from flask import Blueprint, jsonify, request
from app.daos.estimator_dao import EstimatorDAO
from app.models.estimator import Estimator
from app.database.connection import DatabaseConnection
from datetime import datetime
import pyodbc

bp = Blueprint('estimators', __name__, url_prefix='/api/estimators')

@bp.route('/', methods=['GET'])
def get_all_estimators():
    try:
        # Initialize DAO with database connection
        dao = EstimatorDAO(DatabaseConnection.get_connection())
        
        # Get all estimators
        estimators = dao.get_all_estimators()
        
        # Convert to JSON-serializable format
        estimators_data = []
        for estimator in estimators:
            estimator_dict = {
                "estimatorName": estimator.estimatorName,
                "startDate": estimator.startDate.isoformat() if estimator.startDate else None,
                "endDate": estimator.endDate.isoformat() if estimator.endDate else None,
                "estimatorStatus": estimator.estimatorStatus,
                "coID": estimator.coID,
                "deID": estimator.deID
            }
            estimators_data.append(estimator_dict)
        
        return jsonify(estimators_data), 200
        
    except pyodbc.Error as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": "Database operation failed"}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@bp.route('/', methods=['POST'])
def create_estimator():
    try:
        data = request.get_json()  # Use get_json() for better error handling
        
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Parse dates (handle None values)
        start_date = None
        end_date = None
        
        if 'startDate' in data and data['startDate']:
            try:
                start_date = datetime.strptime(data['startDate'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Invalid startDate format. Use YYYY-MM-DD"}), 400
                
        if 'endDate' in data and data['endDate']:
            try:
                end_date = datetime.strptime(data['endDate'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Invalid endDate format. Use YYYY-MM-DD"}), 400

        # Create Estimator object
        estimator = Estimator(
            estimatorName=data.get('estimatorName'),
            startDate=start_date,
            endDate=end_date,
            estimatorStatus=data.get('estimatorStatus'),
            coID=data.get('coID'),
            deID=data.get('deID')
        )

        # Validate
        estimator.validate()

        # Insert to database
        dao = EstimatorDAO(DatabaseConnection.get_connection())
        estimator_id = dao.insert_estimator(estimator)
        
        return jsonify({
            "message": "Estimator created successfully",
            "estimatorID": estimator_id
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except pyodbc.Error as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": "Database operation failed"}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500
    


# In app/routes/estimator_routes.py
@bp.route('/<int:estimator_id>', methods=['PUT'])
def update_estimator(estimator_id):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Parse dates (handle None/empty values)
        start_date = None
        end_date = None
        
        if 'startDate' in data and data['startDate']:
            try:
                start_date = datetime.strptime(data['startDate'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Invalid startDate format. Use YYYY-MM-DD"}), 400
                
        if 'endDate' in data and data['endDate']:
            try:
                end_date = datetime.strptime(data['endDate'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Invalid endDate format. Use YYYY-MM-DD"}), 400

        # Create Estimator object with updated data
        updated_estimator = Estimator(
            estimatorName=data.get('estimatorName'),
            startDate=start_date,
            endDate=end_date,
            estimatorStatus=data.get('estimatorStatus'),
            coID=data.get('coID'),
            deID=data.get('deID')
        )

        # Validate
        updated_estimator.validate()

        # Update in database
        dao = EstimatorDAO(DatabaseConnection.get_connection())
        success = dao.update_estimator(estimator_id, updated_estimator)
        
        if not success:
            return jsonify({"error": "Estimator not found"}), 404
            
        return jsonify({"message": "Estimator updated successfully"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except pyodbc.Error as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": "Database operation failed"}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500