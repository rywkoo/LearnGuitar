from app import app, session, flash, redirect, url_for, request, render_template
import sqlite3
import os
from werkzeug.utils import secure_filename

# ===== CONFIG =====
UPLOAD_FOLDER = 'static/assets/images/products'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ===== Helper Functions =====
def get_db_connection():
    conn = sqlite3.connect('su79_database.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ===== Protect admin routes =====
@app.before_request
def protect_admin_routes():
    protected_paths = ['/admin', '/admin/products']
    if any(request.path.startswith(p) for p in protected_paths) and not session.get('user_id'):
        flash('You must log in first', 'warning')
        return redirect(url_for('login'))
    return None

# ===== Login / Logout =====
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('admin_dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('admin/login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

# ===== Admin Dashboard =====
@app.route('/admin')
def admin_dashboard():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template('admin/index.html', products=[dict(p) for p in products])

# ===== Product List =====
@app.route('/admin/products')
def admin_products():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template('admin/product.html', products=[dict(p) for p in products])

# ===== Add Product =====
@app.route('/admin/add-product', methods=['GET', 'POST'])
def add_product():
    conn = get_db_connection()
    categories = [row['category'] for row in conn.execute("SELECT DISTINCT category FROM products").fetchall()]
    conn.close()

    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = request.form['price']

        # Handle image input
        image_url = request.form.get('image_url', '').strip()
        image_file = request.files.get('image_file')

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image_file.save(save_path)
            image_path = f'/static/assets/images/products/{filename}'
        elif image_url:
            image_path = image_url
        else:
            image_path = ''  # Optional default image

        # Insert product
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO products (name, category, price, image) VALUES (?, ?, ?, ?)',
            (name, category, price, image_path)
        )
        conn.commit()
        conn.close()

        flash('Product added successfully', 'success')
        return redirect(url_for('add_product'))

    return render_template('admin/addproduct.html', categories=categories)

# ===== Edit Product =====
@app.route('/admin/products/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id=?", (id,)).fetchone()
    categories = [row['category'] for row in conn.execute("SELECT DISTINCT category FROM products").fetchall()]
    conn.close()

    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('admin_products'))

    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = request.form['price']

        # Handle image update
        image_url = request.form.get('image_url', '').strip()
        image_file = request.files.get('image_file')

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image_file.save(save_path)
            image_path = f'/static/assets/images/products/{filename}'
        elif image_url:
            image_path = image_url
        else:
            image_path = product['image']  # keep existing

        conn = get_db_connection()
        conn.execute(
            "UPDATE products SET name=?, category=?, price=?, image=? WHERE id=?",
            (name, category, price, image_path, id)
        )
        conn.commit()
        conn.close()
        flash('Product updated successfully', 'success')
        return redirect(url_for('admin_products'))

    return render_template('admin/edit_product.html', product=product, categories=categories)

# ===== Delete Product =====
@app.route('/admin/products/delete/<int:id>', methods=['POST'])
def delete_product(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM products WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash('Product deleted successfully', 'success')
    return redirect(url_for('admin_products'))
