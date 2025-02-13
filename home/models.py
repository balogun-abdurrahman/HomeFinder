from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

#from carapp import db

class User(db.Model):
    user_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_firstname = db.Column(db.String(100), nullable=False)
    user_lastname = db.Column(db.String(100), nullable=False)
    user_password = db.Column(db.String(255), nullable=False)
    user_number = db.Column(db.String(100), nullable=False, unique=True)
    user_picture = db.Column(db.String(100), nullable=True)
    user_email = db.Column(db.String(100), nullable=False, unique=True)
    user_type = db.Column(db.String(255), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    last_login = db.Column(db.DateTime(), default=datetime.utcnow)
    user_status = db.Column(db.Enum("Active","Inactive"), nullable=False, server_default=("Active"))

    use = db.relationship("Property_listing", back_populates="user")
    

    def __repr__(self):
        return f"{self.user_id}:{self.user_firstname}"
    
class Admin(db.Model):
    admin_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    admin_name = db.Column(db.String(100), nullable=False)
    admin_password = db.Column(db.String(255), nullable=False)
    admin_email = db.Column(db.String(100), nullable=False)
    admin_login = db.Column(db.DateTime(), default=datetime.utcnow)



class Property_listing(db.Model):
    property_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    property_price = db.Column(db.Float, nullable=False)
    property_type_id = db.Column(db.Integer, db.ForeignKey("property_type.property_id"), nullable=True)
    property_amenities = db.Column(db.Text, nullable=True)
    property_status = db.Column(db.Enum("Available","Unavailable"), nullable=False, server_default=("Available"))
    property_cover_picture = db.Column(db.String(100), nullable=False)
    property_category = db.Column(db.String(100), nullable=False,)
    property_state_id = db.Column(db.Integer, db.ForeignKey("state.state_id"), nullable=True)

    bedroom_number = db.Column(db.Integer, nullable=True)
    bathroom_number = db.Column(db.Integer, nullable=True)
    parking_space = db.Column(db.Integer, nullable=True)
    
    property_state_id = db.Column(db.Integer, db.ForeignKey("state.state_id"), nullable=True)
    property_state_id = db.Column(db.Integer, db.ForeignKey("state.state_id"), nullable=True)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)

    prop = db.relationship("State", back_populates="stat")
    type = db.relationship("Property_type", back_populates="typ")
    user = db.relationship("User", back_populates="use")
    messa = db.relationship("Message_table", back_populates="mes")
    pim = db.relationship("Property_image", back_populates="pima")


class Property_type(db.Model):
    property_id = db.Column(db.Integer,primary_key=True)
    property_name = db.Column(db.String(255), nullable=False)

    typ = db.relationship("Property_listing", back_populates="type")




class Message_table(db.Model):
    message_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=True)
    reciever_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=True)
    property_id = db.Column(db.Integer, db.ForeignKey("property_listing.property_id"), nullable=True)
    message_content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    status = db.Column(db.Enum("o","1"), nullable=True)

    mes = db.relationship("Property_listing", back_populates="messa")


class State(db.Model):
    state_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    state_name = db.Column(db.String(100), nullable=False)

    stat = db.relationship("Property_listing", back_populates="prop")


class Property_image(db.Model):
    image_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    property_id = db.Column(db.Integer, db.ForeignKey("property_listing.property_id"), nullable=True)
    property_picture = db.Column(db.String(100), nullable=False)

    pima = db.relationship("Property_listing", back_populates="pim")
    





