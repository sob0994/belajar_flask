from pydoc import doc
from app import app, db
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from firebase_admin import firestore
import pandas as pd
from app.helpers import useFileImport

# Login Reuired


def uselogin(f):
    @wraps(f)
    def wrap(*ar, **ars):
        if 'user' in session:
            return f(*ar, **ars)
        else:
            return redirect(url_for('login'))
    return wrap

# Login already


def nologin_req(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" in session:
            return redirect(url_for("home"))
        else:
            return f(*args, **kwargs)
    return wrapper


@app.route("/")
@app.route("/home")
@uselogin
def home():
    return render_template("base.html", title="Selamat Datang")


@app.route("/test")
def test():
    return render_template("test.html")


@app.route("/login", methods=["GET", "POST"])
@nologin_req
def login():
    if session.get("register"):
        session.pop("register")
    # jika methodnya POST
    if request.method == "POST":
        # Inisiasi dataLogin from request
        dataLogin = {
            "username": request.form["username"],
            "password": request.form["password"],
        }
        # Check ke Database
        users = (db.collection("users").where("username", "==",
                                              dataLogin["username"]).stream())
        user = {}
        # Masukkan data users ke user
        for usr in users:
            user = usr.to_dict()
        # Jika user datanya ada maka
        if user:
            if user["password"] == dataLogin["password"]:
                session["user"] = user
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


@app.route("/register", methods=["GET", "POST"])
@nologin_req
def register():
    if request.method == "POST":
        dataRegister = {
            "username": request.form.get("username", ""),
            "namaLengkap": request.form["namaLengkap"] or "",
            "email": request.form["email"] or "",
            "password": request.form["password"] or "",
            "access": "guest",
        }
        # save data to session
        session["register"] = dataRegister
        # chek username exist
        users = (db.collection("users").where(
            "username", "==", dataRegister["username"]).stream())
        user = {}
        for usr in users:
            user = usr.to_dict()

        if user:
            dataRegister["errors"] = {"username": "Username sudah terpakai"}
            flash("Username sudah terpakai", "error")
            return render_template("page/register.html")
            # return redirect(url_for('register'))

        # chek email exist
        users = (db.collection("users").where("email", "==",
                                              dataRegister["email"]).stream())
        user = {}
        for usr in users:
            user = usr.to_dict()

        if user:
            dataRegister["errors"] = {"email": "Email sudah terpakai"}
            flash("Email sudah terpakai", "error")
            return render_template("page/register.html")

        # Save to database
        db.collection("users").document().set(dataRegister)
        flash("Registrasi berhasil", "ok")
        session.pop("register")
        return redirect(url_for("login"))

    return render_template("page/register.html")


@app.route("/nasabah", methods=["GET", "POST"])
@uselogin
def nasabah():
    provs = db.collection('provinsi').order_by(
        "nama", direction=firestore.Query.ASCENDING).stream()
    prov = []
    for i in provs:
        a = i.to_dict()
        a['id'] = i.id
        prov.append(a)
    kota = []
    for i in prov:
        kota[i['nama']] = i['kabupaten']

    return render_template("page/nasabah.html", provinsi=prov, kota=kota)


@app.route("/data/provinsi", methods=["GET", "POST", "PUT", "DELETE"])
def dataProvinsi():
    mth = request.method
    if mth == 'PUT':
        return 'PUT'

    if mth == 'POST':
        importData = request.args.get('import')

        # Code for Import Data
        if importData == 'true':
            # Get file from request File
            myFile = request.files.get('filePath')
            # if File doesn't Exist
            if not myFile:
                return jsonify({"error": "File diperlukan"})
            # if File Exist convert to Json/Object
            myFileData = useFileImport(
                myFile, ['xls', 'xlsx', 'xlsb', 'csv', 'json'], {'id': str})['data']

            # if File Error
            if 'error' in myFileData:
                return jsonify(myFileData)
            # cek if File is OK to import

            fileOk = False
            for i in myFileData:
                if {'id', 'nama'} <= set(i):
                    fileOk = True
            # Check File OK
            if fileOk == False:
                return jsonify({"error": "Maaf File format tidak sesuai"})

            # Insert into Database Firestore
            batch = db.batch()
            # Bath max 500 document
            for i in myFileData:
                docID = i['id']
                dbRef = db.collection('provinsi').document(docID)
                batch.set(dbRef, {"id": docID, "nama": i['nama']}, merge=True)

            batch.commit()

            return jsonify({'ok': myFileData})

        # Code for Form Input Data
        else:
            # Inpur Form Maual
            return jsonify({'status': 'insert new'})

    if mth == 'DELETE':
        return 'DELETE'

    data = (db.collection("provinsi").order_by(
        "nama", direction=firestore.Query.ASCENDING).stream())
    prov = []
    for pr in data:
        p = pr.to_dict()
        p["id"] = pr.id
        prov.append(p)

    return render_template("page/provinsi.html", provinsi=prov, method=mth)


@app.route("/data/provinsi/<uid>")
@uselogin
def showProvinsi(uid):
    ps = db.collection('provinsi').document(uid)
    provs = ps.get().to_dict()
    # kotas = db.collection('kota').where(
    #     'kodeProv', '==', provs['Kode']).stream()
    kota = []
    # for i in kotas:
    #     kota.append(i.to_dict())

    # jumlahKota = len(kota)
    # ps.update({'jumlahKota': jumlahKota})

    if provs:
        return render_template('page/provinsi_show.html', provs=provs, kota=kota)

    return redirect(url_for('dataProvinsi'))


@app.route('/importdata/kota', methods=['POST'])
@uselogin
def importKota():
    if request.method == 'POST':
        # Request File
        flName = request.files.get('fileExcel')
        fileSupport = ['xls', 'xlsx', 'xlsb', 'csv', 'json']
        flType = flName.filename.split('.')[-1]
        # Check File Type
        if not flType in fileSupport:
            return jsonify({'msg': 'File tidak didukung'})

        dataImport = []
        # If file Excel
        if flType[0:2] == 'xl':
            dataExcel = pd.read_excel(
                flName, index_col=0, dtype={'Kode': str}).to_dict(orient='records')
            for i in dataExcel:
                dataImport.append(i)
        # if file Json
        if flType[0:2] == 'js':
            dataJson = pd.read_json(
                flName, dtype={'Kode': str}).to_dict(orient='index')
            for i in dataJson:
                dataImport.append(dataJson[i])
        # if file Csv
        if flType[0:2] == 'cs':
            dataCsv = pd.read_csv(
                flName, dtype={'Kode': str}).to_dict(orient='index')
            for i in dataCsv:
                dataImport.append(dataCsv[i])
        # Initial Data Status
        status = {
            'sukses': [],
            'KodeProv': [],
            'KodeProvErr': [],
            'data': [],
            'dataOk': [],
            'dataErr': [],
            'dataEx': [],
            'prov': [],
        }
        # Serialize Struktur Data
        for i in dataImport:
            # Jika berisi Kolom (Kode, Nama, Kab) maka Sesuai
            if 'Kode' and 'Nama' and 'Kab' in i:
                myData = {
                    'Kode': i['Kode'],
                    'Nama': i['Nama'],
                    'Kab': i['Kab'],
                    'kodeProv': i['Kode'][0:2]
                }

                status["data"].append(myData)
                if i['Kode'][0:2] not in status["KodeProvErr"]:
                    status["KodeProvErr"].append(i['Kode'][0:2])

            else:
                # File tidak sesuai
                return jsonify({'msg': 'File tidak sesuai format'})

        # Cek Provinsi Terdaftar
        dbProv = db.collection('prov')
        for i in status["KodeProvErr"]:
            kode = dbProv.where('Kode', '==', i).stream()
            for a in kode:
                # print(i)
                status["KodeProv"].append(i)
                status["prov"].append(
                    {'Kode': i, 'id': a.id, 'Kota': []})
        print(status["KodeProv"])
        # Pisahkan Data Error
        for d in status["data"]:
            if d['Kode'][0:2] in status["KodeProv"]:
                status["dataOk"].append(d)
            else:
                status['dataErr'].append(d)
        # Simpan ke Database Kota
        dbatch = db.batch()
        dbKota = db.collection('kota')
        for i in status["dataOk"]:
            its = dbKota.where('Kode', '==', i['Kode']).stream()
            oks = {}
            for it in its:
                oks = it.to_dict()
            if oks == {}:
                # dbKota.document().set(i)
                dko = dbKota.document()
                dbatch.set(dko, i)
            dbatch.commit()
        return jsonify({'msg': 'File Sesuai Format', 'data': status})


@app.route('/data/kota', methods=['POST', 'GET'])
@uselogin
def ambilKota():
    mth = request.method
    if mth == 'POST':
        importData = request.args.get("import")
        # Import Data Logic
        if importData == 'true':
            # get file from request file
            myFile = request.files.get("filePath")

            # if file not exist
            if not myFile:
                return jsonify({'error': 'File diperlukan'})

            # if file exist conver to Object/Json
            myFileData = useFileImport(
                myFile, ['xls', 'xlsx', 'xlsb', 'csv', 'json'], {'id': str, 'id_provinsi': str})
            # if File Error
            if 'error' in myFileData:
                return jsonify(myFileData)
            # cek if File is OK to import
            fileOk = True
            for i in myFileData['data']:
                if {'id_provinsi', 'id', 'nama'} <= set(i):
                    fileOk = True

            # if file is OK
            if fileOk == False:
                return jsonify({'error': 'File format salah!'})

            # insert Data into Database
            batch = db.batch()
            # Firebase Batch maximum 500 writes per Request
            setWrites = 200
            pembagianBulat = len(myFileData['data'])//setWrites
            cn = 1
            dataSplit = []
            nStart = 0
            nFinish = setWrites
            # Split into many request
            while(cn <= pembagianBulat + 1):
                dataSplit.append(myFileData['data'][nStart:nFinish])
                cn = cn + 1
                nStart = nStart + setWrites
                nFinish = nFinish + setWrites
            # Insert Splited data into database
            for i in dataSplit:
                for a in i:
                    myRef = db.collection('kota').document(a['id'])
                    batch.set(myRef, {'id': a['id'], 'id_provinsi':
                                      a['id_provinsi'], 'nama': a['nama']}, merge=True)

                    provRef = db.collection(
                        'provinsi').document(a['id_provinsi'])
                    batch.update(provRef, {'kabupaten': firestore.ArrayUnion(
                        [{'id': a['id'], 'nama': a['nama']}])})

                batch.commit()

            return jsonify(dataSplit)

        # Input Form Data Logic
        else:
            return jsonify("Input Data Required " + importData)

    return jsonify("Detail Kota ditampilkan")


@app.route('/data/kota/<idKota>', methods=['POST', 'GET'])
@uselogin
def detailKota(idKota):
    return jsonify(idKota)
