from .mainModel import db
from flask_login import UserMixin


class UserModel(db.Model, UserMixin):
    uuid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String[20], nullable=False, unique=True)
    password = db.Column(db.String[80], nullable=False)
    isAdmin = db.Column(db.Boolean)
    isManager = db.Column(db.Integer)
    firstOrder = db.Column(db.Boolean)

    def get_id(self):
        return self.uuid
