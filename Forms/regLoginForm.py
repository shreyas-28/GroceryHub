from flask import current_app as app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,SelectField
from wtforms.validators import InputRequired, Length


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=80)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")
    action = "/register.html"

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=80)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Login")
    action = "/login.html"

class TicketForm(FlaskForm):
    ticketRequest = SelectField(u'Requesting resource', choices=[('Access', 'Access'), ('Edit', 'Edit')])
    ticketTarget = SelectField(u'Reason', choices=[('AdminAccess', 'AdminAccess'), ('ManagerAccess', 'ManagerAccess'), ('Section', 'Section')])
    ticketDetails = StringField(validators=[InputRequired(), Length(
        min=4, max=220)], render_kw={"placeholder": "Optional: Details"})
    submit = SubmitField("Raise")