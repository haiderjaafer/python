from typing import List
from app.daos.base_dao import BaseDAO
from app.models.department import Department
import pyodbc

class DepartmentDAO(BaseDAO):
    def __init__(self, connection):
        """
        Initialize the DAO with a database connection.
        """
        super().__init__(connection)  # Pass the connection to BaseDAO

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
            return [Department(deID=row.deID, Dep=row.Dep, coID=row.coID) for row in rows]
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