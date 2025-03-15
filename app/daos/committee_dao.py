from typing import List
from app.daos.base_dao import BaseDAO
from app.models.committee import Committee
import pyodbc

class CommitteeDAO(BaseDAO):
    def __init__(self, connection):
        super().__init__(connection)

    def get_all_committees(self) -> List[Committee]:
        """
        Retrieve all committees from the ComTB table.
        """
        query = "SELECT coID, Com FROM ComTB ORDER BY coID ASC"
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [Committee(coID=row.coID, Com=row.Com) for row in rows]
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
        # Your existing insert_committee logic here
        pass