from flask import Flask, jsonify, request, abort, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, validate
from flask_marshmallow import Marshmallow
from flask_restful import Resource, Api
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
import bcrypt

app = Flask(__name__)


#CONFIG
app.config["SECRET_KEY"] = "svtest"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://indrawan99:Ai12171234@www.db4free.net:3306/sv_userdb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app);
ma = Marshmallow(app)
api = Api(app)



# MODEL
class User(db.Model):
  __tablename__ = "users"
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=True)
  username = db.Column(db.String(100), unique=True)
  password = db.Column(db.String(100), nullable=True)
  
  def __repr__(self):
    return '<User %s>' % self.username

# SCHEMA
class UserSchema(ma.Schema):
  class Meta:
    model = User
    fields = ("id", "name", "username", "password")
  
  name = fields.Str(required=True,validate=[validate.Length(min=3)])
  username = fields.Str(required=True,validate=[validate.Length(min=3)])
  password = fields.Str(required=True, validate=[validate.Length(min=7)])
    
user_schema = UserSchema()
users_schema = UserSchema(many=True)


# RESOURCE
class HelloWorld(Resource):
  def get(self, limit, offset):
    return jsonify({
      "status": 1,
      "message": "Welcome everyone",
      "data": {
        "author": "Indrawan Lisanto",
        "github": "https://github.com/itokun99"
      }
    })


class UserPagination(Resource):
  def get(self, limit, offset):
    users = User.query.paginate(offset, limit, error_out=False);
    
    meta = {
      "has_next": users.has_next,
      "has_prev": users.has_prev,
      "next_page": users.next_num,
      "prev_page": users.prev_num,
      "page": users.page,
      "pages": users.pages,
      "total": users.total
    }
    
    response = jsonify({
      "status": 1,
      "message": "successfully",
      "meta": meta,
      "data": users_schema.dump(users.items)
    })
    
    return response;
    
class UserList(Resource):
  def get(self):
    users = User.query.all()
    response = jsonify({
      "status": 1,
      "message": "successfully",
      "data": users_schema.dump(users)
    })
    return response
  
  def post(self):
    
    # get json request
    data = request.get_json(force=True);
    
    # validate the json input
    errors = user_schema.validate(data);
    
    # throw error if any error
    if errors:
      return abort(make_response({
        "status": 0,
        "message": "failed",
        "errors": errors  
      }, 400))
      
    # make variable readable
    name = data['name']
    username = data['username']
    password = data['password']
    
    # find existing username
    existUser = User.query.filter_by(username=username).first()
    
    
    if existUser is not None:
      return abort(make_response({
        "status": 0,
        "message": "user with username {thename} is exist, please insert other username".format(thename=username)
      }, 400))
    
    # encrypt password
    encryptedPassword = bcrypt.hashpw(password.encode("utf=8"), bcrypt.gensalt())
    
    new_user = User(
      name = name,
      username = username,
      password = encryptedPassword
    )
    
    # save to db
    db.session.add(new_user)
    db.session.commit()
    
    response = jsonify({
      "status": 1,
      "message": "user created!",
      "data": user_schema.dump(new_user)
    })
    return response
  
class UserResource(Resource):
  def get(self, user_id):
    user = User.query.get(user_id)
    
    if user is None:
      return abort(make_response({
        "status": 0,
        "message": "User not found!"
      }, 404))    
      
    response = jsonify({
      "status": 1,
      "message": "successfully",
      "data": user_schema.dump(user)
    })
    return response
  
  def put(self, user_id):
    
    data = request.get_json(force=True);
    
    # validate the json input
    errors = user_schema.validate(data);
    
    # throw error if any error
    if errors:
      return abort(make_response({
        "status": 0,
        "message": "failed",
        "errors": errors  
      }, 400))
      
    # make variable readable
    name = data['name']
    username = data['username']
    password = data['password']
    
    user = User.query.get(user_id)
    
    if user is None:
      return abort(make_response({
        "status": 0,
        "message": "User not found!"
      }, 404))
    
    existUsername = User.query.filter_by(username=username).first();
    
    if existUsername is not None:
      if existUsername.username == username and username != user.username:
        return abort(make_response({
          "status": 0,
          "message": "User with username {thename} is exist".format(thename=username),
        }, 400))
      
      
    # encrypt password
    encryptedPassword = bcrypt.hashpw(password.encode("utf=8"), bcrypt.gensalt())
    
    user.name = name;
    user.username = username;
    user.password = encryptedPassword;
    db.session.commit()
    
    response = jsonify({
      "status": 1,
      "message": "User data has updated!",
      "data": user_schema.dump(user)
    })

    return response
  
  def delete(self, user_id):
    user = User.query.get(user_id);
    
    if user is None:
      return abort(make_response({
        "status": 0,
        "message": "User not found!"
      }, 404))
    
    db.session.delete(user)
    db.session.commit()
    
    response = jsonify({
      "status": 1,
      "message": "User data has been deleted!"
    })

    return response
    
  

# run db create table
db.create_all()

# ROUTE
api.add_resource(HelloWorld, "/")
api.add_resource(UserList, "/api/user")
api.add_resource(UserResource, "/api/user/<user_id>")
api.add_resource(UserPagination, "/api/user/<int:limit>/<int:offset>")
  
  
if __name__ == "__main__":
  app.run(debug=True, port=5000)