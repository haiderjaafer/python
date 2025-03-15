import pyodbc

class DatabaseConnection:
    _instance = None

    @classmethod
    def initialize(cls, connection_string):
        if cls._instance is None:
            cls._instance = pyodbc.connect(connection_string)

    @classmethod
    def get_connection(cls):
        if cls._instance is None:
            raise RuntimeError("Database not initialized!")
        return cls._instance