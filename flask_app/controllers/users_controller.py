from flask_app import app
from flask import render_template,redirect,request,session,flash
from flask_app.models import user_model, order_model, product_model

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template("index.html")

@app.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('signup.html')

@app.route('/user/signup', methods=['POST'])
def signup():
    errors = user_model.User.validate_user(request.form)
    if errors:
        for field, error in errors.items():
            flash(error, field)
        return redirect('/signup')
    user_id = user_model.User.save(**request.form)
    session.clear()
    session['user_id'] = user_id
    return redirect("/dashboard")

@app.route('/user/login', methods=['POST'])
def login():
    user = user_model.User.validate_login(request.form)
    if not user:
        return redirect('/login')
    session['user_id'] = user.id
    return redirect('/dashboard')

@app.route('/user/account')
def account():
    if 'user_id' not in session:
        return redirect('/logout')
    user = user_model.User.get_one(session['user_id'])
    cart = session.get('cart', {})
    num_cart = sum(cart.values())
    orders = order_model.Order.get_all_with_details_for_user(user.id)
    return render_template('account.html', user=user, orders=orders, num_cart = num_cart)

@app.route('/user/update/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    if 'user_id' not in session:
        return redirect("/logout")
    errors = user_model.User.validate_update(request.form)
    if errors:
        for field, error in errors.items():
            flash(error, field)
        return redirect('/user/account')
    data = {
        'id': user_id,
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'password': request.form['password'],
        }
    user_model.User.edit_user(**data)
    return redirect("/user/account")

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/logout')
    user = user_model.User.get_one(session['user_id'])
    cart = session.get('cart', {})
    num_cart = sum(cart.values())
    return render_template("dashboard.html", num_cart = num_cart, user = user)

@app.route('/shop/<string:category_name>')
def shop(category_name):
    if 'user_id' not in session:
        return redirect("/logout")
    user = user_model.User.get_one(session['user_id'])
    cart = session.get('cart', {})
    num_cart = sum(cart.values())
    products = product_model.Product.get_products_by_category(category_name)
    return render_template("shop.html", num_cart=num_cart, user=user, category_name=category_name, products=products)

@app.route('/shop/product/<int:product_id>')
def view_product(product_id):
    if 'user_id' not in session:
        return redirect("/logout")
    product = product_model.Product.get_one(product_id)
    return render_template("product.html", product = product)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')