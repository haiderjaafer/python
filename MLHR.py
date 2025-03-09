import pandas as pd

from sklearn.neighbors import NearestNeighbors
import numpy as np
from flask import Flask, jsonify, request

app = Flask(__name__)

# Create a sample dataset
data = {
    "Employee_ID": [1, 2, 3, 4, 5],
    "Name": ["Alice", "Bob", "Charlie", "David", "Eve"],
    "Age": [25, 30, 35, 40, 45],
    "Department": ["HR", "IT", "Finance", "IT", "HR"],
    "Salary": [50000, 60000, 70000, 80000, 90000]
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Save to CSV (optional)
df.to_csv("employee_data.csv", index=False)

print(df)


# Features (Employee_ID) and target (all other columns)
X = df[["Employee_ID"]]
y = df[["Name", "Age", "Department", "Salary"]]

# Train a k-NN model
knn = NearestNeighbors(n_neighbors=1)
knn.fit(X)

# Function to get employee details by ID
def get_employee_details(employee_id):
    distances, indices = knn.kneighbors(np.array([[employee_id]]))
    return y.iloc[indices[0][0]]

# Test the function
print(get_employee_details(2))  # Should return details of Bob



@app.route('/employee', methods=['GET'])
def employee():
    employee_id = request.args.get('id', type=int)
    if employee_id is None:
        return jsonify({"error": "Please provide an employee ID"}), 400
    
    try:
        details = get_employee_details(employee_id)
        return jsonify(details.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == '__main__':
    app.run(debug=True)