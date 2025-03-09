# from flask import Flask 
# from flask_sqlalchemy import SQLAlchemy
# from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort


# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# db= SQLAlchemy(app)
# api = Api(app)

# class UserModel(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(80), unique=True, nullable=False)

#     def __repr__(self):
#         return f"User(name={self.name},email = {self.email})"
# user_args = reqparse.RequestParser()
# user_args.add_argument('name', type=str, required=True, help="Name cannot be blank")
# user_args.add_argument('email', type=str, required=True, help="Email cannot be blank")

# userFields = {
#     'id':fields.Integer,
#     'name':fields.String,
#     'email':fields.String,
# }

# class Users(Resource):
#     @marshal_with(userFields)
#     def get(self):
#         users = UserModel.query.all()
#         return users
    
#     @marshal_with(userFields)
#     def post(self):
#         args = user_args.parse_args()
#         user = UserModel(name=args["name"], email=args["email"])
#         db.session.add(user) 
#         db.session.commit()
#         users = UserModel.query.all()
#         return users, 201
    
# class User(Resource):
#     @marshal_with(userFields)
#     def get(self, id):
#         user = UserModel.query.filter_by(id=id).first() 
#         if not user: 
#             abort(404, message="User not found")
#         return user
    

     
#     @marshal_with(userFields)
#     def patch(self, id):
#         args = user_args.parse_args()
#         user = UserModel.query.filter_by(id=id).first() 
#         if not user: 
#             abort(404, message="User not found")
#         user.name = args["name"]
#         user.email = args["email"]
#         db.session.commit()
#         return user



#     @marshal_with(userFields)
#     def delete(self, id):
#         user = UserModel.query.filter_by(id=id).first() 
#         if not user: 
#             abort(404, message="User not found")
#         db.session.delete(user)
#         db.session.commit()
#         users = UserModel.query.all()
#         return users 



    
# api.add_resource(Users , '/api/users/') 
# api.add_resource(User, '/api/users/<int:id>')   

# @app.route('/')
# def home():
#     return '<h1>Flask Rest Api</h1>'

# if __name__ == '__main__':
#     app.run(debug=True)

#--------------------------------------------------
# from flask import Flask, jsonify, request,render_template,url_for
# from flask_restful import Resource, Api

# import pyodbc 
# app = Flask(__name__)
# api = Api(app)

# # SQL Server Connection
# def get_db_connection():
#     return  pyodbc.connect(
#     'DRIVER={ODBC Driver 17 for SQL Server};'
#     'SERVER=localhost;'
#     'DATABASE=python_db;'
#     'UID=sa;'
#     'PWD=123;'
#     'TrustServerCertificate=yes'
# )


# # API Resource for Fetching Users
# class Users(Resource):
#     def get(self):
#         conn = get_db_connection()   # function to make connection to db
#         cursor = conn.cursor()

#         cursor.execute("SELECT id, name, email FROM users")
#         users = [
#             {"id": row[0], "name": row[1], "email": row[2]}
#             for row in cursor.fetchall()
#         ]

#         conn.close()
#         return jsonify(users)
    
# @app.route('/')
# def home():
#     return render_template('dashboard.html')

    
# # @app.route("/")
# # def dashboard():
# #     return render_template("dashboard.html")


# @app.route("/add-user")
# def add_user():
#     return render_template("add_user.html")

# @app.route('/view_users')
# def view_users():
#      # Assume get_users_from_db() fetches users from your database
#    # users = get_users_from_db()  # You need to implement this function return render_template('view_users.html', users=users)
#     return render_template('view_users.html')  


# # Class-based API resource for user creation
# class CreateUser(Resource):
#     def post(self):
#         try:
#             # Handle both JSON and form data
#             data = request.get_json() or request.form.to_dict()

#             name = data.get('name')
#             email = data.get('email')

#             if not name or not email:
#                 return {"error": "Name and email are required"}, 400

#             conn = get_db_connection()
#             cursor = conn.cursor()
#             cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
#             conn.commit()
#             cursor.close()
#             conn.close()

#             return {"message": "User added successfully"}, 201

#         except Exception as e:
#             return {"error": str(e)}, 500


# api.add_resource(Users, '/api/users/')
# api.add_resource(CreateUser, '/api/users/add') # POST New User


from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from collections import OrderedDict

# Initialize Flask app
app = Flask(__name__)

# SQL Server Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mssql+pyodbc://sa:123@localhost/HRSystem?"
    "driver=ODBC+Driver+17+for+SQL+Server"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define the Employee Model
class Employee(db.Model):
    __tablename__ = 'Employees'
    ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100))
    Skills = db.Column(db.String(500))

# Initialize embeddings and FAISS index
def initialize_search():
    try:
        # Fetch data from SQL Server
        with app.app_context():
            employees = Employee.query.all()
            data = [
                {"id": emp.ID, "name": emp.Name, "skills": emp.Skills}
                for emp in employees
            ]
            df = pd.DataFrame(data)

        # Generate embeddings
        model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        embeddings = model.encode(df['skills'].tolist(), convert_to_tensor=False)

        # Debug: Print embeddings
        print("Employee Skills Embeddings:")
        print(embeddings)

        # Normalize embeddings
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

        # Build FAISS index
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings.astype('float32'))

        # Debug: Print index size
        print("FAISS Index Size:", index.ntotal)

        return df, model, index
    except Exception as e:
        print("Error initializing search:", e)
        raise

# Initialize search system
try:
    df, model, index = initialize_search()
except Exception as e:
    print("Failed to initialize search system. Check SQL Server connection.")
    exit(1)

# Search function
# def search_employees(query, k=3):
#     query_embedding = model.encode([query], convert_to_tensor=False)
    
#     # Debug: Print query embedding
#     print("Query Embedding:")
#     print(query_embedding)

#     # Normalize query embedding
#     query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)

#     distances, indices = index.search(query_embedding.astype('float32'), k)
    
#     # Debug: Print distances and indices
#     print("Distances:", distances)
#     print("Indices:", indices)

#     return df.iloc[indices[0]].to_dict(orient='records')

#----------------------------

# this will result perfect result 

# def search_employees(query, k=3, max_distance=1.0):
#     query_embedding = model.encode([query], convert_to_tensor=False)
#     query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)

#     distances, indices = index.search(query_embedding.astype('float32'), k)
    
#     # Prepare the results
#     results = []
#     for i in range(len(indices[0])):
#         if distances[0][i] <= max_distance:  # Filter by distance
#             employee = df.iloc[indices[0][i]].to_dict()
#             results.append({
#                 "id": employee["id"],
#                 "name": employee["name"],
#                 "skills": employee["skills"],
#                 "index": int(indices[0][i]),
#                 "distance": float(distances[0][i])
#             })
    
#     return results

def search_employees(query, k=3):
    query_embedding = model.encode([query], convert_to_tensor=False)
    query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)

    distances, indices = index.search(query_embedding.astype('float32'), k)
    
    # Prepare the results
    results = []
    for i in range(len(indices[0])):
        employee = df.iloc[indices[0][i]].to_dict()
        results.append(OrderedDict([
            ("id", employee["id"]),
            ("name", employee["name"]),
            ("skills", employee["skills"]),
            ("index", int(indices[0][i])),
            ("distance", float(distances[0][i]))
        ]))
    
    return results


# Flask route for search
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    results = search_employees(query)
    return jsonify(results)

# Home route
@app.route('/')
def home():
    return "HR Search System: Use /search?q=<query> to search for employees."

# Run the app
if __name__ == '__main__':
    app.run(debug=True)