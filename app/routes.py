import csv
import json
from app import app, db
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from firebase_admin import firestore
import pandas as pd

with open("app/Data/Prov.json") as jsonFile:
    dataJson = json.load(jsonFile)
    jsonFile.close

# with open("app/Data/Prov.csv") as csvFile:
#     dataCsv = csv.reader(csvFile)
#     csvFile.close


# Login Reuired
def login_req(f):

    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' in session:
            return f(*args, *kwargs)
        else:
            return redirect(url_for("login"))

    return wrapper


#Login already
def nologin_req(f):

    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' in session:
            return redirect(url_for("home"))
        else:
            return f(*args, **kwargs)

    return wrapper


@app.route("/")
@app.route("/home")
@login_req
def home():
    return render_template("base.html", title="Selamat Datang")


@app.route("/test")
def test():
    return render_template("test.html")


@app.route("/login", methods=['GET', 'POST'])
@nologin_req
def login():
    if session.get('register'): session.pop('register')
    # jika methodnya POST
    if request.method == 'POST':
        # Inisiasi dataLogin from request
        dataLogin = {
            'username': request.form['username'],
            'password': request.form['password'],
        }
        # Check ke Database
        users = db.collection('users').where('username', '==',
                                             dataLogin['username']).stream()
        user = {}
        # Masukkan data users ke user
        for usr in users:
            user = usr.to_dict()
        # Jika user datanya ada maka
        if user:
            if user['password'] == dataLogin['password']:
                session['user'] = user
                return redirect(url_for("home"))
            else:
                flash("Login Gagal", "error")
                return redirect(url_for("login"))
        # Jika user datanya tidak ada
        else:
            flash("Login Salah, silahkan dicek kembali!", "error")
            return redirect(url_for("login"))
    # jika methodnya GET
    return render_template("page/login.html")


@app.route("/out")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/register", methods=['GET', 'POST'])
@nologin_req
def register():
    if request.method == 'POST':
        dataRegister = {
            'username': request.form.get('username', ""),
            'namaLengkap': request.form['namaLengkap'] or "",
            'email': request.form['email'] or "",
            'password': request.form['password'] or "",
            'access': 'guest'
        }
        # save data to session
        session['register'] = dataRegister
        # chek username exist
        users = db.collection('users').where(
            'username', '==', dataRegister['username']).stream()
        user = {}
        for usr in users:
            user = usr.to_dict()

        if user:
            dataRegister['errors'] = {'username': 'Username sudah terpakai'}
            flash("Username sudah terpakai", "error")
            return render_template("page/register.html")
            # return redirect(url_for('register'))

        # chek email exist
        users = db.collection('users').where('email', '==',
                                             dataRegister['email']).stream()
        user = {}
        for usr in users:
            user = usr.to_dict()

        if user:
            dataRegister['errors'] = {'email': 'Email sudah terpakai'}
            flash("Email sudah terpakai", "error")
            return render_template("page/register.html")

        # Save to database
        db.collection('users').document().set(dataRegister)
        flash("Registrasi berhasil", "ok")
        session.pop("register")
        return redirect(url_for('login'))

    return render_template("page/register.html")


@app.route("/nasabah", methods=['GET', 'POST'])
@login_req
def nasabah():
    return render_template("page/nasabah.html")


@app.route("/data/provinsi", methods=['GET', 'POST'])
def dataProvinsi():
    data = db.collection("prov").order_by(
        'Provinsi', direction=firestore.Query.ASCENDING).stream()
    prov = []
    for pr in data:
        p = pr.to_dict()
        p['id'] = pr.id
        prov.append(p)

    return render_template("page/provinsi.html", provinsi=prov)


@app.route("/nsb")
def imp():

    # for itm in dataJson:
    # db.collection("prov").document().set(itm)
    # db.collection("Provinsi").document(u"00000Coba").update({
    #     u'color.red':
    #     u'Merah',
    #     u'color.gelap.hitam':
    #     u'warna hitam',
    # })

    # print(dataCsv)

    return jsonify(dataJson)
