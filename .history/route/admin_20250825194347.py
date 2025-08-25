from app import app, session, flash, redirect, url_for, request, render_template
import sqlite3

# --- Helper function ---                                                                                                                                                                                                                                                                           
def get_db_connection():
    conn = sqlite3.connect('su79_database.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn


# --- Protect admin routes ---
@app.before_request
def protect_admin_routes():
    protected_paths = ['/admin', '/admin/products']
    if any(request.path.startswith(p) for p in protected_paths) and not session.get('user_id'):
        flash('You must log in first', 'warning')
        return redirect(url_for('login'))
    return None


# --- Login / Logout ---
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


# --- Admin dashboard ---
@app.route('/admin')
def admin_dashboard():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template('admin/index.html', products=[dict(p) for p in products])


# --- CRUD for products ---
@app.route('/admin/products')
def admin_products():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template('admin/product.html', products=[dict(p) for p in products])


@app.route('/admin/products/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = request.form['price']
        image = request.form['image']

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO products (name, category, price, image) VALUES (?, ?, ?, ?)",
            (name, category, price, image)
        )
        conn.commit()
        conn.close()
        flash('Product added successfully', 'success')
        return redirect(url_for('admin_products'))

    return render_template('admin/addproduct.html')


@app.route('/admin/products/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id=?", (id,)).fetchone()
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('admin_products'))

    if request.method == 'POST':
        conn.execute(
            "UPDATE products SET name=?, category=?, price=?, image=? WHERE id=?",
            (request.form['name'], request.form['category'], request.form['price'], request.form['image'], id)
        )
        conn.commit()
        conn.close()
        flash('Product updated successfully', 'success')
        return redirect(url_for('admin_products'))

    conn.close()
    return render_template('admin/edit_product.html', product=product)


@app.route('/admin/products/delete/<int:id>', methods=['POST'])
def delete_product(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM products WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash('Product deleted successfully', 'success')
    return redirect(url_for('admin_products'))
