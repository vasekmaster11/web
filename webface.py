from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    Markup,
    escape,
    flash,
)
import functools
import random

# from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = b"totoj e zceLa n@@@hodny retezec nejlep os.urandom(24)"
app.secret_key = b"x6\x87j@\xd3\x88\x0e8\xe8pM\x13\r\xafa\x8b\xdbp\x8a\x1f\xd41\xb8"


def prihlasit(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        if "user" in session:
            return function(*args, **kwargs)
        else:
            return redirect(url_for("login", url=request.path))

    return wrapper


@app.route("/", methods=["GET"])
def root():
    a = 3
    b = 8
    # a = 1 + '1'
    return render_template("base.html")

@app.route("/pes/")
def abc():
    return render_template("pes.html")

@app.route("/kocka/", methods=["GET"])
def spenat():
    if "user" not in session:
        flash("pro vstup se musíš přihlásit")
        return redirect(url_for("login", url=request.path))
    return render_template("kocka.html")

@app.route("/kocka/", methods=["POST"])
def spenat_post():
    pokus = request.form.get('pokus','')
    print(pokus)
    return redirect(url_for("kocka"))

@app.route("/login/", methods=["GET"])
def login():
    if "user" not in session:
        return render_template("login.html")
    return render_template("logout.html")

@app.route("/login/", methods=["POST"])
def login_post():
    jmeno = request.form.get('jmeno','')
    heslo = request.form.get('heslo','')
    url = request.args.get('url','')
    if jmeno == "fixa" and heslo == "0":
        session["user"] = jmeno
        flash("Jsi přihlášen!", "success")
        if url:
            return redirect(url)
        else:
            return redirect(url_for("root"))    
    else:
        flash("Nesprávné přihlašovací údaje","error")
    return redirect(url_for("login", url = url))

@app.route("/logout/")
def logout():
    session.pop("user", None)
    flash("byl jsi odhlášen!", "success")
    return redirect(url_for("root"))

@app.route("/secret")
def secret():
    if 1==1:
        flash("nemáš oprávnění", "error")
        return redirect(url_for("root"))
    else:
        return render_template('secret.html')
