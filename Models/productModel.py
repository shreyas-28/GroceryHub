from .mainModel import db
from .utilModel import MutableDict, JSONEncodedDict
import sqlalchemy


class SectionModel(db.Model):
    sectionId = db.Column(db.Integer, primary_key=True)
    sectionKey = db.Column(db.String[120], nullable=False)
    sectionValue = db.Column(db.String[120], nullable=False)
    engagement = db.Column(db.Integer)


class ProductModel(db.Model):
    productId = db.Column(db.Integer, primary_key=True)
    productImage = db.Column(db.String[100])
    productName = db.Column(db.String[20], nullable=False, unique=True)
    manufacturingDate = db.Column(sqlalchemy.types.DateTime(), nullable=False)
    expiryDate = db.Column(sqlalchemy.types.DateTime())
    quantityInStore = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String[120], nullable=False)
    valuePerUnit = db.Column(db.Float, nullable=False)
    quantityInCart = db.Column(db.Integer)
    addedOnDate = db.Column(sqlalchemy.types.DateTime())
    engagement = db.Column(db.Integer)

    def get_id(self):
        return self.productId


class Cart(db.Model):
    cartId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey(
        'user_model.uuid'), nullable=False)
    totalValue = db.Column(db.Integer, nullable=False)
    products = db.Column(MutableDict.as_mutable(JSONEncodedDict))
