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


@app.route('/register', methods=['GET', 'POST'])  # GET(정보보기), POST(정보수정) 메서드 허용
def register():
    if request.method == 'GET':
        return render_template("register/register.html")
    else:
        userid = request.form.get('userid')
        email = request.form.get('email')
        password = request.form.get('password')
        password_2 = request.form.get('password')

        if not (userid and email and password and password_2):
            return "입력되지 않은 정보가 있습니다"
        elif password != password_2:
            return "비밀번호가 일치하지 않습니다"
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
    # 데이터베이스---------
    basedir = os.path.abspath(os.path.dirname(__file__))  # 현재 파일이 있는 디렉토리 절대 경로
    dbfile = os.path.join(basedir, 'db.sqlite')  # 데이터베이스 파일을 만든다

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True  # 사용자에게 정보 전달완료하면 teadown. 그 때마다 커밋=DB반영
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 추가 메모리를 사용하므로 꺼둔다

    db.init_app(app)  # app설정값 초기화
    db.app = app  # Models.py에서 db를 가져와서 db.app에 app을 명시적으로 넣는다
    db.create_all()  # DB생성

    app.run(host='0.0.0.0', port=8000, debug=False)
