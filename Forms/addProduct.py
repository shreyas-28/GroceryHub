
from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField,FloatField
from wtforms.validators import InputRequired, Length, ValidationError,DataRequired
from wtforms.fields import DateField

class ProductForm(FlaskForm):
    productName = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Name of the product"})
    productImage = StringField(validators=[InputRequired(), Length(
        min=4, max=80)], render_kw={"placeholder": "Image"})
    manufacturingDate = DateField(label='Manufacuring Date',validators=[DataRequired()])
    expiryDate = DateField(label='Manufacuring Date',validators=[DataRequired()])
    quantityInStore = IntegerField('Total quantity',validators=[InputRequired()])
    valuePerUnit = FloatField('Cost/Unit',validators=[InputRequired()])
    section = StringField(validators=[InputRequired(), Length(
        min=4, max=80)], render_kw={"placeholder": "section"})
    submit = SubmitField("Add Product")
    action = "/addProduct.html"


class SectionForm(FlaskForm):
        sectionName = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Name of the section"})
        action ="/addSection.html"
        submit = SubmitField("Add Section")

