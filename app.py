import sys
from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_login import UserMixin, LoginManager, current_user, login_user, login_required, logout_user
from flask_admin.contrib.sqla import ModelView
import Forms.regLoginForm as loginForms
from wtforms.validators import  ValidationError
from Models.mainModel import db
from Models.userModel import UserModel
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SECRET_KEY'] = 'randomSecretKey'
db.init_app(app)


bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.get(int(user_id))

@app.route("/",methods=['POST','GET'])
def mainView():
    login_form=loginForms.LoginForm()
    register_form =loginForms.RegisterForm()

    def validate_username(self, username):
        if app.UserModel.query.filter_by(username=username.data).first():
            raise ValidationError(
                "This username already exists. Please choose something unique")
        
    register_form.validate_username = validate_username
    
    if request.method == 'POST':
        if(request.form.get('loginAction')=='Login'):
            return render_template("mainView.html",form=login_form)
        else:
            return render_template("mainView.html",form=register_form)
    return render_template("mainView.html",form=login_form,)


@app.route("/login.html", methods=['GET', 'POST'])
def login():
    loginForm = loginForms.LoginForm()
    if (loginForm.validate_on_submit()):
        user = UserModel.query.filter_by(username=loginForm.username.data).first()
        if user:
            if (bcrypt.check_password_hash(user.password, loginForm.password.data)):
                print(user)
                login_user(user)
                return redirect(url_for('dashboard'))
        else:
            return redirect(url_for("mainView"))

@app.route("/register.html", methods=['GET', 'POST'])
def register():
    registerForm = loginForms.RegisterForm()
    if registerForm.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            registerForm.password.data)
        new_user = UserModel(username=registerForm.username.data,
                        password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('dashboard'))
    
    
@app.route('/dashboard', methods=['POST', 'GET'])
@login_required
def dashboard():
    return render_template('dashboard.html', UserModel=current_user)

@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('mainView'))


@app.route("/shopingSpace")
def shopingSpace():
    return redirect(url_for('shopingSpace.html'))



if __name__ == "__main__":
    app.run(debug=True)
