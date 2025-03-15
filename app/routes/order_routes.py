from flask import Blueprint, jsonify, request
from app.daos.order_table_dao import OrderTableDAO
from app.models.order_table import OrderTable
from app.database.connection import DatabaseConnection  # Import the connection
from datetime import datetime
import pyodbc

bp = Blueprint('orders', __name__, url_prefix='/api/orders')

@bp.route('/', methods=['POST'])
def create_order():
    data = request.json
    try:
        # Convert date strings to date objects
        order_date = datetime.strptime(data.get('orderDate'), '%Y-%m-%d').date() if data.get('orderDate') else None
        achieved_order_date = datetime.strptime(data.get('achievedOrderDate'), '%Y-%m-%d').date() if data.get('achievedOrderDate') else None

        # Create OrderTable instance
        order = OrderTable(
            orderNo=data.get('orderNo'),
            orderYear=data.get('orderYear'),
            orderDate=order_date,
            orderType=data.get('orderType'),
            coID=data.get('coID'),
            deID=data.get('deID'),
            materialName=data.get('materialName'),
            estimatorID=data.get('estimatorID'),
            procedureID=data.get('procedureID'),
            orderStatus=data.get('orderStatus'),
            notes=data.get('notes'),
            achievedOrderDate=achieved_order_date,
            priceRequestedDestination=data.get('priceRequestedDestination'),
            finalPrice=data.get('finalPrice'),
            currencyType=data.get('currencyType'),
            checkOrderLink=data.get('checkOrderLink'),
            userID=data.get('userID')
        )

        # Validate the order
        order.validate()

        # Initialize the DAO with the database connection
        dao = OrderTableDAO(DatabaseConnection.get_connection())  # Create an instance

        # Insert into the database and get the orderID
        orderID = dao.insert_order(order)

        return jsonify({"message": "Order created successfully", "orderID": orderID}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except pyodbc.Error as e:
        print(f"Database error details: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@bp.route('/countAllOrderNo', methods=['GET'])
def count_all_order_no():
    try:
        # Initialize the DAO with the database connection
        dao = OrderTableDAO(DatabaseConnection.get_connection())  # Create an instance

        # Get the count of all orderNo
        count = dao.count_all_order_no()
        return jsonify({"countAllOrderNo": count}), 200
    except pyodbc.Error as e:
        print(f"Database error details: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500