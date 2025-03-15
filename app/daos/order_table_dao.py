from typing import Optional
from app.daos.base_dao import BaseDAO
from app.models.order_table import OrderTable
import pyodbc

class OrderTableDAO(BaseDAO):
    def __init__(self, connection):
        """
        Initialize the DAO with a database connection.
        """
        super().__init__(connection)  # Pass the connection to BaseDAO

    def check_order_exists(self, orderNo: str, orderYear: str) -> bool:
        """
        Check if an order with the given orderNo and orderYear already exists.
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

    def insert_order(self, order: OrderTable) -> int:
        """
        Insert a new order into the database and return the orderID.
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