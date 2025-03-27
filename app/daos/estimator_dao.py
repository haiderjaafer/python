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
        query = "SELECT  estimatorName,startDate,endDate,estimatorStatus,coID,deID  FROM estimatorsTable"
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            print(f"type of rows...{type(rows)}")
            return [Estimator( estimatorName=row.estimatorName, startDate=row.startDate, endDate=row.endDate, estimatorStatus=row.estimatorStatus,coID =row.coID,deID=row.deID) for row in rows]
        except pyodbc.Error as e:
            print(f"Database error in get_all_estimators: {e}")
            raise
        finally:
            if cursor:
                cursor.close()


    def insert_estimator(self, estimator: Estimator) -> int:
        """
        Insert a new estimator into the database.
        Returns the ID of the newly created estimator.
        """
        query = """
        INSERT INTO estimatorsTable (
            estimatorName, 
            startDate, 
            endDate, 
            estimatorStatus, 
            coID, 
            deID
        ) 
        OUTPUT INSERTED.estimatorID
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        params = (
            estimator.estimatorName,
            estimator.startDate,
            estimator.endDate,
            estimator.estimatorStatus,
            estimator.coID,
            estimator.deID
        )

        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            if not result:
                raise ValueError("Failed to retrieve estimatorID after insert")
            
            estimator_id = result[0]
            self.connection.commit()
            return estimator_id
            
        except pyodbc.Error as e:
            self.connection.rollback()
            print(f"Database error in insert_estimator: {str(e)}")
            raise ValueError(f"Database error: {str(e)}")
        finally:
            if cursor:
                cursor.close()
    


    # In app/daos/estimator_dao.py
    def update_estimator(self, estimator_id: int, updated_estimator: Estimator) -> bool:
        """
        Update an existing estimator in the database.
        Returns True if update was successful.
        """
        query = """
        UPDATE [dbo].[estimatorsTable] 
        SET 
            estimatorName = ?,
            startDate = ?,
            endDate = ?,
            estimatorStatus = ?,
            coID = ?,
            deID = ?
        WHERE 
            estimatorID = ?
        """
        
        # Convert empty string to None for endDate
        end_date = updated_estimator.endDate if updated_estimator.endDate else None
        
        params = (
            updated_estimator.estimatorName,
            updated_estimator.startDate,
            end_date,
            updated_estimator.estimatorStatus,
            updated_estimator.coID,
            updated_estimator.deID,
            estimator_id
        )

        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            
            # Check if any row was affected
            if cursor.rowcount == 0:
                return False
                
            self.connection.commit()
            return True
            
        except pyodbc.Error as e:
            self.connection.rollback()
            print(f"Database error in update_estimator: {str(e)}")
            raise ValueError(f"Database error: {str(e)}")
        finally:
            if cursor:
                cursor.close()