import pyodbc
from flask import Flask, jsonify, request
from dataclasses import dataclass
from typing import Optional, Dict, Any
import re





# 1. Database Connection Singleton Class
class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};'
                'SERVER=localhost;'
                'DATABASE=HRSystem;'
                'UID=sa;'
                'PWD=123'
            )
        return cls._instance

    def get_connection(self):
        return self._instance.connection

# 2. Base Data Access Object (DAO) Class
class BaseDAO:
    def __init__(self, table_name, model_class):
        self.table_name = table_name
        self.model_class = model_class
        self.conn = DatabaseConnection().get_connection()

    def create(self, item):
        cursor = self.conn.cursor()
    
    # Exclude 'id' from the columns and values
        data = {k: v for k, v in item.__dict__.items() if k != 'id'}
    
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
    
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, list(data.values()))
    
        self.conn.commit()
        return cursor.rowcount

    def read(self, item_id):
        cursor = self.conn.cursor()
        query = f"SELECT * FROM {self.table_name} WHERE id = ?"
        cursor.execute(query, item_id)
        row = cursor.fetchone()
        return self.model_class(*row) if row else None

    def update(self, item_id, update_data: Dict[str, Any]):
        cursor = self.conn.cursor()
        set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?"
        cursor.execute(query, (*update_data.values(), item_id))
        self.conn.commit()
        return cursor.rowcount

    def delete(self, item_id):
        cursor = self.conn.cursor()
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        cursor.execute(query, item_id)
        self.conn.commit()
        return cursor.rowcount

# 3. HR Model Class with Validation
@dataclass
class Employee:
    id: Optional[int] = None
    first_name: str = None
    last_name: str = None
    email: str = None
    department: str = None
    salary: float = None

    def validate(self):
        errors = []
        if not self.first_name or len(self.first_name) > 50:
            errors.append("Invalid first name")
        if not self.last_name or len(self.last_name) > 50:
            errors.append("Invalid last name")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            errors.append("Invalid email format")
        if self.salary < 0:
            errors.append("Salary cannot be negative")
        if errors:
            raise ValueError("\n".join(errors))

# 4. Employee DAO
class EmployeeDAO(BaseDAO):
    def __init__(self):
        super().__init__('employees', Employee)

# 5. Flask API Setup
app = Flask(__name__)
employee_dao = EmployeeDAO()

@app.route('/employees', methods=['POST'])
def create_employee():
    try:
        data = request.json
        employee = Employee(**data)
        employee.validate()
        result = employee_dao.create(employee)
        return jsonify({"message": "Employee created", "rows_affected": result}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@app.route('/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    employee = employee_dao.read(employee_id)
    if employee:
        return jsonify(employee.__dict__)
    return jsonify({"message": "Employee not found"}), 404

@app.route('/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    try:
        data = request.json
        employee = Employee(**data)
        employee.validate()
        update_data = {k: v for k, v in employee.__dict__.items() if k != 'id'}
        result = employee_dao.update(employee_id, update_data)
        return jsonify({"message": "Employee updated", "rows_affected": result})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    result = employee_dao.delete(employee_id)
    if result > 0:
        return jsonify({"message": "Employee deleted"})
    return jsonify({"message": "Employee not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)