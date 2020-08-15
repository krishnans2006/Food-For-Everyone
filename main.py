from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

# Needs 2 buttons - Sign Up and Log In
@app.route("/")
def index():
    return render_template("index.html")


# @app.route("/signup")
# def sign_up():
#     return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)