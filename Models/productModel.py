from .mainModel import db

class product(db.Model):
    productId = db.Column(db.Integer, primary_key=True)
    productName = db.Column(db.String[20], nullable=False, unique=True)
    manufacturingDate = db.Column(db.String[80], nullable=False)
    expiryDate = db.Column(db.String[80], nullable=False)
    quantityInStore = db.Column(db.String[80], nullable=False)
    section = db.Column(db.String[80], nullable=False)

    def get_id(self):
        return self.uuid