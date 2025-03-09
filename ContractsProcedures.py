import pyodbc
from flask import Flask, jsonify, request
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date

# Flask API Setup
app = Flask(__name__)

# 1. Database Connection Singleton Class
class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            try:
                cls._instance.connection = pyodbc.connect(
                    'DRIVER={ODBC Driver 17 for SQL Server};'
                    'SERVER=localhost;'
                    'DATABASE=ContractsProcedures;'
                    'UID=sa;'
                    'PWD=123'
                )
            except pyodbc.Error as e:
                print(f"Database connection error: {e}")
                raise
        return cls._instance

    def get_connection(self):
        return self._instance.connection

@dataclass
class OrderTable:
    orderNo: Optional[str] = None
    orderYear: Optional[str] = None
    orderDate: Optional[date] = None
    orderType: Optional[str] = None
    coID: Optional[int] = None
    deID: Optional[int] = None
    materialName: Optional[str] = None
    estimatorID: Optional[int] = None
    procedureID: Optional[int] = None
    orderStatus: Optional[str] = None
    notes: Optional[str] = None
    achievedOrderDate: Optional[date] = None
    priceRequestedDestination: Optional[str] = None
    finalPrice: Optional[str] = None
    currencyType: Optional[str] = None
    cunnrentDate: Optional[date] = None
    color: Optional[str] = None
    checkOrderLink: Optional[bool] = None
    userID: Optional[int] = None    

    def validate(self):
        """
        Validate the order data.
        """
        if not self.orderNo:
            raise ValueError("Order number is required")
        if not self.orderYear:
            raise ValueError("Order year is required")
        if not self.orderDate:
            raise ValueError("Order date is required")
        if not isinstance(self.orderDate, date):
            raise ValueError("Order date must be a valid date")

# Base DAO Class
class BaseDAO:
    def __init__(self, connection):
        self.connection = connection

    def execute_query(self, query, params=None):
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor
        except pyodbc.Error as e:
            print(f"Database error: {e}")
            self.connection.rollback()
            raise
        finally:
            cursor.close()

# OrderTable DAO Class





class OrderTableDAO(BaseDAO):
    def __init__(self, connection):
        super().__init__(connection)

    def check_order_exists(self, orderNo: str, orderYear: str) -> bool:
        """
        Check if an order with the given orderNo and orderYear already exists in the database.
        """
        query = """
        SELECT COUNT(*) 
        FROM [dbo].[orderTable] 
        WHERE orderNo = ? AND orderYear = ?
        """
        params = (orderNo, orderYear)
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result[0] > 0  # Returns True if the order exists, False otherwise
        except pyodbc.Error as e:
            print(f"Database error in check_order_exists: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def insert_order(self, order):
        """
        Insert a new order into the database and return the orderID using OUTPUT INSERTED.orderID.
        """
        # Check if the order already exists
        if self.check_order_exists(order.orderNo, order.orderYear):
            raise ValueError(f"Order with orderNo '{order.orderNo}' and orderYear '{order.orderYear}' already exists.")

        # Set default values if not provided
        notes = order.notes if order.notes else 'لا توجد ملاحظات'
        checkOrderLink = order.checkOrderLink if order.checkOrderLink is not None else False
        finalPrice = order.finalPrice if order.finalPrice else '0'
        procedureID = order.procedureID if order.procedureID else 1
        color = 'GREEN' if order.orderStatus == 'منجز' else 'RED' if order.orderStatus == 'الغيت' else 'YELLOW'

        # Use OUTPUT INSERTED.orderID to get the new order ID directly
        insert_query = """
        INSERT INTO [dbo].[orderTable] (
            orderNo, orderYear, orderDate, orderType, coID, deID, materialName, estimatorID, procedureID, 
            orderStatus, notes, achievedOrderDate, priceRequestedDestination, finalPrice, currencyType, 
            cunnrentDate, color, checkOrderLink, userID
        ) 
        OUTPUT INSERTED.orderID  -- Fetch the new ID immediately
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), ?, ?, ?);
        """

        params = (
            order.orderNo, order.orderYear, order.orderDate, order.orderType, order.coID, order.deID, 
            order.materialName, order.estimatorID, procedureID, order.orderStatus, notes, 
            order.achievedOrderDate, order.priceRequestedDestination, finalPrice, order.currencyType, 
            color, checkOrderLink, order.userID
        )

        cursor = None
        try:
            cursor = self.connection.cursor()

            # Execute the query and get the inserted orderID
            print("Executing INSERT query with OUTPUT INSERTED.orderID...")
            cursor.execute(insert_query, params)
            result = cursor.fetchone()

            if not result or result[0] is None:
                raise ValueError("Failed to retrieve orderID using OUTPUT INSERTED.orderID.")

            orderID = int(result[0])
            print(f"✅ Order inserted successfully with orderID: {orderID}")

            # Commit the transaction
            self.connection.commit()

            return orderID

        except pyodbc.Error as e:
            print(f"❌ Database error in insert_order: {e}")
            self.connection.rollback()
            raise ValueError(f"Database error: {e}")

        except Exception as e:
            print(f"❌ Unexpected error in insert_order: {e}")
            self.connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()



# Initialize the database connection
db_connection = DatabaseConnection().get_connection()
order_table_dao = OrderTableDAO(db_connection)

# Flask Endpoint
@app.route('/order', methods=['POST'])
def create_order():
    data = request.json
    print(data)
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

        # Insert into the database and get the orderID
        orderID = order_table_dao.insert_order(order)

        return jsonify({"message": "Order created successfully", "orderID": orderID}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except pyodbc.Error as e:
        print(f"Database error details: {e}")
        return jsonify({"error": "Database error occurred"}), 500

if __name__ == '__main__':
    app.run(debug=True)