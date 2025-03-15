import pyodbc
from typing import Optional

class BaseDAO:
    def __init__(self, connection):
        """
        Initialize the DAO with a database connection.
        """
        self.connection = connection

    def execute_query(self, query: str, params: Optional[tuple] = None):
        """
        Execute a SQL query and return the cursor.
        """
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