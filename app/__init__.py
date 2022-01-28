from flask import Flask
import firebase_admin
from firebase_admin import credentials, firestore

# cred = credentials.Certificate("firebase-cert.json")
firebase_admin.initialize_app(
    credential=credentials.Certificate("app/firebase-cert.json"))

db = firestore.client()

app = Flask(__name__)
app.secret_key = "bro"
