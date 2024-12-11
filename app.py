from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


# Product catalog
products = [
    {'id': 1, 'name': 'Cozy Blanket', 'price': 29.99, 'description': 'A soft and warm blanket perfect for chilly evenings.', 'image': 'https://m.media-amazon.com/images/I/71wPZW8kDUL.jpg'},
    {'id': 2, 'name': 'Scented Candle', 'price': 14.99, 'description': 'Relaxing vanilla-scented candle for a soothing ambiance.', 'image': 'https://candlefy.com/cdn/shop/products/tahitian-vanilla-scented-candle-made-with-natural-coconut-wax-583708.jpg?v=1710035999&width=1214'},
    {'id': 3, 'name': 'Yoga Mat', 'price': 39.99, 'description': 'Non-slip yoga mat for your fitness and mindfulness practices.', 'image': 'https://target.scene7.com/is/image/Target/GUEST_d972c756-ef1b-4ed7-bdf5-1b86ef5fc625?wid=488&hei=488&fmt=pjpeg'},
    {'id': 4, 'name': 'Artisanal Coffee Mug', 'price': 19.99, 'description': 'Handcrafted ceramic mug for your favorite brew.', 'image': 'https://lh5.googleusercontent.com/proxy/k_5X7Fw8YoqCuN2pRKyfo_Kg0WZl16Kva0GiTNgE1hK729zF_v9_pKyCk5ArIKoChuv13SrOr-RzZXxUc-5djhkR3vWjO5g9CG5UCSix_eSYRoUVOtGt2egm'},
    {'id': 5, 'name': 'Plant Pot', 'price': 24.99, 'description': 'Minimalist plant pot for your indoor greenery.', 'image': 'https://m.media-amazon.com/images/I/71VClE6rcYL.jpg'},
    {'id': 6, 'name': 'Board Game', 'price': 49.99, 'description': 'A fun strategy game for friends and family game nights.', 'image': 'https://m.media-amazon.com/images/I/81ymbGmdHiL.jpg'},
    {'id': 7, 'name': 'Desk Organizer', 'price': 18.99, 'description': 'Keep your desk neat and tidy with this multifunctional organizer.', 'image': 'https://i5.walmartimages.com/seo/Desk-Organizer-Large-Shelf-Multi-Compartments-Units-Wood-Desktop-Storage-Board-Organizer-White_da102804-8935-487e-b58b-5c1a43807813.24f8a53895e412179b2dbe7b24f6c980.png'},
    {'id': 8, 'name': 'Noise-Cancelling Earplugs', 'price': 9.99, 'description': 'Focus better with these comfortable noise-cancelling earplugs.', 'image': 'https://m.media-amazon.com/images/I/61ZHYKulDkL.jpg'},
    {'id': 9, 'name': 'Reusable Water Bottle', 'price': 12.99, 'description': 'Stay hydrated with this eco-friendly reusable water bottle.', 'image': 'https://m.media-amazon.com/images/I/61YuhJHMlXL.jpg'},
]



# Simulated user database
users = {
    "testuser": {"name": "Test User", "password": "password123"}
}

@app.route('/')
def index():
    return render_template('index.html', products=products)

@app.context_processor
def inject_user():
    return {'user': session.get('user')}

@app.route('/checkout_success')
def checkout_success():
    return render_template('checkout_success.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists
        user = users.get(username)
        if not user:
            # If the user does not exist, flash an error message
            flash('That account does not exist, please register for a new account.', 'danger')
            return redirect(url_for('login'))

        # Validate password
        if user['password'] == password:
            session['user'] = {'username': username, 'name': user['name']}
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Incorrect password. Please try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if username already exists
        if username in users:
            flash('That username is already taken. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('register'))

        # Add new user to the users dictionary
        users[username] = {"name": username.capitalize(), "password": password}
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/product/<int:product_id>')
def product_details(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('index'))
    return render_template('product_details.html', product=product)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []

    # Find the product
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('index'))

    # Check if product already exists in the cart
    for item in session['cart']:
        if item['id'] == product_id:
            item['quantity'] += 1  # Increment quantity
            session.modified = True
            flash(f'{product["name"]} quantity increased.', 'success')
            return redirect(url_for('cart'))

    # Add product with quantity 1
    session['cart'].append({'id': product['id'], 'name': product['name'], 'price': product['price'], 'quantity': 1})
    session.modified = True
    flash(f'{product["name"]} added to cart.', 'success')
    return redirect(url_for('cart'))


@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session:
        for item in session['cart']:
            item.setdefault('quantity', 1)  # Fallback for missing quantity
            if item['id'] == product_id:
                if item['quantity'] > 1:
                    item['quantity'] -= 1
                else:
                    session['cart'].remove(item)
                session.modified = True
                flash(f'{item["name"]} removed from cart.', 'success')
                break
    return redirect(url_for('cart'))


@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    # Ensure all items have a default quantity of 1
    for item in cart:
        item.setdefault('quantity', 1)
    total = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('cart.html', cart=cart, total=total)



@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)

    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            flash(f'Order confirmed! A confirmation email will be sent to {email}.', 'success')
            # Clear the cart after checkout
            session.pop('cart', None)
            session.modified = True
            return redirect(url_for('checkout_success'))  # Ensure this points to the correct route

    return render_template('checkout.html', cart=cart, total=total)

if __name__ == '__main__':
    app.run(debug=True)

