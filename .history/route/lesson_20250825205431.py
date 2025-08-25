from flask import render_template
from app import app


@app.route("/lesson")
def lesson():
    return render_template("lesson.html", products=[])
