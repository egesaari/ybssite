import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'gizli_anahtar_buraya'  # Kendi secret key'ini buraya yazabilirsin

# --- VERİTABANI BAĞLANTI AYARI ---
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///ybs_club.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- TABLOLAR (MODELLER) ---
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    rsvp_link = db.Column(db.String(250), nullable=True)
    image_filename = db.Column(db.String(250), nullable=True)

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(250), nullable=False)
    icon = db.Column(db.String(50), nullable=True)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())

# Uygulama ayağa kalkarken tabloları otomatik oluşturur
with app.app_context():
    db.create_all()

# --- ROTALAR ---
@app.route('/')
def index():
    events = Event.query.all()
    links = Link.query.all()
    return render_template('index.html', events=events, links=links)

# İhtiyacına göre diğer route (sayfa) fonksiyonların buradadır.
# Kendi projendeki diğer route'ları (admin girişi, etkinlik ekleme vb.) buraya ekleyebilirsin.

if __name__ == '__main__':
    app.run(debug=True)