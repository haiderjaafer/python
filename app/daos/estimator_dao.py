from typing import List
from app.daos.base_dao import BaseDAO
from app.models.estimator import Estimator
import pyodbc

class EstimatorDAO(BaseDAO):
    def __init__(self, connection):
        """
        Initialize the DAO with a database connection.
        """
        super().__init__(connection)  # Pass the connection to BaseDAO

    def get_all_estimators(self) -> List[Estimator]:
        """
        Retrieve all estimators from the estimatorsTable.
        """
        query = "SELECT estimatorID, estimatorName FROM estimatorsTable"
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [Estimator(estimatorID=row.estimatorID, estimatorName=row.estimatorName) for row in rows]
        except pyodbc.Error as e:
            print(f"Database error in get_all_estimators: {e}")
            raise
        finally:
            if cursor:
                cursor.close()