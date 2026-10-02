import os
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["SECRET_KEY"] = "beykent-ybs-cok-gizli-guvenlik-anahtari-2026"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ybs_club.db"

# Yüklenen etkinlik görselleri için güvenli klasör yolu
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Proje dizininde uploads klasörü yoksa otomatik olarak oluşturur
full_upload_path = os.path.join(app.root_path, UPLOAD_FOLDER)
os.makedirs(full_upload_path, exist_ok=True)

db = SQLAlchemy(app)

# Yönetici Paneli Güvenli Şifresi (Aa160422)
ADMIN_PASSWORD_HASH = generate_password_hash("Aa160422")


# Etkinlik Veritabanı Modeli
class Event(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(150), nullable=False)
  description = db.Column(db.Text, nullable=False)
  date = db.Column(db.String(50), nullable=False)
  location = db.Column(db.String(100), nullable=False)
  rsvp_link = db.Column(db.String(250))
  image_filename = db.Column(db.String(250))


# Sosyal Medya / Hızlı Linkler Veritabanı Modeli
class Link(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), nullable=False)
  url = db.Column(db.String(250), nullable=False)
  icon = db.Column(db.String(50), default="fa-solid fa-link")


# İletişim Mesajları Veritabanı Modeli (Bize Ulaşın)
class ContactMessage(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  email = db.Column(db.String(120), nullable=False)
  message = db.Column(db.Text, nullable=False)
  date = db.Column(db.DateTime, default=db.func.current_timestamp())


# Ana Sayfa Rotaları
@app.route("/")
def index():
  events = Event.query.order_by(Event.id.desc()).all()
  links = Link.query.order_by(Link.id.desc()).all()
  return render_template("index.html", events=events, links=links)


# Bize Ulaşın Formu Gönderim Rotası
@app.route("/contact", methods=["POST"])
def contact():
  name = request.form.get("name")
  email = request.form.get("email")
  message = request.form.get("message")

  if name and email and message:
    new_msg = ContactMessage(name=name, email=email, message=message)
    db.session.add(new_msg)
    db.session.commit()
    flash(
        "Mesajınız başarıyla gönderildi! En kısa sürede dönüş yapacağız.",
        "success",
    )
  else:
    flash("Lütfen tüm alanları doldurun.", "error")

  return redirect(url_for("index") + "#contact")


# Yönetici Paneli Giriş ve Paneli
@app.route("/admin", methods=["GET", "POST"])
def admin():
  if not session.get("logged_in"):
    if request.method == "POST":
      entered_password = request.form.get("password")
      if check_password_hash(ADMIN_PASSWORD_HASH, entered_password):
        session["logged_in"] = True
        return redirect(url_for("admin"))
      flash("Geçersiz şifre!", "error")
    return render_template("login.html")

  events = Event.query.order_by(Event.id.desc()).all()
  links = Link.query.order_by(Link.id.desc()).all()
  messages = ContactMessage.query.order_by(ContactMessage.id.desc()).all()
  return render_template(
      "admin.html", events=events, links=links, messages=messages
  )


# Yeni Etkinlik Ekleme
@app.route("/admin/add_event", methods=["POST"])
def add_event():
  if not session.get("logged_in"):
    return redirect(url_for("admin"))

  title = request.form.get("title")
  description = request.form.get("description")
  date = request.form.get("date")
  location = request.form.get("location")
  rsvp_link = request.form.get("rsvp_link")

  image_filename = None
  if "image" in request.files:
    file = request.files["image"]
    if file and file.filename != "":
      filename = secure_filename(file.filename)
      file.save(os.path.join(full_upload_path, filename))
      image_filename = filename

  if title and description and date and location:
    new_event = Event(
        title=title,
        description=description,
        date=date,
        location=location,
        rsvp_link=rsvp_link,
        image_filename=image_filename,
    )
    db.session.add(new_event)
    db.session.commit()
  return redirect(url_for("admin"))


# Etkinlik Silme
@app.route("/admin/delete_event/<int:id>", methods=["POST"])
def delete_event(id):
  if not session.get("logged_in"):
    return redirect(url_for("admin"))
  event = Event.query.get_or_404(id)
  db.session.delete(event)
  db.session.commit()
  return redirect(url_for("admin"))


# Sosyal Medya / Hızlı Link Ekleme
@app.route("/admin/add_link", methods=["POST"])
def add_link():
  if not session.get("logged_in"):
    return redirect(url_for("admin"))
  title = request.form.get("title")
  url = request.form.get("url")
  icon = request.form.get("icon") or "fa-solid fa-link"
  if title and url:
    db.session.add(Link(title=title, url=url, icon=icon))
    db.session.commit()
  return redirect(url_for("admin"))


# Sosyal Medya / Hızlı Link Silme
@app.route("/admin/delete_link/<int:id>", methods=["POST"])
def delete_link(id):
  if not session.get("logged_in"):
    return redirect(url_for("admin"))
  link = Link.query.get_or_404(id)
  db.session.delete(link)
  db.session.commit()
  return redirect(url_for("admin"))


# İletişim Mesajı Silme
@app.route("/admin/delete_message/<int:id>", methods=["POST"])
def delete_message(id):
  if not session.get("logged_in"):
    return redirect(url_for("admin"))
  msg = ContactMessage.query.get_or_404(id)
  db.session.delete(msg)
  db.session.commit()
  return redirect(url_for("admin"))


# Çıkış Yapma
@app.route("/logout")
def logout():
  session.clear()
  return redirect(url_for("index"))


if __name__ == "__main__":
  with app.app_context():
    db.create_all()
  app.run(debug=True)