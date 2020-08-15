from flask import Flask, request, session, render_template, redirect, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = "mysecretkey"

# Needs 2 buttons - Sign Up and Log In
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        choice = request.form["role"]
        if choice == "Donor":
            return redirect(url_for("signup_donor"))
        elif choice == "Food Bank":
            session["role"] = "Food Bank"
            print(session["role"])
            return redirect(url_for("choose_address"))
        elif choice == "Recipient":
            session["role"] = "Recipient"
            print(session["role"])
            return redirect(url_for("choose_address"))
    return render_template("signup.html")
@app.route("/signup_donor", methods=["GET", "POST"]) 
def signup_donor():
    if request.method == "POST":
        choice = request.form["role"]
        if choice == "Supermarket":
            session["role"] = "Supermarket"
            print(session["role"])
            return redirect(url_for("choose_address"))
        elif choice == "Individual Donor":
            session["role"] = "Individual Donor"
            print(session["role"])
            return redirect(url_for("choose_address"))
    return render_template("signup_donor.html")
@app.route("/choose_address")
def choose_address():
    return render_template("choose_address.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        pwd = request.form["pwd"]
        session["login"], session["email"], session["pwd"] = True, email, pwd
        if email == "hello@123.com" and pwd == "PWD":
            return redirect(url_for("supermarket"))
        else:
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/supermarket") 
def supermarket():
    return render_template("supermarket.html")
@app.route("/individual_donor") 
def individual_donor():
    return render_template("individual_donor.html")
@app.route("/food_bank") 
def food_bank():
    return render_template("food_bank.html")
@app.route("/recipient") 
def recipient():
    return render_template("recipient.html")

if __name__ == "__main__":
    app.run(debug=False)