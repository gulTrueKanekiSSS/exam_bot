
from marshmallow import Schema, fields
from config import db, app


class Birthday(db.Model):
    __tablename__ = 'birthdays'
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String)
    owner_id = db.Column(db.Integer)
    friend_name = db.Column(db.String)
    photo = db.Column(db.String)
    friend_congratulations = db.Column(db.Text)


class BirthdaySchema(Schema):
    id = fields.Int()
    owner = fields.Str()
    owner_id = fields.Int()
    friend_name = fields.Str()
    photo = fields.Str()
    friend_congratulations = fields.Str()



app.app_context().push()
db.create_all()
