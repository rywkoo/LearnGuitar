from app import app
from flask import request, render_template, jsonify
from flask_mail import Mail, Message
import sqlite3
import traceback
import requests
import json
from datetime import date, datetime

# ======== CONFIGURE EMAIL =========
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'theareachmiku@gmail.com'
app.config['MAIL_PASSWORD'] = 'otppdcjyhanngoks'  # Avoid committing this to version control
app.config['MAIL_DEFAULT_SENDER'] = 'theareachmiku@gmail.com'

mail = Mail(app)

# ======== TELEGRAM CONFIG =========
TELEGRAM_BOT_TOKEN = '7884087901:AAGrPE8dJauRXZMZdw7mPktJsAnhSWQWIgs'
TELEGRAM_CHAT_ID = '-1002632266756'

# ======== CHECKOUT ROUTE =========
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No JSON data received'}), 400

            name = data.get('name', '')
            phone = data.get('phone', '')
            email = data.get('email', '')
            address = data.get('address', '')
            cart_list = data.get('cart', [])

            if not cart_list:
                return jsonify({'success': False, 'error': 'Cart is empty'}), 400

            # Calculate total
            total = sum(item.get('quantity', item.get('qty', 1)) * item.get('price', 0) for item in cart_list)

            # ======== INSERT INTO SQLITE =========
            conn = sqlite3.connect('su79_database.sqlite3')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO invoice (name, phone, email, address, total, items_json, date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                phone,
                email,
                address,
                total,
                json.dumps(cart_list),
                datetime.now().isoformat(),
                'checked_out'
            ))
            conn.commit()
            conn.close()

            # ======== RENDER EMAIL =========
            invoice_html = render_template('checkoutEmail.html',
                                           name=name,
                                           phone=phone,
                                           email=email,
                                           address=address,
                                           cart=cart_list,
                                           total=total)

            msg = Message(subject='🧾 Your Order Invoice',
                          recipients=[email],
                          html=invoice_html)
            mail.send(msg)

            # ======== TELEGRAM =========
            message_lines = [
                f"<strong>🧾 Invoice #{date.today().strftime('%Y%m%d')}</strong>",
                f"<code>👤 {name}</code>",
                f"<code>📧 {email}</code>",
                f"<code>📆 {date.today()}</code>",
                f"<code>🏠 {address}</code>",
                "<code>=======================</code>",
            ]
            for i, item in enumerate(cart_list, start=1):
                qty = item.get('quantity', item.get('qty', 1))
                subtotal = qty * item.get('price', 0)
                message_lines.append(f"<code>{i}. {item['title']} x{qty} = ${subtotal:.2f}</code>")
            message_lines.append("<code>=======================</code>")
            message_lines.append(f"<code>💵 Total: ${total:.2f}</code>")

            telegram_message = "\n".join(message_lines)

            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                data={"chat_id": TELEGRAM_CHAT_ID, "text": telegram_message, "parse_mode": "HTML"}
            )

            return jsonify({'success': True})

        except Exception as e:
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500

    # GET request: render the checkout page
    return render_template('checkOut.html')
