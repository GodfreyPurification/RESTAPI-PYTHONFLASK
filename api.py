from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
from sqlalchemy.exc import IntegrityError

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
db= SQLAlchemy(app)
api=Api(app)
class UserModel(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	name=db.Column(db.String(80), unique=True, nullable=False)
	email=db.Column(db.String(80), unique=True, nullable=False)
	
	def __repr__(self):
		return f"User (name={self.name}, email={self.email})"
user_args=reqparse.RequestParser()
user_args.add_argument('name', type=str, required=True,help="Name cannot be blank")
user_args.add_argument('email', type=str, required=True,help="Email cannot be blank")

userFields = {
    'id':fields.Integer,
	'name':fields.String,
	'email':fields.String,
}

class UserList(Resource):
    @marshal_with(userFields)
    def get(self):
        users = UserModel.query.all()
        return users

    @marshal_with(userFields)
    def post(self):
        args = user_args.parse_args()
        
        # Check if user with the same name or email already exists
        existing_user = UserModel.query.filter(
            (UserModel.name == args["name"]) | (UserModel.email == args["email"])
        ).first()
        
        if existing_user:
            abort(409, message="User with this name or email already exists.")
        
        try:
            user = UserModel(name=args["name"], email=args["email"])  # type: ignore
            db.session.add(user)
            db.session.commit()
            return user, 201
        except IntegrityError:
            db.session.rollback()
            abort(500, message="Internal server error while saving user.")

class User(Resource):
    @marshal_with(userFields)
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message='User not found')
        return user
    

    @marshal_with(userFields)
    def patch(self, id):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message='User not found')
            return  # Add a return to satisfy the type checker
        if args['name'] is not None:
            user.name = args['name']
        if args['email'] is not None:
            user.email = args['email']
        db.session.commit()
        return user
# _____________________________________________________
    @marshal_with(userFields)
    def delete(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message='User not found')
            return  # Add a return to satisfy the type checker
        db.session.delete(user)
        db.session.commit()
        users = UserModel.query.all()
        return users, 204

api.add_resource(UserList, '/api/users/')
api.add_resource(User, '/api/users/<int:id>')
@app.route('/')
def home():
    return '<h1>Flask REST API</h1>'

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
    


# https://www.youtube.com/watch?v=z3YMz-Gocmw 30:00