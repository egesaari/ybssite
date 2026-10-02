import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'beykent_ybs_gizli_anahtar'

# Dosya yükleme klasörü ayarı (Görseller için)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

# Tabloları oluştur
with app.app_context():
    db.create_all()

# --- ROTALAR ---
@app.route('/')
def index():
    events = Event.query.all()
    links = Link.query.all()
    return render_template('index.html', events=events, links=links)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # Etkinlik Ekleme Formu Kontrolü
        if 'add_event' in request.form:
            title = request.form.get('title')
            description = request.form.get('description')
            date = request.form.get('date')
            location = request.form.get('location')
            rsvp_link = request.form.get('rsvp_link')
            
            image_filename = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    image_filename = filename

            new_event = Event(
                title=title,
                description=description,
                date=date,
                location=location,
                rsvp_link=rsvp_link,
                image_filename=image_filename
            )
            db.session.add(new_event)
            db.session.commit()
            flash('Etkinlik başarıyla eklendi!', 'success')

        # Sosyal Medya / Hızlı Bağlantı Ekleme
        elif 'add_link' in request.form:
            title = request.form.get('link_title')
            url = request.form.get('link_url')
            icon = request.form.get('link_icon')
            
            new_link = Link(title=title, url=url, icon=icon)
            db.session.add(new_link)
            db.session.commit()
            flash('Bağlantı başarıyla eklendi!', 'success')

        return redirect(url_for('admin'))

    events = Event.query.all()
    links = Link.query.all()
    return render_template('admin.html', events=events, links=links)

if __name__ == '__main__':
    app.run(debug=True)