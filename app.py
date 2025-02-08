from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, fields, marshal_with, abort


app = Flask(__name__)

# SQL Server Configuration (Update with your database details)
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc://sa:123@localhost/python_db?driver=ODBC+Driver+17+for+SQL+Server"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)


# User Model
class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"User(name={self.name}, email={self.email})"

# Define resource fields for API response
userFields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String,
}

class Users(Resource):
    @marshal_with(userFields)
    def get(self):
        users = UserModel.query.all()
        return users

    @marshal_with(userFields)
    def post(self):
        name = request.form.get("name")
        email = request.form.get("email")

        if not name or not email:
            abort(400, message="Name and Email are required!")

        user = UserModel(name=name, email=email)
        db.session.add(user)
        db.session.commit()
        return user, 201

# Add API resource
api.add_resource(Users, '/api/users/')

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)