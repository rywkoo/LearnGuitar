from flask import render_template
from app import app


@app.route("/")
@app.route("/home")
def home():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template("home.html", products=products)
