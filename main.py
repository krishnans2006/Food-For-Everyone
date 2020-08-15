from flask import Flask, request, session, render_template, redirect, url_for
from datetime import timedelta
import sqlite3

app = Flask(__name__)
app.config["SECRET_KEY"] = "saranggoel"


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=20)
    session.modified = True

# Needs 2 buttons - Sign Up and Log In
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup/", methods=["GET", "POST"])
def signup():
    if session.get("logged_in"):
        return redirect(url_for(session["role"]))
    if request.method == "POST":
        choice = request.form["role"]
        if choice == "Donor":
            return redirect(url_for("signup_donor"))
        elif choice == "Food Bank":
            session["role"] = "food_bank"
            return redirect(url_for("choose_address"))
        elif choice == "Recipient":
            session["role"] = "recipient"
            return redirect(url_for("choose_address"))
    return render_template("signup.html")
@app.route("/signup_donor/", methods=["GET", "POST"]) 
def signup_donor():
    if request.method == "POST":
        choice = request.form["role"]
        if choice == "Supermarket":
            session["role"] = "supermarket"
            return redirect(url_for("choose_address"))
        elif choice == "Individual Donor":
            session["role"] = "individual_donor"
            return redirect(url_for("choose_address"))
    return render_template("signup_donor.html")
@app.route("/choose_address/", methods=["GET", "POST"])
def choose_address():
    if not session.get("role"):
        return redirect(url_for("index"))
    if request.method == "POST":
        session["name"] = request.form["fname"] + " " + request.form["lname"]
        session["address"] = request.form["addr1"] + ", " + request.form["addr2"] + (", " if len(request.form["addr2"]) > 0 else "") + request.form["city"] + ", " + request.form["state"] + " " + request.form["zip_code"]
        session["email"] = request.form["email"]
        session["pwd"] = request.form["pwd"]
        session["logged_in"] = True
        print(session["address"], session["name"])
        return redirect(url_for(session["role"]))
    return render_template("choose_address.html")

@app.route("/login/", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for(session["role"]))
    if request.method == "POST":
        email, pwd = request.form["email"], request.form["pwd"]
        conn = create_connection("project.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM accounts WHERE email == '{email}' AND password == '{pwd}'")
        rows = cursor.fetchall()
        if conn:
            conn.close()
        if len(rows) > 0:
            session["logged_in"], session["name"], session["address"], session[
                "email"], session["pwd"], session["role"] = True, *rows[0][1:6]
            print(session["address"], session["name"], "Login")
            return redirect(url_for(session["role"]))
        else:
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/supermarket/") 
def supermarket():
    if not session.get("role"):
        return redirect(url_for("index"))
    return render_template("supermarket.html")
@app.route("/individual_donor/") 
def individual_donor():
    if not session.get("role"):
        return redirect(url_for("index"))
    return render_template("individual_donor.html")
@app.route("/food_bank/") 
def food_bank():
    if not session.get("role"):
        return redirect(url_for("index"))
    return render_template("food_bank.html")
@app.route("/recipient/") 
def recipient():
    if not session.get("role"):
        return redirect(url_for("index"))
    return render_template("recipient.html")

@app.route("/add_batch")
def add_batch():
    return render_template("add_batch.html")
@app.route("/add_product")
def add_product():
    return render_template("add_product.html")

if __name__ == "__main__":
    app.run(debug=False)
