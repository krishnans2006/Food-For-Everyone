from flask import Flask, request, session, render_template, redirect, url_for, flash, get_flashed_messages
from datetime import timedelta
import sqlite3
import requests
import json
import copy
import jsonify

class Product:
    def __init__(self, upc, brand, title, description, size, weight, image_link, quantity, expiry):
        self.upc = upc
        self.brand = brand
        self.title = title
        self.description = description
        self.size = size
        self.weight = weight
        self.image_link = image_link
        self.quantity = quantity
        self.expiry = expiry

    def return_params():
        return self.upc, self.brand, self.title, self.description, self.size, self.weight, self.image_link, self.quantity, self.expiry


headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

app = Flask(__name__)
app.config["SECRET_KEY"] = "sa"


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    
def get_data(upc):
    resp = requests.get(
        "https://api.upcitemdb.com/prod/trial/lookup?upc=" + upc, headers=headers)
    data = json.loads(resp.text)
    item = list(data.values())[3][0]
    return json.dumps(item)


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=20)
    session.modified = True

# Needs 2 buttons - Sign Up and Log In


@app.route("/")
def index():
    return render_template("index.html", user=session.get("name"))


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
    return render_template("signup.html", user=session.get("name"))


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
    return render_template("signup_donor.html", user=session.get("name"))


@app.route("/choose_address/", methods=["GET", "POST"])
def choose_address():
    if not session.get("role"):
        return redirect(url_for("index"))
    if request.method == "POST":
        session["name"] = request.form["fname"] + " " + request.form["lname"]
        session["address"] = request.form["addr1"] + ", " + request.form["addr2"] + (", " if len(
            request.form["addr2"]) > 0 else "") + request.form["city"] + ", " + request.form["state"] + " " + request.form["zip_code"]
        session["email"] = request.form["email"]
        session["pwd"] = request.form["pwd"]
        session["logged_in"] = True
        conn = create_connection("project.db")
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * from accounts WHERE email == '{session['email']}'")
        rows = cursor.fetchall()
        if len(rows) > 0:
            flash(
                "0An account has already been created with this email. Please choose another email to use.")
        cursor.execute(
            f"""INSERT INTO accounts(name,address,email,password,role)
            VALUES('{session["name"]}','{session["address"]}','{session["email"]}','{session["pwd"]}','{session["role"]}')""")
        conn.commit()
        return redirect(url_for(session["role"]))
    return render_template("choose_address.html", user=session.get("name"))


@app.route("/login/", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for(session["role"]))
    if request.method == "POST":
        email, pwd = request.form["email"], request.form["pwd"]
        if not(email and pwd):
            flash("0Please enter a username and password")
        conn = create_connection("project.db")
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM accounts WHERE email == '{email}' AND password == '{pwd}'")
        rows = cursor.fetchall()
        if conn:
            conn.close()
        if len(rows) > 0:
            session["logged_in"], session["name"], session["address"], session[
                "email"], session["pwd"], session["role"] = True, *rows[0][1:6]
            flash(f"1Successfully logged in as {session['name']}!")
            return redirect(url_for(session["role"]))
        else:
            flash("0Incorrect username or password!")
            return redirect(url_for("login"))
    return render_template("login.html", user=session.get("name"))


@app.route("/logout/")
def logout():
    try:
        session["logged_in"] = False
        del session["name"], session["address"], session[
            "email"], session["pwd"], session["role"], session["products"]
    except Exception as e:
        print(str(e))
    return redirect(url_for("index"))


@app.route("/supermarket/")
def supermarket():
    if not session.get("role"):
        return redirect(url_for("index"))
    return render_template("supermarket.html", user=session.get("name"))


@app.route("/individual_donor/")
def individual_donor():
    if not session.get("role"):
        return redirect(url_for("index"))
    conn = create_connection("project.db")
    cursor = conn.cursor()
    city = session['address'].split(", ")[1]
    cursor.execute(
        f"SELECT * FROM accounts WHERE role == 'food_bank'")
    rows = cursor.fetchall()
    same_city = []
    for row in rows:
        if row[2].split(",")[1] == session["address"].split(",")[1]:
            same_city.append(row)
    if conn:
        conn.close()
    return render_template("individual_donor.html", user=session.get("name"), rows=same_city)


@app.route("/food_bank/")
def food_bank():
    if not session.get("role"):
        return redirect(url_for("index"))
    conn = create_connection("project.db")
    cursor = conn.cursor()
    city = session['address'].split(", ")[1]
    cursor.execute(
        f"SELECT * FROM accounts WHERE role == 'supermarket'")
    rows = cursor.fetchall()
    same_city = []
    for row in rows:
        if row[2].split(",")[1] == session["address"].split(",")[1]:
            same_city.append(row)
    if conn:
        conn.close()
    return render_template("food_bank.html", user=session.get("name"), rows=same_city)


@app.route("/recipient/")
def recipient():
    if not session.get("role"):
        return redirect(url_for("index"))
    conn = create_connection("project.db")
    cursor = conn.cursor()
    city = session['address'].split(", ")[1]
    cursor.execute(
        f"SELECT * FROM accounts WHERE role == 'food_bank'")
    rows = cursor.fetchall()
    same_city = []
    for row in rows:
        if row[2].split(",")[1] == session["address"].split(",")[1]:
            same_city.append(row)
    if conn:
        conn.close()
    return render_template("recipient.html", user=session.get("name"), rows=same_city)


@app.route("/add_batch")
@app.route("/add_batch", methods=["GET", "POST"])
def add_batch():
    if not session.get("products"):
        session["products"] = []
    if request.method == "POST":
        date_available = request.form["pickup"]
        try:
            conn = create_connection("project.db")
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM accounts WHERE email == '{session['email']}'")
            my_id = cursor.fetchone()[0]
            upcs = []
            brands = []
            titles = []
            descriptions = []
            sizes = []
            weights = []
            image_links = []
            quantities = []
            expiries = []
            for a_product in session.get("products"):
                product = json.loads(a_product)
                upcs.append(product["upc"].replace(",", "."))
                brands.append(product["brand"].replace(",", "."))
                titles.append(product["title"].replace(",", "."))
                descriptions.append(product["description"].replace(",", "."))
                sizes.append(product["size"].replace(",", "."))
                weights.append(product["weight"].replace(",", "."))
                get_imgs = product["images"].replace(",", "<")
                if get_imgs:
                    image_links.append(get_imgs[0])
                else:
                    image_links.append("No Image")
                quantities.append(product.get("quantity"))
                expiries.append(product.get("expiry"))
            execute = f"""INSERT INTO batches(product_upc,product_brand,product_title,product_description,product_size,product_weight,product_image_link,product_quantity,product_expiry,owner,date_available)
            VALUES ('{", ".join(upcs)}',
                '{", ".join(brands)}',
                '{", ".join(titles)}',
                '{", ".join(descriptions)}',
                '{", ".join(sizes)}',
                '{", ".join(weights)}',
                '{", ".join(image_links)}',
                '{", ".join(quantities)}',
                '{", ".join(expiries)}',
                {my_id},
                {date_available})"""
            print("Executing: \n" + execute)
            cursor.execute(execute)
            conn.commit()
        except Exception as e:
            print("Error: " + str(e))
    return render_template("add_batch.html", user=session.get("name"), products=session.get("products"), loads=json.loads)


@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        upc = request.form["upc"]
        quantity = request.form["quantity"]
        expiry = request.form["expiry"]
        try:
            data = get_data(upc)
            new_data = json.loads(data)
            new_data["quantity"] = quantity
            new_data["expiry"] = expiry
            data = json.dumps(new_data)
            if not session.get("products"):
                session["products"] = []
            session["products"].append(data)
            print(json.loads(session["products"][0])["description"])
        except Exception as e:
            flash("0" + "Error gathering barcode data! " + str(e))
            print(e)
            return redirect(url_for("add_product"))
        return redirect(url_for("add_batch"))
    return render_template("add_product.html", user=session.get("name"))

if __name__ == "__main__":
    app.run(debug=True)
