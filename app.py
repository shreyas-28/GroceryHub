from datetime import datetime
import sys
from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_login import UserMixin, LoginManager, current_user, login_user, login_required, logout_user
from flask_admin.contrib.sqla import ModelView
import Forms.regLoginForm as loginForms
import Forms.addProduct as addProductForm
from wtforms.validators import ValidationError
from Models.mainModel import db
from Models.userModel import UserModel
from Models.productModel import ProductModel,Cart
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
    print("Login Manager")
    return UserModel.query.get(int(user_id))


@app.route("/", methods=['POST', 'GET'])
def mainView():
    print("main view")
    login_form = loginForms.LoginForm()
    register_form = loginForms.RegisterForm()

    def validate_username(self, username):
        if app.UserModel.query.filter_by(username=username.data).first():
            raise ValidationError(
                "This username already exists. Please choose something unique")

    register_form.validate_username = validate_username

    if request.method == 'POST':
        if (request.form.get('loginAction') == 'Login'):
            return render_template("mainView.html", form=login_form)
        else:
            return render_template("mainView.html", form=register_form)
    return render_template("mainView.html", form=login_form,)


@app.route("/login.html", methods=['GET', 'POST'])
def login():
    print('login')
    loginForm = loginForms.LoginForm()
    if (loginForm.validate_on_submit()):
        user = UserModel.query.filter_by(
            username=loginForm.username.data).first()
        if user:
            print("User Identified")
            if (bcrypt.check_password_hash(user.password, loginForm.password.data)):
                print(user)
                login_user(user)
            print("Cart checking")
    cart = Cart.query.filter_by(userId = user.uuid).first()
    print('cart',cart)
    if not cart:
        print('Creating a new cart')
        new_cart = Cart(userId=user.uuid,totalValue = 0,products={})
        db.session.add(new_cart)
        db.session.commit()
    return redirect(url_for('dashboard'))
        # else:
        #     return redirect(url_for("mainView"))


@app.route("/register.html", methods=['GET', 'POST'])
def register():
    print('register')
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


@app.route("/addProduct.html", methods=['GET', 'POST'])
def addProduct():
    productForm = addProductForm.ProductForm()
    print(productForm.manufacturingDate.data)
    if productForm.validate_on_submit():
        new_product = ProductModel(productName=productForm.productName.data, 
                                    productImage='/static/'+productForm.productImage.data,
                                    manufacturingDate=productForm.manufacturingDate.data,
                                    expiryDate=productForm.expiryDate.data, 
                                    quantityInStore=productForm.quantityInStore.data, 
                                    section=productForm.section.data, 
                                    valuePerUnit=productForm.valuePerUnit.data)
        print(new_product)
        db.session.add(new_product)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/addToCart/<productId>', methods=['POST'])
@login_required
def addToCart(productId):
    print('addToCart')
    productToAdd = ProductModel.query.filter_by(productId = productId).first()
    cart = Cart.query.filter_by(userId =current_user.uuid).first()
    productKey = str(productToAdd.productId)
    if productKey not in cart.products:
        print("new cart item")
        cart.products[productKey] = 0
    cart.products[productKey]+=1
    cart.totalValue += productToAdd.valuePerUnit
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/dashboard', methods=['POST', 'GET'])
@login_required
def dashboard():
    print('dashboard')
    productDataArray = ProductModel.query.all()
    print(productDataArray)
    productForm = addProductForm.ProductForm()
    return render_template('dashboard.html', UserModel=current_user, productFormProp=productForm,productDataArray=productDataArray)


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    print('logout')
    logout_user()
    return redirect(url_for('mainView'))

# @app.route('/cart', methods=['POST', 'GET'])
# @login_required
# def cart():
#     myCart = Cart.query.all()
#     for i in myCart.keys()
#     return render_template('cart.html',cartData = myCart)

if __name__ == "__main__":
    app.run(debug=True)
