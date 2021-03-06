import hashlib
import os
import sqlite3
import pandas as pd
from flask import Flask, jsonify, render_template, request, redirect, make_response, session
from blockchain import Blockchain
from user import db, User

mg_coin = Blockchain()

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():
    global cookie_hash
    login_df = pd.DataFrame(sqlite3.connect("db.sqlite").cursor().execute("SELECT * FROM 'user_table'").fetchone()).T

    try:
        cookie_hash = hashlib.sha3_512()
        cookie_hash.update(request.cookies.get('password').encode('utf-8'))
    except:
        pass

    if request.method == 'GET' and 'username' not in session and 'password' not in session:
        return render_template("index.html")

    elif request.method == 'GET' and 'username' in session and 'password' in session:
        if True in (login_df[3] == cookie_hash.hexdigest()) & (login_df[2] == request.cookies.get('username')):
            return render_template("logined_index.html")
        else:
            return render_template("index.html")

    elif request.method == 'POST':
        userid = request.form.get('userid')
        password = request.form.get('password')

        hash = hashlib.sha3_512()
        hash.update(password.encode('utf-8'))

        if 'username' in session and 'password' in session:
            if True in login_df[(login_df[3] == cookie_hash.hexdigest()) & (login_df[2] == request.cookies.get('username'))]:
                print("Login success")
                resp = make_response(render_template("logined_index.html"))
                resp.set_cookie('username', str(userid))
                resp.set_cookie('password', str(password))
                return resp

            print("Login failed")
            return render_template("login_falied_index.html")


@app.route('/mine', methods=['GET'])
def mine():
    return "We'll mine a new Block"


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    return "We'll add a new transaction"


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': mg_coin.chain,
        'length': len(mg_coin.chain),
    }
    return jsonify(response), 200


@app.route('/register', methods=['GET', 'POST'])  # GET(????????????), POST(????????????) ????????? ??????
def register():
    if request.method == 'GET':
        return render_template("register/register.html")
    else:
        userid = request.form.get('userid')
        email = request.form.get('email')
        password = request.form.get('password')
        password_2 = request.form.get('password')

        if not (userid and email and password and password_2):
            return "???????????? ?????? ????????? ????????????"
        elif password != password_2:
            return "??????????????? ???????????? ????????????"
        else:
            hash = hashlib.sha3_512()
            hash.update(password.encode('utf-8'))

            usertable = User(hash.hexdigest())
            usertable.userid = userid
            usertable.email = email
            usertable.password = hash.hexdigest()

            id_df = sqlite3.connect("db.sqlite").cursor().execute(
                "SELECT * FROM 'user_table' WHERE userid == userid").fetchone()
            if not id_df:
                db.session.add(usertable)
                db.session.commit()
                return render_template("register/register_done.html")
            else:
                return render_template("register/already_register.html")


if __name__ == "__main__":
    # ??????????????????---------
    basedir = os.path.abspath(os.path.dirname(__file__))  # ?????? ????????? ?????? ???????????? ?????? ??????
    dbfile = os.path.join(basedir, 'db.sqlite')  # ?????????????????? ????????? ?????????

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True  # ??????????????? ?????? ?????????????????? teadown. ??? ????????? ??????=DB??????
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # ?????? ???????????? ??????????????? ?????????

    db.init_app(app)  # app????????? ?????????
    db.app = app  # Models.py?????? db??? ???????????? db.app??? app??? ??????????????? ?????????
    db.create_all()  # DB??????

    app.run(host='0.0.0.0', port=8000, debug=False)
