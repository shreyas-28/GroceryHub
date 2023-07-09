from flask import Flask, render_template, url_for, redirect, request
from flask_login import  LoginManager, current_user, login_user, login_required, logout_user
import Forms.regLoginForm as loginForms
import Forms.addProduct as addProductForm
from wtforms.validators import ValidationError
from Models.mainModel import db
from Models.userModel import UserModel
from Models.productModel import ProductModel,Cart, Sections
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SECRET_KEY'] = 'randomSecretKey'
db.init_app(app)
migrate = Migrate(app, db) 

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    print("Login Manager")
    return UserModel.query.get(int(user_id))

def cart_init():
    cart = Cart.query.filter_by(userId = current_user.uuid).first()
    print('cart',cart)
    print("Initialising app......")
    print("Clearing products data.....")
    productData = ProductModel.query.all()
    for product in productData:
        product.quantityInCart=0  
        db.session.commit()
    print("Clearing cart data........")
    if not cart:
        print('Creating a new cart')
        new_cart = Cart(userId=current_user.uuid,totalValue = 0,products={})
        db.session.add(new_cart)
        db.session.commit()
    else:
        print("Loading older cart ..........")
        cartData = cart.products
        for product in cartData:
            print("adding from older cart...",product)
            dbProduct = ProductModel.query.filter_by(productId = int(product)).first()
            dbProduct.quantityInCart = cartData[product]
        db.session.commit()

@app.route("/", methods=['POST', 'GET'])
@app.route("/<error>", methods=['POST', 'GET'])
def mainView(error=""):
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
    return render_template("mainView.html", form=login_form,error=error)


@app.route("/login.html", methods=['GET', 'POST'])
def login():
    print('Loggin in.........')
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
            cart_init()
        return redirect(url_for('dashboard'))
    error = "Invalid Username or Password"

    return redirect(url_for('mainView',error=error))


@app.route("/register.html", methods=['GET', 'POST'])
def register():
    print('Registering ......')
    registerForm = loginForms.RegisterForm()
    if registerForm.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            registerForm.password.data)
        checkUsername = UserModel.query.filter_by(username =registerForm.username.data).first()
        if(checkUsername):
            return redirect(url_for('mainView',error="Username already taken"))
        new_user = UserModel(username=registerForm.username.data,
                             password=hashed_password)
        
        print('Creating a new cart')
        db.session.add(new_user)
        db.session.commit()
        new_cart = Cart(userId=new_user.uuid,totalValue = 0,products={})
        db.session.add(new_cart)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('dashboard'))


@app.route("/addProduct.html", methods=['GET', 'POST'])
def addProduct():
    productForm = addProductForm.ProductForm()
    if productForm.validate_on_submit():
        new_product = ProductModel(productName=productForm.productName.data, 
                                    productImage='/static/'+productForm.productImage.data,
                                    manufacturingDate=productForm.manufacturingDate.data,
                                    expiryDate=productForm.expiryDate.data, 
                                    quantityInStore=productForm.quantityInStore.data, 
                                    section=Sections[productForm.section.data], 
                                    valuePerUnit=productForm.valuePerUnit.data)
        print("Adding new product",new_product)
        db.session.add(new_product)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/editCart/<kwargs>', methods=['POST'])
@login_required
def editCart(kwargs):
    kwargs = eval(kwargs)
    productId = kwargs['productId']
    productToAdd = ProductModel.query.filter_by(productId = productId).first()
    cart = Cart.query.filter_by(userId =current_user.uuid).first()
    productKey = str(productToAdd.productId)
    if 'action' in kwargs.keys() :
        action = kwargs['action']   
    else:
        action = "add"
    if productKey not in cart.products:
        cart.products[productKey] = 0

    match action:
        case "remove":
            cart.products[productKey]-=1
            productToAdd.quantityInCart -=1
            cart.totalValue -= productToAdd.valuePerUnit
        case "add":
            cart.products[productKey]+=1
            productToAdd.quantityInCart +=1
            cart.totalValue += productToAdd.valuePerUnit
        case "clean":
            quantity = cart.products[productKey]
            value = productToAdd.valuePerUnit
            cart.totalValue -= (quantity*value)
            productToAdd.quantityInCart = 0
            cart.products[productKey] = 0
    db.session.commit()
    if 'origin' in kwargs.keys():
        if(kwargs['origin'] =='cart'):
            return redirect(url_for('cart'))
    return redirect(url_for('dashboard'))

@app.route('/cart', methods=['POST', 'GET'])
@login_required
def cart():

    cart = Cart.query.filter_by(userId = current_user.uuid).first()
    if(cart):
        cartData = cart.products
        cartDataProp = {}
        for product in cartData:
            productData = ProductModel.query.filter_by(productId = int(product)).first()
            cartDataProp[productData] = cartData[product]
        cartDataProp = {x:y for x,y in cartDataProp.items() if y!=0}
        return render_template('cart.html',cartDataProp = cartDataProp,totalValue=cart.totalValue)
    return redirect(url_for('dashboard'))

@app.route('/productDetailView/<productId>', methods=['POST','GET'])
@login_required
def productDetailView(productId):
    productData = ProductModel.query.filter_by(productId=productId).first()
    return render_template('productDetailView.html',productData=productData)

##Temp funtion to fix db anamolies
def fix_db():
    lemon = ProductModel.query.filter_by(productId=9).first()
    lemon.productImage = 'static/lemon.jpg'
    db.session.commit()


@app.route('/sections', methods=['GET'])
@app.route('/sections/<sectionCategory>', methods=['GET'])
@login_required
def sections(sectionCategory=None):
    print('Loading sections.........')
    sectionsData = [sec.name for sec in Sections]
    if(sectionCategory):
        productDataArray = ProductModel.query.filter_by(section = sectionCategory)
        return render_template('sections.html',productDataArray = productDataArray,sections = sectionsData,sectionCategory=sectionCategory)

    productDataArray = ProductModel.query.all()
    return render_template('sections.html',productDataArray = productDataArray, sections = sectionsData)

@app.route('/dashboard', methods=['POST', 'GET'])
@login_required
def dashboard():
    cart_init()
    print('Dashboard')
    productDataArray = ProductModel.query.all()
    productForm = addProductForm.ProductForm()
    return render_template('dashboard.html', UserModel=current_user, productFormProp=productForm,productDataArray=productDataArray)


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    print('Loging out.....')
    logout_user()
    return redirect(url_for('mainView'))



if __name__ == "__main__":
    app.run(debug=True)
