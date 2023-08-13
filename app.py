from datetime import datetime
from flask import Flask, render_template, url_for, redirect, request
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from flask_restful import Api
from sqlalchemy import desc
import Forms.regLoginForm as loginForms
import Forms.Product as addProductForm
from wtforms.validators import ValidationError
from utils import cart_init, editEngagement, updateCart
from Models.mainModel import db
from Models.userModel import UserModel
from Models.productModel import ProductModel, Cart, SectionModel
from Models.ticketModel import TicketModel
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SECRET_KEY'] = 'randomSecretKey'
api = Api(app)
db.init_app(app)
migrate = Migrate(app, db)

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    print("Login Manager working.")
    return UserModel.query.get(int(user_id))


@app.route("/", methods=['POST', 'GET'])
@app.route("/<error>", methods=['POST', 'GET'])
def mainView(error=""):
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
    return render_template("mainView.html", form=login_form, error=error)


@app.route("/login.html", methods=['GET', 'POST'])
def login():
    print('Logging in.')
    loginForm = loginForms.LoginForm()
    if (loginForm.validate_on_submit()):
        user = UserModel.query.filter_by(
            username=loginForm.username.data).first()
        if user:
            isAdmin = len(request.form.getlist('isAdmin'))
            isManager = len(request.form.getlist('isManager'))
            if isAdmin or user.isAdmin:
                if isAdmin and not user.isAdmin:
                    return redirect(url_for('mainView', error="Not admin login"))
                if not isAdmin and user.isAdmin:
                    return redirect(url_for('mainView', error="Admin login! Use correct form."))
            elif isManager or user.isManager:
                if isManager and not user.isManager:
                    return redirect(url_for('mainView', error="Not manager login"))
                if not isManager and user.isManager:
                    return redirect(url_for('mainView', error="Manager login! Use correct form."))

            if (bcrypt.check_password_hash(user.password, loginForm.password.data)):
                login_user(user)
            print("Cart checking.")
            cart_init(db, current_user)
        return redirect(url_for('dashboard'))
    error = "Invalid Username or Password"

    return redirect(url_for('mainView', error=error))


@app.route("/register.html", methods=['GET', 'POST'])
def register():
    print('Registering .')
    registerForm = loginForms.RegisterForm()
    if registerForm.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            registerForm.password.data)
        checkUsername = UserModel.query.filter_by(
            username=registerForm.username.data).first()
        if (checkUsername):
            return redirect(url_for('mainView', error="Username already taken"))
        new_user = UserModel(username=registerForm.username.data,
                             password=hashed_password, firstOrder=True)
        print('Creating a new cart.')
        db.session.add(new_user)
        db.session.commit()
        new_cart = Cart(userId=new_user.uuid, totalValue=0, products={})
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
                                   section=request.form['section'].lower(),
                                   valuePerUnit=productForm.valuePerUnit.data,
                                   addedOnDate=datetime.now())
        print("Adding new product ", new_product)
        db.session.add(new_product)
        db.session.commit()
    return redirect(url_for('admin', message="Added " + new_product.productName))


@app.route("/requestManager.html", methods=['GET', 'POST'])
def requestManager():
    newTicket = TicketModel(ticketRequest='Access',
                            ticketTarget='ManagerAccess',
                            ticketDetails="Please provide access to new user "+current_user.username,
                            ticketRaisedBy=current_user.uuid)
    db.session.add(newTicket)
    db.session.commit()
    return redirect(url_for('dashboard', message="Successfully raised a ticket!"))


@app.route("/editProduct.html", methods=['POST'])
def editProduct():
    productToEdit = request.form['productToEdit']
    productInStock = request.form['productInStock']
    productEditForm = addProductForm.EditProductForm()
    product = ProductModel.query.filter_by(productName=productToEdit).first()
    try:
        productChangeStock = request.form['changeStock']
    except:
        productChangeStock = False
    if product:
        if productChangeStock == 'changeStock':
            if productInStock == "Out of stock":
                editEngagement(db, product, -5)
                product.quantityInStore = 0
            elif productInStock == "Change stock":
                editEngagement(db, product, +1)
                print("Updating product." + product.productName)
                product.quantityInStore = productEditForm.unitsInStock.data
                product.addedOnDate = datetime.now()
        if productEditForm.productValue.data:
            editEngagement(db, product, +1)
            product.valuePerUnit = productEditForm.productValue.data
        db.session.commit()
        return redirect(url_for('admin', message="Updated "+product.productName))
    else:
        return redirect(url_for('admin', message="Couldn't find the product"))


@app.route("/raiseTicket.html", methods=['POST'])
def raiseTicket():
    ticketForm = loginForms.TicketForm()
    if ticketForm.validate_on_submit():

        newTicket = TicketModel(ticketRequest=ticketForm.ticketRequest.data,
                                ticketTarget=ticketForm.ticketTarget.data,
                                ticketDetails=ticketForm.ticketDetails.data,
                                ticketRaisedBy=current_user.uuid)
        print("Adding ticket. ", newTicket)
        db.session.add(newTicket)
        db.session.commit()
        return redirect(url_for('admin', message="Successfully raised a ticket!"))


@app.route("/handleTicket.html/<kwargs>", methods=['POST'])
def handleTicket(kwargs):
    kwargs = eval(kwargs)
    ticketId, approved = kwargs['ticketId'], kwargs['approved']
    ticketDetails = TicketModel.query.filter_by(ticketId=ticketId).first()
    if approved:
        ticketDetails.action = 'Approved'
        match ticketDetails.ticketRequest:
            case 'Access':
                userToPromote = UserModel.query.filter_by(
                    uuid=ticketDetails.ticketRaisedBy).first()
                if ticketDetails.ticketTarget == "ManagerAccess":
                    userToPromote.isManager = True
                else:
                    userToPromote.isAdmin = True
        db.session.commit()
    else:
        ticketDetails.action = 'Denied'
        db.session.commit()

    return redirect(url_for('admin', message='Ticket closed!'))


@app.route("/handleBuyNow.html", methods=['POST'])
def handleBuyNow():
    existingCart = Cart.query.filter_by(userId=current_user.uuid).first()
    changed = updateCart(db, existingCart)
    if changed:
        return redirect(url_for('cart', message='Some items in the cart has been updated. Please view the cart.'))
    for product in existingCart.products.keys():
        productToUpdate = ProductModel.query.filter_by(
            productId=int(product)).first()
        if existingCart.products[product] > 10:
            editEngagement(db, productToUpdate, +5)
        else:
            editEngagement(db, productToUpdate, +2)
    Cart.query.filter_by(userId=current_user.uuid).delete()
    newCart = Cart(userId=current_user.uuid, totalValue=0, products={})
    current_user.firstOrder = False
    print("First order for " + str(current_user.firstOrder))
    db.session.add(newCart)
    db.session.commit()
    return redirect(url_for('dashboard', message="Thank you for your purchase !!"))


@app.route('/editSection.html/<kwargs>', methods=['POST', 'GET'])
@login_required
def editSection(kwargs):
    sectionForm = addProductForm.SectionForm()
    kwargs = eval(kwargs)
    action = kwargs['action']
    match action:
        case 'add':
            if sectionForm.validate_on_submit():
                newSection = SectionModel(sectionKey=sectionForm.sectionName.data.lower(),
                                          sectionValue=sectionForm.sectionName.data.lower())
                print('Adding section .', newSection)
                db.session.add(newSection)
                db.session.commit()
                return redirect(url_for('admin', message="Section added!"))
        case 'remove':
            print("Removing Section. ")
            sectionToRemove = request.form['sectionToRemove']
            print('Section to remove ', sectionToRemove)
            if current_user.isAdmin:
                print("Admin removing section.")
                SectionModel.query.filter_by(
                    sectionKey=sectionToRemove.lower()).delete()
                SectionModel.query.filter_by(
                    sectionKey=sectionToRemove).delete()
                # Removing this section from all the products and marking them as "other"
                products = ProductModel.query.filter_by(
                    section=sectionToRemove.lower())
                for product in products:
                    product.section = 'others'
                db.session.commit()
                return redirect(url_for('admin', message=sectionToRemove+" removed seccesfully"))
        case 'edit':
            if sectionForm.validate_on_submit():
                print("Editting a section .")
                sectionToEdit = SectionModel.query.filter_by(
                    sectionKey=request.form['sectionToEdit']).first()
                sectionToEdit.sectionKey, sectionToEdit.sectionValue = sectionForm.editSectionName.data, sectionForm.editSectionName.data
                db.session.commit()
                return redirect(url_for('admin', message="Section editted successfully!"))
    return redirect(url_for('admin', message="Error! Try again later."))


@app.route('/editCart/<kwargs>', methods=['POST'])
@login_required
def editCart(kwargs):
    kwargs = eval(kwargs)

    productId = kwargs['productId']
    productToAdd = ProductModel.query.filter_by(productId=productId).first()
    cart = Cart.query.filter_by(userId=current_user.uuid).first()
    productKey = str(productToAdd.productId)
    if 'action' in kwargs.keys():
        action = kwargs['action']
    else:
        action = "add"
    if productKey not in cart.products:
        cart.products[productKey] = 0

    match action:
        case "remove":
            cart.products[productKey] -= 1
            productToAdd.quantityInCart -= 1
            cart.totalValue -= productToAdd.valuePerUnit
            editEngagement(db, productToAdd, -1)
        case "add":
            cart.products[productKey] += 1
            productToAdd.quantityInCart += 1
            productToAdd.quantityInStore -= 1
            editEngagement(db, productToAdd, +1)
            cart.totalValue += productToAdd.valuePerUnit
        case "clean":
            quantity = cart.products[productKey]
            value = productToAdd.valuePerUnit
            cart.totalValue -= (quantity*value)
            editEngagement(db, productToAdd, -1*quantity)
            productToAdd.quantityInCart = 0
            cart.products[productKey] = 0
    db.session.commit()
    if 'origin' in kwargs.keys():
        if (kwargs['origin'] == 'cart'):
            return redirect(url_for('cart'))
        elif (kwargs['origin'] == 'detailView'):
            return redirect(url_for('productDetailView', productId=kwargs['productId']))
    return redirect(url_for('dashboard'))


@app.route('/cart', methods=['POST', 'GET'])
@app.route('/cart/<message>', methods=['POST', 'GET'])
@login_required
def cart(message=None):
    cart = Cart.query.filter_by(userId=current_user.uuid).first()
    total = cart.totalValue
    discount = 0
    if (cart):
        cartData = cart.products
        cartDataProp = {}
        for product in cartData:
            productData = ProductModel.query.filter_by(
                productId=int(product)).first()
            cartDataProp[productData] = cartData[product]
        cartDataProp = {x: y for x, y in cartDataProp.items() if y != 0}
        if current_user.firstOrder:
            discount = 15*total/100
            discountMessage = 'First order discount'
            return render_template('cart.html', cartDataProp=cartDataProp, totalValue=total, message=message, discount=discount, discountMessage=discountMessage)
        return render_template('cart.html', cartDataProp=cartDataProp, totalValue=total, message=message, discount=discount)
    return redirect(url_for('dashboard'))


@app.route('/productDetailView/<productId>', methods=['POST', 'GET'])
@login_required
def productDetailView(productId):
    productData = ProductModel.query.filter_by(productId=productId).first()
    editEngagement(db, productData, +3)
    return render_template('productDetailView.html', productData=productData)


@app.route('/sections', methods=['GET'])
@app.route('/sections/<sectionCategory>', methods=['GET'])
@login_required
def sections(sectionCategory=None):
    print('Loading sections.')
    sectionsData = [sec.sectionValue.capitalize()
                    for sec in SectionModel.query.all()]

    if (sectionCategory):
        productDataArray = ProductModel.query.filter_by(
            section=sectionCategory.lower())
        return render_template('sections.html', productDataArray=productDataArray, sections=sectionsData, sectionCategory=sectionCategory)

    productDataArray = ProductModel.query.all()
    return render_template('sections.html', productDataArray=productDataArray, sections=sectionsData)


@app.route('/dashboard', methods=['POST', 'GET'])
@app.route('/dashboard/<message>', methods=['POST', 'GET'])
@login_required
def dashboard(message=None):
    cart_init(db, current_user)
    print('Loading dashboard')
    productDataArray = ProductModel.query.all()
    freshProducts = ProductModel.query.order_by(
        desc(ProductModel.addedOnDate))[:6]
    return render_template('dashboard.html', UserModel=current_user, productDataArray=productDataArray, message=message, freshProducts=freshProducts)


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    print('Loging out.')
    logout_user()
    return redirect(url_for('mainView'))


@app.route('/admin', methods=['GET'])
@app.route('/admin/<message>', methods=['GET'])
@login_required
def admin(message=None):
    sections = [sec.sectionValue.capitalize()
                for sec in SectionModel.query.all()]
    raisedTickets = TicketModel.query.all()
    raisedTicketsProps = []
    for ticket in raisedTickets:
        if ticket.action:
            continue
        ticket.raisedBy = UserModel.query.filter_by(
            uuid=ticket.ticketRaisedBy).first().username
        raisedTicketsProps.append(ticket)
    productsList = ProductModel.query.all()
    productEditForm = addProductForm.EditProductForm()
    addProduct = addProductForm.ProductForm()
    sectionForm = addProductForm.SectionForm()
    raiseTicketForm = loginForms.TicketForm()
    return render_template('adminManager.html', addProductForm=addProduct, sections=sections, sectionFormProps=sectionForm, message=message, raiseTicketForm=raiseTicketForm, raisedTickets=raisedTicketsProps, productsList=productsList, productEditForm=productEditForm)


@app.route('/search', methods=['POST', 'GET'])
@app.route('/search/<advancedSearch>', methods=['POST', 'GET'])
@login_required
def search(advancedSearch=False):
    if advancedSearch:
        advancedSearchForm = addProductForm.AdvancedSearch()
        priceFilter = advancedSearchForm.priceFilter.data
        dateFilter = advancedSearchForm.manufacturingDateFilter.data
        if priceFilter:
            searchedProducts = ProductModel.query.filter_by(
                valuePerUnit=priceFilter).all()
            searchedProducts = db.session.query(ProductModel).filter(
                ProductModel.valuePerUnit.between(priceFilter-20, priceFilter+20)).all()
        elif dateFilter:
            my_time = datetime.min.time()
            newDate = datetime.combine(dateFilter, my_time)
            searchedProducts = ProductModel.query.filter_by(
                manufacturingDate=newDate).all()
        newAdvancedSearchForm = addProductForm.AdvancedSearch()
        return render_template('search.html', searchedSections=[], searchedProducts=searchedProducts, advancedSearch=newAdvancedSearchForm)

    searchString = request.form['Search']
    if not len(searchString):
        return redirect(url_for('dashboard'))
    searchedSection = SectionModel.query.filter(
        SectionModel.sectionKey.like(f"{searchString}%")).all()

    searchedProducts = ProductModel.query.filter(
        ProductModel.productName.like(f"{searchString}%")).all()
    advancedSearchForm = addProductForm.AdvancedSearch()
    return render_template('search.html', searchedSections=searchedSection, searchedProducts=searchedProducts, advancedSearch=advancedSearchForm)


if __name__ == "__main__":
    app.run(debug=True)
