from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mail import Mail, Message
import json
import requests
from datetime import date
from dotenv import load_dotenv
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = "741e4fa4-f067-4aec-b48d-deb18e9cca92"

import route

@app.route("/components")
def components():
    return render_template("component.html")

if __name__ == "__main__":
    app.run(debug=True)
