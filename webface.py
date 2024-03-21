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
import datetime
from sqlitewrap import SQLite
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlite3 import IntegrityError
import os


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
    with SQLite('data.sqlite') as cur:
        response = cur.execute('SELECT login, password FROM user WHERE login = ?',[jmeno])
        response = response.fetchone()
        if response:
            login, pass_hash = response
            if check_password_hash(pass_hash, heslo):
                session["user"] = jmeno
                flash("Jsi přihlášen!", "success")
                if url:
                    return redirect(url)
                else:
                    return redirect(url_for("root"))
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

@app.route("/register", methods =["get"])
def register():
    return render_template("register.html")

@app.route("/register", methods =["post"])
def register_post():
    jmeno = request.form.get('jmeno','')
    heslo1 = request.form.get('heslo1','')
    heslo2 = request.form.get('heslo2','')
    if heslo1 != heslo2:
        flash("hesla se neshodují", "error")
        return redirect(url_for("register"))
    pass_hash = generate_password_hash(heslo1)
    try:
        with SQLite('data.sqlite') as cur:
            cur.execute('INSERT INTO user (login, password) VALUES (?, ?) ', [jmeno, pass_hash])
        flash(f'uživatel {jmeno} byl přidán', 'success')
    except IntegrityError:
        flash(f"uživatel {jmeno} již existuje", "error")
    return redirect(url_for("register"))

@app.route("/vzkazy/", methods=["GET"])
def vzkazy():
    if "user" not in session:
        flash("pro vstup se musíš přihlásit")
        return redirect(url_for("login", url=request.path))
    
    with SQLite('data.sqlite') as cur:
        response = cur.execute('SELECT login, body, datetime, message.id FROM user JOIN message ON user.id = message.user_id ORDER BY datetime DESC').fetchall()

    return render_template("vzkazy.html", response=response, d=datetime.datetime)

@app.route("/vzkazy/", methods=["POST"])
def vzkazy_post():
    if "user" not in session:
        flash("pro vstup se musíš přihlásit")
        return redirect(url_for("login", url=request.path))
    
    with SQLite('data.sqlite') as cur:
        user_id = list(cur.execute('SELECT id FROM user WHERE login = ?', [session['user']]).fetchone())[0]

    vzkaz = request.form.get('vzkaz')
    if vzkaz:
        with SQLite('data.sqlite') as cur:
            cur.execute(
                'INSERT INTO message (user_id, body, datetime) VALUES (?,?,?)', [user_id, vzkaz, datetime.datetime.now()],
            )

    return redirect(url_for("vzkazy"))

@app.route('/vzkaz/vymazat', methods=['POST'])
def vymaz_vzkaz():
    if request.form.get('id'):
        with SQLite('data.sqlite') as cur:
            cur.execute('DELETE FROM message where id = ? and user_id = ?', [request.form.get('id'), cur.execute('SELECT id FROM user WHERE login = ?', [session['user']]).fetchone()[0]])
    return redirect(url_for('vzkazy'))

@app.route('/editovat/<int:_id>')
@prihlasit
def editovat(_id):
    with SQLite('data.sqlite') as cur:
        body = cur.execute('select body from message where id = ?', [_id]).fetchone()[0]
    return render_template('editovat.html', body=body)

@app.route('/editovat/<int:_id>', methods=['POST'])
@prihlasit
def editovat_post(_id):
    if request.form.get('vzkaz'):
        with SQLite('data.sqlite') as cur:
            cur.execute('update message set body = ? where id = ? and user_id = (SELECT id FROM user WHERE login = ?)', [request.form.get('vzkaz') , _id, session['user']])
    return redirect(url_for('vzkazy'))

@app.route('/upload', methods=['GET'])
def upload():
    print(__file__)
    return render_template('upload.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

uploadfolder = os.path.dirname(__file__)+'/upload'
allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

@app.route('/upload', methods=['POST'])
def upload_post():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(uploadfolder, filename))
        flash('upload succesfull')
        return redirect(url_for('upload'))