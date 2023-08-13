from Models.userModel import UserModel
from Models.productModel import Cart, ProductModel, SectionModel


def cart_init(db, current_user):
    print('fixing_db')
    fix_db(db)
    cart = Cart.query.filter_by(userId=current_user.uuid).first()
    print('cart', cart)
    print("Initialising app.")
    print("Clearing products data.")
    productData = ProductModel.query.all()
    for product in productData:
        product.quantityInCart = 0
        db.session.commit()
    print("Clearing cart data.")
    if not cart:
        print('Creating a new cart')
        new_cart = Cart(userId=current_user.uuid, totalValue=0, products={})
        db.session.add(new_cart)
        db.session.commit()
    else:
        print("Loading older cart.")
        cartData = cart.products
        if (cartData):
            for product in cartData:
                print("adding from older cart.", product)
                dbProduct = ProductModel.query.filter_by(
                    productId=int(product)).first()
                dbProduct.quantityInCart = cartData[product]
        else:
            cart.products = {}
        db.session.commit()


def updateCart(db, existingCart):
    oldValue = 0 + existingCart.totalValue
    newValue = 0
    for product in existingCart.products.keys():
        productItem = ProductModel.query.filter_by(
            productId=int(product)).first()
        productValue = productItem.valuePerUnit
        if productItem.quantityInStore == 0:
            existingCart.products[product] = 0
            productToUpdate = ProductModel.query.filter_by(
                productId=int(product))
            editEngagement(productToUpdate, -2)
        newValue += productValue*existingCart.products[product]

    if oldValue != newValue:
        existingCart.totalValue = newValue
        db.session.commit()
        return True
    else:
        return False


def fix_db(db):
    # ProductModel.query.filter_by(productName='TestProduct').delete()
    # users = UserModel.query.all()
    # for user in users:
    #     user.firstOrder = True
    # db.session.commit()
    return None

# Value : how much we need to increase or decrease engagement


def editEngagement(db, product, value):
    if not product.engagement:
        product.engagement = 0

    product.engagement += value
    section = SectionModel.query.filter_by(sectionKey=product.section).first()
    if not section.engagement:
        section.engagement = 0
    if value > 0:
        section.engagement += 1
    else:
        section.engagement -= 1
    db.session.commit()
    return None
