from flask_app import app
from flask import render_template, redirect, request, session
from flask_app.models import user_model, order_model, product_model

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'user_id' not in session:
        return redirect("/logout")
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    str_product_id = str(product_id)
    if str_product_id not in cart:
        cart[str_product_id] = 0
    cart[str_product_id] += 1
    session['cart'] = cart
    return redirect("/cart")

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if 'user_id' not in session:
        return redirect("/logout")
    cart = session.get('cart', {})
    products = []
    subtotal = 0
    if len(cart) == 0:
        shipping = 0
    else:
        shipping = 6.57 # adjust this value as needed - but also change it in order_model line 38
    tax_rate = 0.0875 # adjust this value as needed - but also change it in order_model line 41
    for product_id in cart:
        product = product_model.Product.get_one(product_id)
        product.quantity = cart[product_id]
        product.total = product.price * product.quantity
        products.append(product)
        subtotal += product.total
    tax = round(float(subtotal) * tax_rate, 2)
    total = round(float(subtotal) + shipping + tax, 2)
    cart = session.get('cart', {})
    num_cart = sum(cart.values())
    return render_template('cart.html', products=products, subtotal=subtotal, shipping=shipping, tax=tax, total=total, num_cart = num_cart)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        return redirect("/logout")
    cart = session.get('cart', {})
    products = []
    subtotal = 0
    if len(cart) == 0:
        shipping = 0
    else:
        shipping = 6.57 # adjust this value as needed
    tax_rate = 0.0875 # adjust this value as needed
    for product_id in cart:
        product = product_model.Product.get_one(product_id)
        product.quantity = cart[product_id]
        product.total = product.price * product.quantity
        products.append(product)
        subtotal += product.total
    tax = round(float(subtotal) * tax_rate, 2)
    total = round(float(subtotal) + shipping + tax, 2)
    cart = session.get('cart', {})
    num_cart = sum(cart.values())
    return render_template('checkout.html', products=products, subtotal=subtotal, shipping=shipping, tax=tax, total=total, num_cart = num_cart)

@app.route('/remove_from_cart/<int:product_id>', methods=['GET', 'POST'])
def remove_from_cart(product_id):
    if 'user_id' not in session:
        return redirect("/logout")
    str_product_id = str(product_id)
    cart = session.get('cart', {})
    if str_product_id in cart:
        del cart[str_product_id]
    if len(cart) == 0: # Check if cart is empty
        del session['cart'] # Remove the 'cart' object from session
    else:
        session['cart'] = cart # Assign the updated cart object back to session
    return redirect('/cart')

@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    if 'user_id' not in session:
        return redirect("/logout")
    cart = session.get('cart', {})
    quantity = int(request.form['quantity'])
    cart[str(product_id)] = quantity
    session['cart'] = cart
    return redirect('/cart')

@app.route('/orders/create', methods=['POST'])
def create_order():
    if 'user_id' not in session:
        return redirect('/logout')
    if not order_model.Order.validate_order(request.form):
        return redirect('/checkout')
    cart = session.get('cart', {})
    num_cart = sum(cart.values())
    new_order = order_model.Order.save(**request.form, user_id = session['user_id'])
    order = order_model.Order.get_with_details(new_order['id'])
    return render_template('order_complete.html', num_cart = num_cart, order = order)