
from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, FloatField
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired
from wtforms.fields import DateField


class ProductForm(FlaskForm):
    productName = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Name of the product"})
    productImage = StringField(validators=[InputRequired(), Length(
        min=4, max=80)], render_kw={"placeholder": "Image"})
    manufacturingDate = DateField(
        label='Manufacuring Date', validators=[DataRequired()])
    expiryDate = DateField(label='Manufacuring Date',
                           validators=[DataRequired()])
    quantityInStore = IntegerField(
        'Total quantity', validators=[InputRequired()])
    valuePerUnit = FloatField('Cost/Unit', validators=[InputRequired()])
    section = StringField(validators=[InputRequired(), Length(
        min=4, max=80)], render_kw={"placeholder": "section"})
    submit = SubmitField("Add Product")
    action = "/addProduct.html"


class EditProductForm(FlaskForm):
    productName = StringField(render_kw={"placeholder": "Name of the product"})
    productValue = StringField(render_kw={"placeholder": "Edit value"})
    productInStock = StringField(render_kw={"placeholder": "Edit in stock"})
    unitsInStock = IntegerField(
        'Total quantity')
    submitEdit = SubmitField("Edit Product")


class SectionForm(FlaskForm):
    sectionName = StringField(render_kw={"placeholder": "Name of the section"})
    submit = SubmitField("Add Section")
    editSectionName = StringField(
        render_kw={"placeholder": "Edit section name"})
    submitEdit = SubmitField("Edit Section")
