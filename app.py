import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
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

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == '160422':
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('Hatalı şifre!', 'danger')
    return render_template('admin_login.html')

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Çıkış yapıldı.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    events = Event.query.all()
    links = Link.query.all()
    return render_template('admin.html', events=events, links=links)

@app.route('/admin/add_event', methods=['POST'])
def add_event():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

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
    return redirect(url_for('admin'))

@app.route('/admin/edit_event/<int:id>', methods=['GET', 'POST'])
def edit_event(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    event = Event.query.get_or_404(id)
    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        event.date = request.form.get('date')
        event.location = request.form.get('location')
        event.rsvp_link = request.form.get('rsvp_link')
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                event.image_filename = filename

        db.session.commit()
        flash('Etkinlik başarıyla güncellendi!', 'success')
        return redirect(url_for('admin'))
    
    return render_template('edit_event.html', event=event)

@app.route('/admin/delete_event/<int:id>', methods=['POST'])
def delete_event(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    event = Event.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    flash('Etkinlik silindi!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/add_link', methods=['POST'])
def add_link():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    title = request.form.get('link_title') or request.form.get('title')
    url = request.form.get('link_url') or request.form.get('url')
    icon = request.form.get('link_icon') or request.form.get('icon')
    
    new_link = Link(title=title, url=url, icon=icon)
    db.session.add(new_link)
    db.session.commit()
    flash('Bağlantı başarıyla eklendi!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/delete_link/<int:id>', methods=['POST'])
def delete_link(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    link = Link.query.get_or_404(id)
    db.session.delete(link)
    db.session.commit()
    flash('Bağlantı silindi!', 'success')
    return redirect(url_for('admin'))

@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    
    new_msg = ContactMessage(name=name, email=email, message=message)
    db.session.add(new_msg)
    db.session.commit()
    flash('Mesajınız başarıyla gönderildi!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)