import pyodbc
from flask import Flask, jsonify, request
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date
from typing import List  # Import List from typing module


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





@dataclass
class Committee:
    coID: str  # coID is nvarchar(50)
    Com: str   # Com is nvarchar(255)

    def validate(self):
        """
        Validate committee data.
        """
        if not self.coID:
            raise ValueError("coID is required")
        if not self.Com:
            raise ValueError("Committee name (Com) is required")
        if len(self.coID) > 50:
            raise ValueError("coID must be 50 characters or less")
        if len(self.Com) > 255:
            raise ValueError("Committee name (Com) must be 255 characters or less")




@dataclass
class Department:
    deID: int       # deID is int
    Dep: str        # Dep is nvarchar(250)
    coID: int       # coID is int

    def validate(self):
        """
        Validate department data.
        """
        if not self.deID or self.deID <= 0:
            raise ValueError("deID must be a positive integer")
        if not self.Dep:
            raise ValueError("Department name (Dep) is required")
        if len(self.Dep) > 250:
            raise ValueError("Department name (Dep) must be 250 characters or less")
        if not self.coID or self.coID <= 0:
            raise ValueError("coID must be a positive integer")


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
    

    def count_all_order_no(self) -> int:
        """
        Count all orderNo in the orderTable.
        """
        query = "SELECT COUNT([orderNo]) FROM [dbo].[orderTable]"
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            return result[0]  # Return the count
        except pyodbc.Error as e:
            print(f"Database error in count_all_order_no: {e}")
            raise
        finally:
            if cursor:
                cursor.close()


# Estimators DAO Class
class EstimatorsDAO(BaseDAO):
    def __init__(self, connection):
        super().__init__(connection)

    def get_all_estimators(self) -> List[dict]:
        """
        Retrieve all estimators (estimatorID and estimatorName) from the estimatorsTable.
        """
        query = "SELECT estimatorID, estimatorName FROM estimatorsTable"
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

            # Convert rows to a list of dictionaries
            estimators = [{"estimatorID": row.estimatorID, "estimatorName": row.estimatorName} for row in rows]
            return estimators
        except pyodbc.Error as e:
            print(f"Database error in get_all_estimators: {e}")
            raise
        finally:
            if cursor:
                cursor.close()





class CommitteeDAO(BaseDAO):
    def __init__(self, connection):
        super().__init__(connection)

    def get_all_committees(self) -> List[Committee]:
        """
        Retrieve all committees from the ComTB table, ordered by coID ascending.
        Returns a list of Committee objects.
        """
        query = "SELECT coID, Com FROM ComTB ORDER BY coID ASC"
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

            # Convert rows to a list of Committee objects
            committees = [Committee(coID=row.coID, Com=row.Com) for row in rows]
            return committees
        except pyodbc.Error as e:
            print(f"Database error in get_all_committees: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def insert_committee(self, committee: Committee):
        """
        Insert a new committee into the ComTB table.
        """
        # Validate the committee data
        committee.validate()

        query = "INSERT INTO ComTB (coID, Com) VALUES (?, ?)"
        params = (committee.coID, committee.Com)
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            print(f"✅ Committee inserted successfully: {committee}")
        except pyodbc.Error as e:
            print(f"❌ Database error in insert_committee: {e}")
            self.connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()



from typing import List

class DepartmentDAO(BaseDAO):
    def __init__(self, connection):
        super().__init__(connection)

    def get_departments_by_coID(self, coID: int) -> List[Department]:
        """
        Retrieve all departments for a specific coID from the DepTB table.
        """
        query = "SELECT deID, Dep, coID FROM DepTB WHERE coID = ?"
        params = (coID,)
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            # Convert rows to a list of Department objects
            departments = [Department(deID=row.deID, Dep=row.Dep, coID=row.coID) for row in rows]
            return departments
        except pyodbc.Error as e:
            print(f"Database error in get_departments_by_coID: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def insert_department(self, department: Department):
        """
        Insert a new department into the DepTB table.
        """
        # Validate the department data
        department.validate()

        query = "INSERT INTO DepTB (deID, Dep, coID) VALUES (?, ?, ?)"
        params = (department.deID, department.Dep, department.coID)
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            print(f"✅ Department inserted successfully: {department}")
        except pyodbc.Error as e:
            print(f"❌ Database error in insert_department: {e}")
            self.connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()





# Initialize the database connection
db_connection = DatabaseConnection().get_connection()
order_table_dao = OrderTableDAO(db_connection)

# Initialize the DAO
estimators_dao = EstimatorsDAO(db_connection)


# Initialize the DAO
committee_dao = CommitteeDAO(db_connection)


# Initialize the DAO
department_dao = DepartmentDAO(db_connection)


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


# Flask Endpoint for Counting All OrderNo
@app.route('/countAllOrderNo', methods=['GET'])
def count_all_order_no():
    try:
        # Get the count of all orderNo
        count = order_table_dao.count_all_order_no()
        return jsonify({"countAllOrderNo": count}), 200
    except pyodbc.Error as e:
        print(f"Database error details: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


# Flask Endpoint for Retrieving All Estimators
@app.route('/estimators', methods=['GET'])
def get_all_estimators():
    try:
        # Get all estimators from the database
        estimators = estimators_dao.get_all_estimators()
        return jsonify(estimators), 200
    except pyodbc.Error as e:
        print(f"Database error details: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500



# Flask Endpoint for Retrieving All Committees
@app.route('/committees', methods=['GET'])
def get_all_committees():
    try:
        # Get all committees from the database
        committees = committee_dao.get_all_committees()

        # Convert Committee objects to dictionaries for JSON response
        committees_data = [{"coID": committee.coID, "Com": committee.Com} for committee in committees]
        return jsonify(committees_data), 200
    except pyodbc.Error as e:
        print(f"Database error details: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

# Flask Endpoint for Inserting a New Committee
@app.route('/committees', methods=['POST'])
def create_committee():
    data = request.json
    try:
        # Create a Committee object from the request data
        committee = Committee(
            coID=data.get('coID'),
            Com=data.get('Com')
        )

        # Insert the committee into the database
        committee_dao.insert_committee(committee)

        return jsonify({"message": "Committee created successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except pyodbc.Error as e:
        print(f"Database error details: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500



# Flask Endpoint for Retrieving Departments by coID
@app.route('/departments/<int:coID>', methods=['GET'])
def get_departments_by_coID(coID: int):
    try:
        # Get departments for the specified coID
        departments = department_dao.get_departments_by_coID(coID)

        # Convert Department objects to dictionaries for JSON response
        departments_data = [{"deID": department.deID, "Dep": department.Dep, "coID": department.coID} for department in departments]
        return jsonify(departments_data), 200
    except pyodbc.Error as e:
        print(f"Database error details: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

# Flask Endpoint for Inserting a New Department
@app.route('/departments', methods=['POST'])
def create_department():
    data = request.json
    try:
        # Create a Department object from the request data
        department = Department(
            deID=data.get('deID'),
            Dep=data.get('Dep'),
            coID=data.get('coID')
        )

        # Insert the department into the database
        department_dao.insert_department(department)

        return jsonify({"message": "Department created successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except pyodbc.Error as e:
        print(f"Database error details: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500




if __name__ == '__main__':
    app.run(debug=True)

# run 
#py ContractsProcedures.py 